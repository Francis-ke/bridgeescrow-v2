from flask import request
from app.models import User
from app.models.checkout_security import CheckoutAuth
from app.models.mixins import utcnow
from app.core.db import db
from .integration_common import digest, require


def authorize(order):
    token = request.headers.get('X-Checkout-Session', '')
    session = CheckoutAuth.query.filter_by(order_id=order.id, session_hash=digest(token)).first() if token else None
    require(session and session.session_expires > utcnow(), 'Verify your email to continue', 401)
    buyer = db.session.get(User, session.buyer_id)
    require(buyer and buyer.is_active, 'Buyer account is unavailable', 403)
    require(not order.buyer_id or order.buyer_id == buyer.id, 'This order belongs to another buyer', 403)
    return session, buyer
