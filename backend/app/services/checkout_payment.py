from marshmallow import Schema, fields, validate
from app.core.db import db
from app.models import User
from app.models.mixins import utcnow
from app.services.protected.common import require, event
from . import checkout_codes
from .checkout_state import state
from .checkout_funding import create


class PaySchema(Schema):
    last4 = fields.String(load_default='', validate=validate.Regexp(r'^(\d{4})?$'))
    method = fields.String(load_default='card', validate=validate.OneOf(['card', 'mpesa']))
    phone_number = fields.String(load_default='', validate=validate.Length(max=20))


def pay(order, session, buyer, payload):
    from flask import current_app
    require(order.developer_application_id or current_app.config['PAYMENT_MODE'] == 'simulated',
            'Legacy simulated checkout is disabled in provider mode', 403)
    data = PaySchema().load(payload)
    require(data['method'] != 'card' or len(data['last4']) == 4, 'Enter card details', 422)
    if order.state in ['paid', 'completed']:
        require(order.buyer_id == buyer.id, 'This checkout belongs to another buyer', 403)
        return {'state': state(order), 'escrow_id': order.escrow_id, 'code_email_sent': bool(order.code_sent_at)}
    require(order.state == 'pending' and order.expires_at > utcnow(), 'This checkout has expired', 410)
    require(buyer.id != order.seller_id, 'You cannot pay yourself', 422)
    seller = db.session.get(User, order.seller_id)
    require(seller.is_active and seller.email_verified, 'This seller is unavailable', 403)
    if order.developer_application_id:
        from .developer.checkout import ensure_active, record_payment, validate_method
        ensure_active(order)
        validate_method(data)
    else:
        require(data['method'] == 'card', 'This checkout supports cards only', 422)
    if order.developer_application_id:
        application = ensure_active(order)
        if application.environment == 'production':
            from .developer.live_checkout import start
            return start(order, session, buyer, data)
    payment = create(order, buyer)
    if order.developer_application_id:
        record_payment(order, payment, data)
    order.buyer_id, order.escrow_id = buyer.id, payment.escrow_id
    order.card_last4 = data['last4'] or None
    order.buyer_snapshot = {'name': buyer.full_name, 'email': buyer.email,
        'shipping_name': session.full_name, 'phone': session.phone, 'address': session.address}
    order.state = 'paid'
    code = checkout_codes.prepare(order)
    event(payment, buyer.id, 'checkout_paid', 'Payment secured; release requires buyer confirmation.')
    db.session.commit()
    return {'state': 'paid', 'escrow_id': payment.escrow_id,
            'code_email_sent': checkout_codes.email_code(order, code)}
