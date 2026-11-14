import hmac
import secrets
from datetime import timedelta
from marshmallow import Schema, fields, validate
from app.core.db import db
from app.models import User
from app.models.checkout_security import CheckoutAuth
from app.models.mixins import utcnow
from .integration_common import require, secret_hash, digest
from . import checkout_mail


class BuyerSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=190))
    full_name = fields.String(required=True, validate=validate.Length(min=3, max=120))
    phone = fields.String(required=True, validate=validate.Length(min=7, max=32))
    address = fields.String(required=True, validate=validate.Length(min=5, max=500))


def request_code(order, payload):
    data = BuyerSchema().load(payload)
    require(order.state != 'pending' or order.expires_at > utcnow(), 'This checkout has expired', 410)
    email = data['email'].lower()
    if order.buyer_id:
        require(db.session.get(User, order.buyer_id).email == email, 'Unable to verify this order', 403)
    latest = CheckoutAuth.query.filter_by(order_id=order.id).order_by(CheckoutAuth.id.desc()).first()
    require(not latest or utcnow() - latest.sent_at >= timedelta(seconds=60), 'Wait 60 seconds before requesting another code', 429)
    code, challenge = f'{secrets.randbelow(1000000):06d}', secrets.token_urlsafe(24)
    row = CheckoutAuth(order_id=order.id, challenge=challenge, email=email,
        full_name=data['full_name'].strip(), phone=data['phone'].strip(), address=data['address'].strip(),
        otp_hash=secret_hash(challenge + code), expires_at=utcnow() + timedelta(minutes=10), sent_at=utcnow())
    require(len(row.full_name) >= 3 and len(row.address) >= 5, 'Enter your full name and delivery address', 422)
    checkout_mail.send(email, 'Verify your BridgeEscrow checkout', f'Your checkout OTP is {code}. It expires in 10 minutes.')
    CheckoutAuth.query.filter_by(order_id=order.id, session_hash=None).update({'expires_at': utcnow()})
    db.session.add(row)
    db.session.commit()
    return {'challenge_id': challenge, 'email': email, 'status': 'otp_sent'}


def verify(order, payload):
    require(isinstance(payload, dict), 'Submit a JSON object', 422)
    row = CheckoutAuth.query.filter_by(order_id=order.id, challenge=payload.get('challenge_id')).with_for_update().first()
    require(row and row.expires_at > utcnow() and row.attempts < 5 and not row.session_hash, 'OTP is expired, used, or locked', 422)
    code = payload.get('otp', '')
    if not isinstance(code, str) or not hmac.compare_digest(row.otp_hash, secret_hash(row.challenge + code)):
        row.attempts += 1
        db.session.commit()
        require(False, 'Incorrect OTP', 422)
    require(order.state != 'pending' or order.expires_at > utcnow(), 'This checkout has expired', 410)
    buyer = User.query.filter_by(email=row.email).first()
    if not buyer:
        from app.services.accounts import next_account_number
        buyer = User(account_number=next_account_number(), full_name=row.full_name,
            email=row.email, phone='CK-' + secrets.token_hex(8), email_verified=True)
        buyer.set_password(secrets.token_urlsafe(48))
        db.session.add(buyer)
        db.session.flush()
    require(buyer.is_active and buyer.id != order.seller_id, 'Choose another active buyer account', 403)
    require(not order.buyer_id or order.buyer_id == buyer.id, 'Checkout belongs to another buyer', 403)
    buyer.email_verified = True
    token = secrets.token_urlsafe(32)
    row.buyer_id, row.session_hash = buyer.id, digest(token)
    row.session_expires = utcnow() + timedelta(minutes=30)
    db.session.commit()
    return {'session_token': token, 'status': 'verified'}
