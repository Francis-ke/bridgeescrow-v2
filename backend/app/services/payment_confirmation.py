from sqlalchemy import select, text
from app.core.db import db
from app.core.errors import ApiError
from app.models import Payment, Wallet, LedgerEntry
from . import wallet_service
from .ledger import credit


def confirm(payment_id, receipt=None, credit_wallet=True, commit=True):
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    pay = db.session.execute(select(Payment).where(Payment.id == payment_id)
        .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
    if not pay:
        raise ApiError('Payment not found', 404, 'not_found')
    if pay.status == 'confirmed':
        return pay
    if pay.status != 'pending':
        raise ApiError(f'Payment is {pay.status}', 409, 'invalid_state')
    if pay.checkout_order_id:
        from .developer.live_checkout import fund
        fund(pay)
    elif credit_wallet and pay.provider != 'daraja_sandbox':
        wallet = db.session.execute(select(Wallet).where(Wallet.id == pay.wallet_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one()
        key = 'pay-' + pay.reference
        if not LedgerEntry.query.filter_by(idempotency_key=key).first():
            credit(wallet, int(pay.amount_cents), 'deposit', 'M-PESA payment received', key=key)
    import secrets
    pay.status, pay.receipt = 'confirmed', receipt or ('Q' + secrets.token_hex(5).upper())
    db.session.commit() if commit else db.session.flush()
    return pay
