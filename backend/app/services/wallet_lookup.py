from app.core.db import db
from app.models import Wallet


def wallet_by_id(wallet_id: int) -> Wallet:
    wallet = db.session.get(Wallet, wallet_id)
    if not wallet:
        raise LookupError(f"Wallet {wallet_id} not found")
    return wallet
