import hashlib
import hmac
from urllib.parse import urlparse
from flask import current_app, request
from sqlalchemy import select, text
from app.core.db import db
from app.core.jwt import current_user_id
from app.models import User
from app.models.merchant_api import MerchantApiKey, CheckoutOrder
from app.services.protected.common import require


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def secret_hash(value):
    return hmac.new(current_app.config['SECRET_KEY'].encode(), value.encode(), hashlib.sha256).hexdigest()


def safe_url(value):
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return bool(parsed.hostname and not parsed.username and not parsed.password and
                (parsed.scheme == 'https' or parsed.scheme == 'http' and parsed.hostname in ['localhost', '127.0.0.1']))


def seller(api=False):
    token = request.headers.get('Authorization', '').removeprefix('Bearer ')
    if api:
        key = MerchantApiKey.query.filter_by(key_hash=digest(token), revoked_at=None).first()
        require(key is not None and token.startswith('be_sk_'), 'Invalid or revoked API key', 401)
        uid = key.user_id
    else:
        uid = current_user_id()
    user = db.session.get(User, uid)
    require(user and user.is_active and user.email_verified, 'An active verified account is required', 403)
    return user


def lock_order(token=None, oid=None):
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    query = select(CheckoutOrder).where(CheckoutOrder.public_token == token) if token else select(CheckoutOrder).where(CheckoutOrder.id == oid)
    order = db.session.execute(query.with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
    require(order is not None, 'Checkout not found', 404)
    return order
