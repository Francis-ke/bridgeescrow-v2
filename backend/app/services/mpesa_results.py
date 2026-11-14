from decimal import Decimal, InvalidOperation
from flask import current_app
from app.core.db import db
from app.core.errors import ApiError
from app.models import Payment
from . import payment_service
from .providers import daraja


def callback(body, reference=None):
    data = body.get('Body', {}).get('stkCallback', {})
    identifier = data.get('CheckoutRequestID')
    query = Payment.query.filter_by(provider=current_app.config['PAYMENT_MODE'])
    pay = query.filter_by(reference=reference).first() if reference else query.filter_by(checkout_request_id=identifier).first() if identifier else None
    if not pay or pay.provider == 'simulated':
        raise ApiError('Unknown provider checkout reference', 404, 'not_found')
    if not identifier or pay.checkout_request_id and pay.checkout_request_id != identifier:
        raise ApiError('Provider checkout reference mismatch', 422, 'payment_mismatch')
    duplicate = Payment.query.filter(Payment.provider == pay.provider, Payment.checkout_request_id == identifier, Payment.id != pay.id).first()
    if duplicate:
        raise ApiError('Provider checkout reference already used', 409, 'payment_mismatch')
    pay.checkout_request_id = identifier
    if pay.status in ('confirmed', 'failed'):
        return pay
    if str(data.get('ResultCode')) != '0':
        verified = daraja.query(identifier)
        if str(verified.get('ResultCode')) != str(data.get('ResultCode')) or 'ResultCode' not in data:
            raise ApiError('Provider has not confirmed this failure', 409, 'payment_pending')
        return payment_service.fail(pay.id)
    items = {item.get('Name'): item.get('Value') for item in data.get('CallbackMetadata', {}).get('Item', [])}
    from .phone_numbers import normalize
    if Decimal(str(items.get('Amount', '-1'))) * 100 != pay.amount_cents or normalize(items.get('PhoneNumber', '')) != pay.msisdn:
        raise ApiError('Payment callback does not match the request', 422, 'payment_mismatch')
    receipt = str(items.get('MpesaReceiptNumber', ''))
    if not receipt or Payment.query.filter(Payment.receipt == receipt, Payment.id != pay.id).first():
        raise ApiError('Missing or reused payment receipt', 409, 'payment_mismatch')
    verified = daraja.query(identifier)
    if str(verified.get('ResultCode')) != '0':
        raise ApiError('Provider has not confirmed this payment', 409, 'payment_pending')
    return payment_service.confirm(pay.id, receipt)
