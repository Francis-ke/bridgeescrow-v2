from datetime import timedelta, timezone

from app.models import Contract, LedgerEntry


def iso(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def transaction_details(escrow):
    from app.services.receipt_hold import active
    funded = LedgerEntry.query.filter_by(
        escrow_id=escrow.id, entry_type="hold", direction="debit"
    ).order_by(LedgerEntry.id).first()
    received = LedgerEntry.query.filter_by(
        escrow_id=escrow.id, entry_type="release", direction="credit"
    ).order_by(LedgerEntry.id).first()
    if escrow.protection and escrow.status != 'released':
        received = None
    contract = Contract.query.filter_by(escrow_id=escrow.id).first()
    expected_delivery = None
    if funded and contract and contract.fully_signed:
        expected_delivery = funded.created_at + timedelta(days=contract.delivery_days)
    receipt = {
        "hold": "Awaiting funding",
        "funded": "Recipient receives funds after the buyer confirms delivery",
        "disputed": "Payment is paused until the dispute is resolved",
        "released": "Funds released to the recipient",
        "refunded": "Refunded to the sender; recipient will not receive funds",
        "cancelled": "Cancelled; recipient will not receive funds",
    }
    if active(escrow) and escrow.status == "funded":
        receipt["funded"] = "Recipient hold is active; buyer confirmation is required after it expires"
    return {
        "hold_request": {"hours": escrow.hold_request_hours,
                         "reason": escrow.hold_request_reason,
                         "status": escrow.hold_request_status,
                         "requested_at": iso(escrow.hold_requested_at),
                         "decided_at": iso(escrow.hold_decided_at)},
        "receipt_hold_until": iso(escrow.receipt_hold_until),
        "receipt_hold_reason": escrow.receipt_hold_reason,
        "receipt_hold_active": active(escrow) and escrow.status == "funded",
        "sender": {"id": escrow.buyer_id, "name": escrow.buyer.full_name, "email": escrow.buyer.email,
                   "card_number": escrow.buyer.card_number},
        "recipient": {"id": escrow.seller_id, "name": escrow.seller.full_name, "email": escrow.seller.email,
                      "card_number": escrow.seller.card_number},
        "payment_method": "wallet", "card_last4": None,
        "transaction_at": iso(escrow.created_at),
        "funded_at": iso(funded.created_at) if funded else None,
        "received_at": iso(received.created_at) if received else None,
        "expected_delivery_at": iso(expected_delivery),
        "receipt_status": receipt.get(escrow.status, "Receipt time is not available"),
    }
