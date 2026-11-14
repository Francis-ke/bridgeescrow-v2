from app.core.db import db
from app.models.escrow import Escrow
from app.models.ledger import LedgerEntry
from app.core.security import random_token
from app.services.wallet_service import wallet_for


def _move(wallet, esc, kind, direction, cents, desc):
    if cents <= 0:
        return
    db.session.add(LedgerEntry(wallet_id=wallet.id, escrow_id=esc.id,
                               entry_type=kind, direction=direction,
                               amount_cents=cents, description=desc,
                               reference=f"LG{random_token(8).upper()}"))


def _release_hold(buyer, esc: Escrow) -> None:
    buyer.escrow_cents -= esc.money_cents
    _move(buyer, esc, "release", "debit", esc.money_cents,
          f"Escrow {esc.reference} settled")


def pay_seller(esc: Escrow) -> None:
    from app.services.protected.common import legacy_guard
    legacy_guard(esc)
    from app.services.receipt_hold import ensure_releasable
    ensure_releasable(esc)
    buyer, seller = wallet_for(esc.buyer_id), wallet_for(esc.seller_id)
    from app.services.protected.ledger import lock_wallets
    lock_wallets(buyer, seller)
    _release_hold(buyer, esc)
    net = esc.money_cents - esc.fee_money_cents
    seller.available_cents += net
    _move(seller, esc, "release", "credit", net, f"Payment for {esc.reference}")
    esc.status = "released"
    from app.services.notifications import add
    from app.models.mixins import MoneyMixin
    add(esc.seller_id, esc, f"received-{esc.id}",
        f"You received KES {MoneyMixin.from_cents(net)} from {esc.buyer.full_name} for {esc.title}.")
    db.session.flush()


def refund_buyer(esc: Escrow) -> None:
    from app.services.protected.common import legacy_guard
    legacy_guard(esc)
    buyer = wallet_for(esc.buyer_id)
    from app.services.protected.ledger import lock_wallets
    lock_wallets(buyer)
    _release_hold(buyer, esc)
    buyer.available_cents += esc.money_cents
    _move(buyer, esc, "refund", "credit", esc.money_cents,
          f"Refund for {esc.reference}")
    esc.status = "refunded"
    from app.services.notifications import add
    add(esc.buyer_id, esc, f"refunded-{esc.id}",
        f"Your payment for {esc.title} has been refunded to your wallet.")
    db.session.flush()
