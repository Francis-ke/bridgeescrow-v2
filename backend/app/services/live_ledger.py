"""Prevent test money from becoming withdrawable when switching provider modes."""
from sqlalchemy import func
from app.core.db import db
from app.core.errors import ApiError
from app.models import User, Wallet, LedgerEntry, Payment
from app.models.payout import Payout


def verify_clean():
    normal = db.session.query(Wallet.id).join(User).filter(User.role != 'system')
    deposits = db.session.query(LedgerEntry.id).filter(LedgerEntry.wallet_id.in_(normal),
        LedgerEntry.entry_type == 'deposit', LedgerEntry.direction == 'credit')
    backed = db.session.query(Payment.id).filter(Payment.wallet_id == LedgerEntry.wallet_id,
        LedgerEntry.idempotency_key == 'pay-' + Payment.reference,
        Payment.provider == 'daraja_live', Payment.status == 'confirmed').exists()
    if deposits.filter(~backed).first():
        raise ApiError('This database contains simulated deposits. Use a separate clean production database before enabling live money.',
                       503, 'live_database_required')
    balance = db.session.query(func.coalesce(func.sum(Wallet.available_cents + Wallet.escrow_cents), 0)).filter(Wallet.id.in_(normal)).scalar()
    real = db.session.query(func.coalesce(func.sum(Payment.amount_cents), 0)).filter(
        Payment.provider == 'daraja_live', Payment.status == 'confirmed', Payment.wallet_id.in_(normal)).scalar()
    reserved = db.session.query(func.coalesce(func.sum(Payout.amount_cents), 0)).filter(Payout.status != 'failed').scalar()
    if balance > real - reserved:
        raise ApiError('Account balances are not backed by verified live deposits. Reconcile the database before enabling live money.',
                       503, 'live_database_required')


def register_guard(app):
    @app.before_request
    def guard_live_money():
        from flask import request
        if app.config['PAYMENT_MODE'] != 'daraja_live':
            return
        for name in ('SECRET_KEY', 'JWT_SECRET'):
            value = str(app.config.get(name, ''))
            if len(value) < 32 or value.startswith(('dev-', 'replace-')):
                raise ApiError('Set strong production signing secrets before enabling live payments', 503, 'live_secrets_required')
        protected = ('/api/wallet', '/api/payments', '/api/payouts', '/api/ussd',
                     '/api/protected', '/api/escrows', '/api/checkout', '/api/callbacks')
        if request.path.startswith(protected):
            verify_clean()
