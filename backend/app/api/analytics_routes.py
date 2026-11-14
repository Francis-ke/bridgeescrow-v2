from flask import Blueprint
from sqlalchemy import func
from app.core.db import db
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.models import Escrow, LedgerEntry
from app.services.wallet_service import wallet_for

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@bp.get("/me")
@login_required
def my_analytics():
    uid = current_user_id()
    wallet = wallet_for(uid)
    by_status = dict(db.session.query(Escrow.status, func.count(Escrow.id))
                     .filter((Escrow.buyer_id == uid) | (Escrow.seller_id == uid))
                     .group_by(Escrow.status).all())
    inflow, outflow = _flows(wallet)
    from app.services.protected.reports import categories
    return {'protected_categories': categories(uid), "by_status": by_status, "inflow_cents": inflow,
            "outflow_cents": outflow, "available_cents": wallet.available_cents,
            "escrow_cents": wallet.escrow_cents,
            "ledger_rows": LedgerEntry.query.filter_by(wallet_id=wallet.id).count()}


def _flows(wallet) -> tuple[int, int]:
    rows = (db.session.query(LedgerEntry.direction,
                             func.coalesce(func.sum(LedgerEntry.amount_cents), 0))
            .filter(LedgerEntry.wallet_id == wallet.id, LedgerEntry.account_bucket == "available")
            .group_by(LedgerEntry.direction).all())
    sums = {d: int(v) for d, v in rows}
    return sums.get("credit", 0), sums.get("debit", 0)
