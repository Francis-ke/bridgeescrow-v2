from app.core.db import db
from app.core.errors import ApiError
from app.models import Wallet, LedgerEntry
from app.models.mixins import MoneyMixin
from app.services.ledger import credit, debit
from app.services.wallet_lookup import wallet_by_id

MAX_DEPOSIT_CENTS = 500_000_000


def fmt(cents: int) -> str:
    return MoneyMixin.from_cents(int(cents or 0))


def wallet_for(user_id: int) -> Wallet:
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, available_cents=0)
        db.session.add(wallet)
        db.session.flush()
    return wallet


def wallet_for_user(wallet_id: int) -> Wallet:
    return wallet_by_id(wallet_id)


def credit_external(wallet: Wallet, cents: int, key: str | None) -> Wallet:
    """Credit a wallet from a confirmed external payment (M-Pesa)."""
    if _replayed(key):
        return wallet
    credit(wallet, cents, "deposit", "M-Pesa payment received", key=key)
    db.session.commit()
    return wallet


def _replayed(key):
    if not key:
        return None
    return LedgerEntry.query.filter_by(idempotency_key=key).first()


def deposit(user_id: int, amount, key: str | None) -> Wallet:
    wallet = wallet_for(user_id)
    if _replayed(key):
        return wallet
    cents = MoneyMixin.to_cents(amount)
    if cents > MAX_DEPOSIT_CENTS:
        raise ApiError("Deposit exceeds the per-transaction limit")
    credit(wallet, cents, "deposit", "Wallet top-up", key=key)
    db.session.commit()
    return wallet


def withdraw(user_id: int, amount, pin_ok: bool, key: str | None) -> Wallet:
    wallet = wallet_for(user_id)
    if _replayed(key):
        return wallet
    if not pin_ok:
        raise ApiError("A valid transaction PIN is required", 403, "pin_required")
    debit(wallet, MoneyMixin.to_cents(amount), "withdrawal", "Wallet withdrawal",
          key=key)
    db.session.commit()
    return wallet


def history(user_id: int, limit: int = 50) -> list[dict]:
    wallet = wallet_for(user_id)
    rows = (LedgerEntry.query.filter_by(wallet_id=wallet.id)
            .order_by(LedgerEntry.id.desc()).limit(limit).all())
    return [r.to_dict() for r in rows]
