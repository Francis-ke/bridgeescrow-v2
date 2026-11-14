from app.services.demo_checkout_input import CheckoutSchema, recipient_for
import hashlib
import json
import secrets
from decimal import Decimal
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from app.core.db import db
from app.core.errors import ApiError
from app.models import User, Wallet, Escrow, LedgerEntry
from app.models.demo_transaction import DemoTransaction
from app.services.wallet_service import wallet_for
from app.services.notifications import add

def checkout(uid, payload):
    from flask import current_app
    if current_app.config['PAYMENT_MODE'] != 'simulated' and payload.get('kind') != 'send':
        raise ApiError('Demo transactions are disabled in provider mode', 403, 'simulation_disabled')
    data = CheckoutSchema().load(payload)
    cents = int(data['amount'] * 100)
    if Decimal(cents) / 100 != data['amount']:
        raise ApiError('Use at most two decimal places', 422, 'invalid_amount')
    fingerprint = hashlib.sha256(json.dumps({k: str(v) for k, v in data.items()
                                           if k != 'idempotency_key'}, sort_keys=True).encode()).hexdigest()
    key = data['idempotency_key']
    previous = DemoTransaction.query.filter_by(user_id=uid, idempotency_key=key).first()
    if previous:
        if previous.fingerprint != fingerprint:
            raise ApiError('This request was already used for another transaction', 409, 'idempotency_conflict')
        return previous
    sender = db.session.get(User, uid)
    if not sender.is_active or not sender.email_verified:
        raise ApiError('An active verified account is required', 403, 'account_unavailable')
    recipient, target = recipient_for(uid, data, cents)
    wallet = wallet_for(uid)
    receipt = DemoTransaction(user_id=uid, idempotency_key=key, fingerprint=fingerprint,
        reference='TXN-' + secrets.token_hex(6).upper(), kind=data['kind'], method=data['method'],
        amount_cents=cents, destination=recipient.full_name if recipient else target, last4=data['last4'])
    db.session.add(receipt)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        previous = DemoTransaction.query.filter_by(user_id=uid, idempotency_key=key).first()
        if previous and previous.fingerprint == fingerprint:
            return previous
        raise ApiError('Transaction request already used', 409, 'idempotency_conflict')
    values = {'available_cents': Wallet.available_cents + cents}
    condition = Wallet.id == wallet.id
    entry_type, direction = 'deposit', 'credit'
    if data['kind'] != 'deposit':
        condition = condition & (Wallet.available_cents >= cents)
        values = {'available_cents': Wallet.available_cents - cents}
        entry_type, direction = ('transfer' if data['kind'] == 'send' else 'hold' if recipient else 'withdrawal' if data['kind'] == 'withdraw' else 'purchase'), 'debit'
        if recipient and data['kind'] != 'send':
            values['escrow_cents'] = Wallet.escrow_cents + cents
    if db.session.execute(update(Wallet).where(condition).values(**values)).rowcount != 1:
        db.session.rollback()
        raise ApiError('Insufficient funds in your wallet', 409, 'insufficient_funds')
    if recipient and data['kind'] == 'send':
        from app.services.direct_transfer import receive
        receive(sender, recipient, cents, receipt)
    elif recipient:
        escrow = Escrow(reference=Escrow.new_reference(), buyer_id=uid, seller_id=recipient.id,
            amount_cents=cents, fee_cents=cents // 100, title='Purchase' if data['kind'] == 'buy' else 'Money transfer', status='funded')
        db.session.add(escrow)
        db.session.flush()
        receipt.escrow_id = escrow.id
        add(recipient.id, escrow, f'funded-{escrow.id}',
            f'{sender.full_name} sent KES {data["amount"]} to escrow. View Received money for details.')
    db.session.add(LedgerEntry(wallet_id=wallet.id, escrow_id=receipt.escrow_id,
        entry_type=entry_type, direction=direction, amount_cents=cents,
        reference='LG' + secrets.token_hex(10).upper(), description=f'{data["kind"].capitalize()}: {receipt.reference}',
        idempotency_key=f'demo-{uid}-{key}'))
    if data['kind'] == 'deposit':
        add(uid, None, f'demo-deposit-{receipt.id}',
            f'Deposit of KES {cents // 100}.{cents % 100:02d} added to your wallet. Reference: {receipt.reference}')
    db.session.commit()
    return receipt
