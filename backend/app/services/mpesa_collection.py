from decimal import Decimal, InvalidOperation
from flask import current_app
from app.core.db import db
from app.core.errors import ApiError
from app.models import Payment, User
from .phone_numbers import require_verified
from .wallet_service import wallet_for
from . import payment_service
from .providers import daraja


def initiate(uid, amount, client_key, checkout_order=None):
    cfg = current_app.config
    phone = require_verified(db.session.get(User, uid), live=cfg['PAYMENT_MODE'] == 'daraja_live')
    if not client_key or not 16 <= len(client_key) <= 100:
        raise ApiError('Use an Idempotency-Key of 16–100 characters', 422, 'idempotency_required')
    try:
        value = Decimal(str(amount))
        if not value.is_finite() or value != value.to_integral_value() or not 1 <= value <= 150000:
            raise ValueError()
    except (InvalidOperation, ValueError):
        raise ApiError('M-PESA amount must be whole KES between 1 and 150000', 422, 'invalid_amount') from None
    wallet = wallet_for(uid)
    previous = Payment.query.filter_by(wallet_id=wallet.id, client_key=client_key).first()
    if previous:
        if previous.amount_cents != int(value * 100) or previous.msisdn != phone or previous.provider != cfg['PAYMENT_MODE'] or previous.checkout_order_id != (checkout_order.id if checkout_order else None):
            raise ApiError('This idempotency key belongs to another payment', 409, 'idempotency_conflict')
        return previous
    daraja.required('MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET', 'MPESA_SHORTCODE',
                    'MPESA_PASSKEY', 'MPESA_CALLBACK_URL', 'MPESA_CALLBACK_TOKEN')
    pay = payment_service.start(uid, value, phone, commit=False)
    pay.provider, pay.client_key, pay.checkout_request_id = cfg['PAYMENT_MODE'], client_key, None
    pay.checkout_order_id = checkout_order.id if checkout_order else None
    db.session.commit()
    response = daraja.stk(pay)
    db.session.refresh(pay)
    if pay.status in ('confirmed', 'failed'):
        return pay
    if 'ResponseCode' not in response or str(response['ResponseCode']) == '0' and not response.get('CheckoutRequestID'):
        raise ApiError('Provider outcome is unknown. Keep this payment reference and do not submit a new request.', 502, 'provider_unavailable')
    if str(response['ResponseCode']) != '0':
        pay.status = 'failed'
        db.session.commit()
        raise ApiError('M-PESA did not accept this request', 502, 'provider_rejected')
    db.session.refresh(pay)
    if pay.checkout_request_id and pay.checkout_request_id != response['CheckoutRequestID']:
        raise ApiError('Provider checkout identifiers disagree; reconciliation required', 409, 'provider_mismatch')
    pay.checkout_request_id = response['CheckoutRequestID']
    db.session.commit()
    return pay


from .mpesa_results import callback
