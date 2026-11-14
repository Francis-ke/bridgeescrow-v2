from flask import Blueprint, g, current_app
from sqlalchemy import func
from app.models import Escrow
from app.core.db import db
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.services import wallet_service

bp = Blueprint("wallet", __name__, url_prefix="/api/wallet")

# The current request's wallet is snapshotted right after any write so the
# response never reflects a stale identity-map copy.
def snapshot(user_id: int, wallet=None) -> dict:
    if wallet is None:
        wallet = wallet_service.wallet_for(user_id)
    from app.services.protected.reports import incoming as incoming_balance
    from app.services.developer.merchant_balances import for_owner
    incoming = incoming_balance(user_id)
    return {"payment_mode": current_app.config["PAYMENT_MODE"], "website_sandbox": for_owner(user_id), "incoming_escrow": wallet_service.fmt(incoming), "available": wallet_service.fmt(wallet.available_cents),
            "escrow": wallet_service.fmt(wallet.escrow_cents),
            "currency": wallet.currency}


@bp.get("")
@login_required
def get_wallet():
    db.session.expire_all()
    return {"wallet": snapshot(current_user_id())}


@bp.get("/ledger")
@login_required
def get_ledger():
    return {"entries": wallet_service.history(current_user_id())}
