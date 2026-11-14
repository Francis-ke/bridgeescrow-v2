"""Serialize balance writes and keep retry keys private to each wallet."""
import hashlib
from sqlalchemy import select, text
from app.core.db import db
from app.core.errors import ApiError
from app.models import Wallet, LedgerEntry


def lock(wallet):
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    return db.session.execute(select(Wallet).where(Wallet.id == wallet.id)
        .with_for_update().execution_options(populate_existing=True)).scalar_one()


def scoped_key(wallet, kind, key):
    if key is None:
        return None
    digest = hashlib.sha256(str(key).encode()).hexdigest()
    return f'w{wallet.id}-{kind}-{digest}'[:80]


def replayed(wallet, kind, cents, key):
    if key is None:
        return False
    scoped = scoped_key(wallet, kind, key)
    row = LedgerEntry.query.filter_by(wallet_id=wallet.id, idempotency_key=scoped).first()
    # Preserve retries of transactions recorded before wallet-scoped keys.
    if row is None:
        row = LedgerEntry.query.filter_by(wallet_id=wallet.id, idempotency_key=key).first()
    if row is None:
        return False
    if row.entry_type != kind or row.amount_cents != cents:
        raise ApiError('This retry key was used for a different transaction', 409, 'idempotency_conflict')
    return True
