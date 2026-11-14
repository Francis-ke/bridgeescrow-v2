import hashlib
import hmac
import secrets
from datetime import timedelta
from sqlalchemy import select
from flask import current_app
from app.core.db import db
from app.core.errors import ApiError
from app.models.phone_channel import PhoneChallenge
from app.models.mixins import utcnow
from . import phone_numbers, sms
from .channel_limits import consume


def start(user, phone):
    if current_app.config['SMS_MODE'] == 'africastalking' and not all(current_app.config.get(k) for k in ('AT_USERNAME', 'AT_API_KEY')):
        raise ApiError('Configure your SMS provider before requesting a phone code', 503, 'sms_unavailable')
    phone = phone_numbers.normalize(phone)
    consume(user.id, 'phone_verify')
    existing = phone_numbers.find(phone)
    if existing and existing.id != user.id:
        raise ApiError('This number is already linked to another account', 409, 'phone_taken')
    PhoneChallenge.query.filter_by(user_id=user.id, consumed_at=None).update({'consumed_at': utcnow()})
    code = f'{secrets.randbelow(1000000):06d}'
    source = 'africastalking_' + current_app.config['AT_ENVIRONMENT'] if current_app.config['SMS_MODE'] == 'africastalking' else 'simulated'
    row = PhoneChallenge(user_id=user.id, phone=phone, source=source, token=secrets.token_urlsafe(24),
        code_hash=hashlib.sha256(code.encode()).hexdigest(), expires_at=utcnow() + timedelta(minutes=10))
    db.session.add(row)
    sms.queue(user, f'BridgeEscrow phone verification code: {code}. Expires in 10 minutes. Do not share it.',
              'phone-verify-' + row.token, phone=phone)
    db.session.commit()
    return {'challenge_id': row.token, 'phone': phone, 'sms_mode': current_app.config['SMS_MODE']}


def verify(user, token, code):
    consume(user.id, 'phone_attempt', limit=10)
    row = db.session.execute(select(PhoneChallenge).where(PhoneChallenge.token == token,
        PhoneChallenge.user_id == user.id).with_for_update()).scalar_one_or_none()
    if not row or row.consumed_at or row.expires_at < utcnow() or row.attempts >= 5:
        raise ApiError('This phone verification code is expired or unavailable', 422, 'phone_otp_invalid')
    if not hmac.compare_digest(row.code_hash, hashlib.sha256(code.encode()).hexdigest()):
        row.attempts += 1
        db.session.commit()
        raise ApiError('Incorrect verification code', 422, 'phone_otp_invalid')
    existing = phone_numbers.find(row.phone)
    if existing and existing.id != user.id:
        raise ApiError('This number is already linked to another account', 409, 'phone_taken')
    user.phone, user.phone_verified = row.phone, True
    user.phone_verification_source = row.source
    row.consumed_at = utcnow()
    db.session.commit()
    return user
