import secrets
from decimal import Decimal, InvalidOperation
from flask import current_app
from sqlalchemy import select, text
from app.core.db import db
from app.core.errors import ApiError
from app.models import User, Wallet
from app.models.payout import Payout
from .phone_numbers import require_verified
from .transaction_pin import verify
from .ledger import debit
from .providers import daraja_payout, daraja


def initiate(uid, payload):
    cfg = current_app.config
    if cfg['PAYMENT_MODE'] != 'daraja_live' or not cfg.get('MPESA_B2C_ENABLED'):
        raise ApiError('Live payouts are not enabled. No funds were deducted.', 503, 'payout_unavailable')
    daraja.required('MPESA_B2C_INITIATOR', 'MPESA_B2C_SECURITY_CREDENTIAL', 'MPESA_SHORTCODE',
                    'MPESA_B2C_RESULT_URL', 'MPESA_B2C_TIMEOUT_URL', 'MPESA_CALLBACK_TOKEN')
    user = db.session.get(User, uid)
    phone = require_verified(user, live=True)
    verify(user, payload.get('pin', ''))
    key = str(payload.get('idempotency_key', ''))
    if not 16 <= len(key) <= 100:
        raise ApiError('Supply an idempotency key of 16–100 characters', 422, 'idempotency_required')
    try:
        amount = Decimal(str(payload.get('amount')))
        if not amount.is_finite() or amount != amount.to_integral_value() or not 10 <= amount <= 150000:
            raise ValueError()
    except (InvalidOperation, ValueError):
        raise ApiError('Payout amount must be whole KES between 10 and 150000', 422, 'invalid_amount') from None
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    wallet = db.session.execute(select(Wallet).where(Wallet.user_id == uid).with_for_update()
        .execution_options(populate_existing=True)).scalar_one()
    previous = Payout.query.filter_by(user_id=uid, client_key=key).first()
    if previous:
        if previous.amount_cents != int(amount * 100) or previous.phone != phone:
            raise ApiError('Idempotency key belongs to another payout', 409, 'idempotency_conflict')
        return previous
    payout = Payout(user_id=uid, reference='PO' + secrets.token_hex(12).upper(),
        client_key=key, phone=phone, amount_cents=int(amount * 100), status='requesting')
    db.session.add(payout)
    debit(wallet, payout.amount_cents, 'withdrawal', 'M-PESA payout reserved ' + payout.reference,
          key='payout-' + payout.reference)
    db.session.commit()
    try:
        response = daraja_payout.send(payout)
    except ApiError:
        payout.status = 'unknown'
        db.session.commit()
        return payout
    if 'ResponseCode' not in response or str(response['ResponseCode']) == '0' and not all(response.get(k) for k in ('ConversationID', 'OriginatorConversationID')):
        payout.status = 'unknown'
        db.session.commit()
        return payout
    if str(response['ResponseCode']) != '0':
        from .payout_results import finish
        return finish(payout.reference, {'Result': {'ResultCode': 'provider_rejected'}})
    db.session.refresh(payout)
    if payout.status == 'requesting':
        payout.status = 'pending'
    payout.conversation_id = response.get('ConversationID')
    payout.originator_id = response.get('OriginatorConversationID')
    db.session.commit()
    return payout
