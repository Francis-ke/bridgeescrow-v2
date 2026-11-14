from flask import Blueprint
from sqlalchemy import func
from app.core.db import db
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.models import Escrow, LedgerEntry, User
from app.services.wallet_service import wallet_for

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
@login_required
def summary():
    uid = current_user_id()
    wallet = wallet_for(uid)
    rows = (db.session.query(Escrow.status, func.count(Escrow.id))
            .filter((Escrow.buyer_id == uid) | (Escrow.seller_id == uid))
            .group_by(Escrow.status).all())
    spent = (db.session.query(func.coalesce(func.sum(LedgerEntry.amount_cents), 0))
             .filter(LedgerEntry.wallet_id == wallet.id,
                     LedgerEntry.entry_type == "release",
                     LedgerEntry.direction == "debit").scalar())
    user = db.session.get(User, uid)
    return {"wallet": wallet.to_dict(), "escrow_counts": dict(rows),
            "total_paid_out_cents": int(spent),
            "account_number": user.account_number, "full_name": user.full_name,
            "role": user.role}
