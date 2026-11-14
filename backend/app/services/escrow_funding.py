from app.services.protected.common import legacy_guard
from app.core.db import db
from app.core.errors import ApiError
from app.models.escrow import Escrow
from app.services.wallet_service import wallet_for
from app.services.ledger import debit


def load(escrow_id: int) -> Escrow:
    from sqlalchemy import select, text
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    esc = db.session.execute(select(Escrow).where(Escrow.id == escrow_id).with_for_update()
        .execution_options(populate_existing=True)).scalar_one_or_none()
    if not esc:
        raise ApiError("Escrow not found", 404, "not_found")
    return esc


def fund(escrow_id: int, buyer_id: int, commit=True) -> Escrow:
    esc = load(escrow_id)
    legacy_guard(esc)
    if esc.buyer_id != buyer_id:
        raise ApiError("Only the buyer can fund this escrow", 403, "forbidden")
    if esc.status != "hold":
        raise ApiError(f"Escrow is already {esc.status}", 409, "invalid_state")
    wallet = wallet_for(buyer_id)
    from app.services.protected.ledger import lock_wallets
    lock_wallets(wallet)
    debit(wallet, esc.money_cents, "hold", f"Funds held for {esc.reference}",
          key=f"fund-{esc.reference}", escrow=esc)
    wallet.escrow_cents += esc.money_cents
    esc.status = "funded"
    from app.services.notifications import add
    from app.models.mixins import MoneyMixin
    add(esc.seller_id, esc, f"funded-{esc.id}",
        f"{esc.buyer.full_name} sent KES {MoneyMixin.from_cents(esc.money_cents)} to escrow for {esc.title}. View the transaction details.")
    db.session.commit() if commit else db.session.flush()
    return esc
