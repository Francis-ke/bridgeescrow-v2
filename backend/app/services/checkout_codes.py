import hmac
import secrets
from datetime import timedelta
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.models.mixins import utcnow
from .integration_common import secret_hash, require
from . import checkout_mail


def prepare(order):
    code = f'{secrets.randbelow(100000000):08d}'
    order.delivery_hash = secret_hash(f'{order.id}:{code}')
    order.delivery_expires = utcnow() + timedelta(hours=order.duration_hours, days=7)
    order.delivery_attempts = 0
    buyer = db.session.get(User, order.buyer_id) if order.buyer_id else None
    if buyer and buyer.phone_verified:
        from .sms import queue
        queue(buyer, f'BridgeEscrow delivery code {code} for order {order.client_reference or order.external_id}. Share only after receiving and checking your order. This releases payment.',
              f'checkout-code-{order.id}-{order.delivery_hash[:16]}')
    return code


def email_code(order, code):
    email = db.session.get(User, order.buyer_id).email
    try:
        checkout_mail.send(email, 'Your BridgeEscrow delivery code',
            f'Order {order.external_id}: your delivery code is {code}. '
            'Keep this code private. Give it to the seller only after receiving and checking your package. '
            'The code releases the protected payment. Never share it before delivery.')
        order.code_sent_at = utcnow()
        db.session.commit()
        return True
    except ApiError:
        db.session.rollback()
        return False


def resend(order):
    from .checkout_state import state
    require(state(order) == 'paid', 'Only paid, undelivered orders have a delivery code')
    require(not order.code_sent_at or utcnow() - order.code_sent_at >= timedelta(seconds=60),
            'Wait 60 seconds before sending another code', 429)
    code = prepare(order)
    db.session.commit()
    return {'code_email_sent': email_code(order, code)}


def valid(order, code):
    require(order.delivery_hash and order.delivery_expires > utcnow(), 'Delivery code has expired')
    require(order.delivery_attempts < 5, 'Code attempts locked; ask the buyer to resend their code', 429)
    if not isinstance(code, str) or not hmac.compare_digest(order.delivery_hash, secret_hash(f'{order.id}:{code.strip()}')):
        order.delivery_attempts += 1
        db.session.commit()
        require(False, 'Incorrect delivery code', 422)
