from app.core.db import db
from app.core.errors import ApiError
from app.models import Wallet, LedgerEntry
from app.core.security import random_token


def _entry(wallet, escrow, kind, direction, cents, desc, key):
    row = LedgerEntry(wallet_id=wallet.id, escrow_id=escrow.id if escrow else None,
                      entry_type=kind, direction=direction, amount_cents=cents,
                      reference=f"LG{random_token(8).upper()}", description=desc,
                      idempotency_key=key)
    db.session.add(row)
    return row


def credit(wallet: Wallet, cents: int, kind: str, desc: str, key=None,
           escrow=None) -> None:
    if cents <= 0:
        raise ApiError("Amount must be greater than zero")
    wallet.available_cents += cents
    row = _entry(wallet, escrow, kind, "credit", cents, desc, key)
    if kind == "deposit":
        from app.services.notifications import add
        add(wallet.user_id, None, f"deposit-{row.reference}",
            f"Deposit of KES {cents // 100}.{cents % 100:02d} added to your wallet.")


def debit(wallet: Wallet, cents: int, kind: str, desc: str, key=None,
          escrow=None) -> None:
    if cents <= 0:
        raise ApiError("Amount must be greater than zero")
    if wallet.available_cents < cents:
        raise ApiError("Insufficient funds in your wallet", 409, "insufficient_funds")
    wallet.available_cents -= cents
    _entry(wallet, escrow, kind, "debit", cents, desc, key)
