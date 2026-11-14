from datetime import timedelta
from marshmallow import Schema, fields, validate
from app.core.db import db
from app.core.errors import ApiError
from app.models.mixins import utcnow
from app.services.notifications import add


class ReceiptHoldSchema(Schema):
    hours = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=720))
    reason = fields.String(required=True, validate=validate.Length(min=10, max=400))


def active(escrow):
    return bool(escrow.receipt_hold_until and escrow.receipt_hold_until > utcnow())


def ensure_releasable(escrow):
    if active(escrow):
        raise ApiError("The recipient's hold has not expired yet", 409, "receipt_hold_active")


def save(escrow, user_id, payload):
    from app.services.protected.common import legacy_guard
    legacy_guard(escrow)
    if escrow.seller_id != user_id:
        raise ApiError("Only the recipient can request a receipt hold", 403, "forbidden")
    if escrow.status != "funded":
        raise ApiError("Only funded escrows can be held", 409, "invalid_state")
    if escrow.hold_request_status == "pending":
        raise ApiError("A hold request is already awaiting the sender's decision", 409, "request_pending")
    data = ReceiptHoldSchema().load(payload)
    reason = data["reason"].strip()
    if len(reason) < 10:
        raise ApiError("Describe the reason in at least 10 characters", 422, "invalid_reason")
    now = utcnow()
    if active(escrow) and now + timedelta(hours=data["hours"]) < escrow.receipt_hold_until:
        raise ApiError("An active hold can only be extended", 409, "hold_cannot_shorten")
    escrow.hold_request_hours = data["hours"]
    escrow.hold_request_reason = reason
    escrow.hold_request_status = "pending"
    escrow.hold_requested_at = now
    escrow.hold_decided_at = None
    add(escrow.buyer_id, escrow, f"hold-request-{escrow.id}-{now.isoformat()}",
        f"{escrow.seller.full_name} requested {data['hours']} hours of hold time for {escrow.title}. Open Sent money to accept or decline.")
    db.session.commit()
    return escrow


def decide(escrow, user_id, decision):
    from app.services.protected.common import legacy_guard
    legacy_guard(escrow)
    if escrow.buyer_id != user_id:
        raise ApiError("Only the sender can decide a hold request", 403, "forbidden")
    if decision not in ("accept", "decline"):
        raise ApiError("Choose accept or decline", 422, "invalid_decision")
    if escrow.status != "funded" or escrow.hold_request_status != "pending":
        raise ApiError("No pending hold request for this funded escrow", 409, "invalid_state")
    now = utcnow()
    if decision == "accept":
        until = now + timedelta(hours=escrow.hold_request_hours)
        if active(escrow) and until < escrow.receipt_hold_until:
            raise ApiError("An active hold can only be extended", 409, "hold_cannot_shorten")
        escrow.receipt_hold_until = until
        escrow.receipt_hold_reason = escrow.hold_request_reason
        escrow.release_code_hash = None
    escrow.hold_request_status = "accepted" if decision == "accept" else "declined"
    escrow.hold_decided_at = now
    add(escrow.seller_id, escrow, f"hold-decision-{escrow.id}-{escrow.hold_requested_at.isoformat()}",
        f"{escrow.buyer.full_name} {escrow.hold_request_status} your hold-time request for {escrow.title}.")
    db.session.commit()
    return escrow
