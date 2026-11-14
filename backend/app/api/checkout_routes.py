from flask import Blueprint, request
from app.models.merchant_api import CheckoutOrder
from app.services.integration_common import lock_order, require
from app.services.integration_orders import public
from app.services import checkout_otp, checkout_codes
from app.services.checkout_session import authorize
from app.services.checkout_payment import pay

bp = Blueprint('checkout', __name__, url_prefix='/api/checkout')


@bp.get('/<token>')
def detail(token):
    order = CheckoutOrder.query.filter_by(public_token=token).first()
    require(order is not None, 'Checkout not found', 404)
    result = public(order)
    if request.headers.get('X-Checkout-Session'):
        session, buyer = authorize(order)
        result['buyer'] = order.buyer_snapshot or {'name': session.full_name, 'email': buyer.email}
        result['code_email_sent'] = bool(order.code_sent_at)
        result['escrow_id'] = order.escrow_id
        result['verified_phone'] = buyer.phone if buyer.phone_verified and buyer.phone_verification_source == 'africastalking_live' else None
    return {'order': result}


@bp.post('/<token>/request-otp')
def request_otp(token):
    return checkout_otp.request_code(lock_order(token=token), request.get_json(silent=True) or {})


@bp.post('/<token>/verify')
def verify(token):
    return checkout_otp.verify(lock_order(token=token), request.get_json(silent=True) or {})


@bp.post('/<token>/pay')
def confirm_payment(token):
    order = lock_order(token=token)
    session, buyer = authorize(order)
    return pay(order, session, buyer, request.get_json(silent=True) or {})


@bp.post('/<token>/delivery-code')
def delivery_code(token):
    order = lock_order(token=token)
    authorize(order)
    return checkout_codes.resend(order)
