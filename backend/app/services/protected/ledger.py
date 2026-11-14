import secrets
from sqlalchemy import select
from app.core.db import db
from app.models import User, Wallet, LedgerEntry
from app.services.wallet_service import wallet_for
from .common import require


def fee_wallet(payment=None):
    if payment and payment.rules.get('sandbox_application_id'):
        from app.services.developer.sandbox import fees
        return fees(payment.rules['sandbox_application_id'])
    user = User.query.filter_by(account_number='BEPLATFORM').first()
    if not user:
        user = User(account_number='BEPLATFORM', full_name='Platform fees',
            email='fees@bridgeescrow.invalid', phone='SYS-FEES', role='system',
            is_active=False, email_verified=False)
        user.set_password(secrets.token_urlsafe(48))
        db.session.add(user)
        db.session.flush()
    return wallet_for(user.id)


def lock_wallets(*wallets):
    ids = sorted(wallet.id for wallet in wallets)
    db.session.execute(select(Wallet).where(Wallet.id.in_(ids)).order_by(Wallet.id)
        .with_for_update().execution_options(populate_existing=True)).scalars().all()


def line(wallet, payment, direction, amount, bucket, kind, batch):
    if amount:
        row = LedgerEntry(wallet_id=wallet.id, escrow_id=payment.escrow_id,
            direction=direction, amount_cents=amount, account_bucket=bucket,
            entry_type=kind, batch_reference=batch, description=f'{payment.category}: {payment.escrow.title}',
            reference='LG' + secrets.token_hex(12).upper())
        db.session.add(row)
        return row


def fund(payment):
    buyer = wallet_for(payment.escrow.buyer_id)
    lock_wallets(buyer)
    amount = payment.escrow.money_cents
    require(buyer.available_cents >= amount, 'Insufficient funds in your wallet')
    buyer.available_cents -= amount
    buyer.escrow_cents += amount
    batch = 'PF-' + secrets.token_hex(10)
    line(buyer, payment, 'debit', amount, 'available', 'hold', batch)
    line(buyer, payment, 'credit', amount, 'escrow', 'hold', batch)


def distribute(payment, amount, refund=0):
    buyer, seller = wallet_for(payment.escrow.buyer_id), wallet_for(payment.escrow.seller_id)
    fees = fee_wallet(payment)
    lock_wallets(buyer, seller, fees)
    require(0 <= refund <= amount <= remaining(payment), 'Invalid settlement amount')
    require(buyer.escrow_cents >= amount, 'Escrow balance is inconsistent')
    gross = amount - refund
    fee = (payment.released_cents + gross) // 100 - payment.earned_fee_cents
    batch = 'PS-' + secrets.token_hex(10)
    buyer.escrow_cents -= amount
    buyer.available_cents += refund
    seller.available_cents += gross - fee
    fees.available_cents += fee
    line(buyer, payment, 'debit', amount, 'escrow', 'release', batch)
    line(buyer, payment, 'credit', refund, 'available', 'refund', batch)
    line(seller, payment, 'credit', gross - fee, 'available', 'release', batch)
    line(fees, payment, 'credit', fee, 'available', 'fee', batch)
    payment.released_cents += gross
    payment.refunded_cents += refund
    payment.earned_fee_cents += fee


def remaining(payment):
    return payment.escrow.money_cents - payment.released_cents - payment.refunded_cents
