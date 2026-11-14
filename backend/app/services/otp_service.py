from app.services.otp_email import _send_email
from datetime import timedelta
import hashlib
import hmac
import secrets
import smtplib

from flask import current_app
from app.core.db import db
from app.core.errors import ApiError
from app.core.security import random_token
from app.models import OtpChallenge, User
from app.models.mixins import utcnow

REGISTER = "register"
RESET = "password_reset"


def _digest(code):
    return hashlib.sha256(code.encode()).hexdigest()




def issue(user: User, purpose: str):
    now = utcnow()
    OtpChallenge.query.filter_by(user_id=user.id, purpose=purpose,
                                 consumed_at=None).update({"consumed_at": now})
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge = OtpChallenge(
        user_id=user.id, purpose=purpose, challenge_token=random_token(24),
        code_hash=_digest(code),
        expires_at=now + timedelta(seconds=current_app.config["OTP_TTL_SECONDS"]),
    )
    db.session.add(challenge)
    db.session.flush()
    sent = _send_email(user, code, purpose)
    return challenge, code, sent


def response(user, challenge, code, sent):
    result = {"status": "otp_sent", "email": user.email,
              "challenge_id": challenge.challenge_token,
              "email_sent": sent}
    return result


def verify(user: User, purpose: str, code: str, challenge_id=None):
    query = OtpChallenge.query.filter_by(user_id=user.id, purpose=purpose,
                                         consumed_at=None)
    if challenge_id:
        query = query.filter_by(challenge_token=challenge_id)
    challenge = query.order_by(OtpChallenge.created_at.desc()).first()
    now = utcnow()
    if not challenge or challenge.expires_at < now:
        raise ApiError("That OTP is invalid or expired", 422, "otp_invalid")
    if challenge.attempts >= current_app.config["OTP_MAX_ATTEMPTS"]:
        raise ApiError("Too many OTP attempts; send a new code", 429, "otp_locked")
    if not hmac.compare_digest(challenge.code_hash, _digest(code)):
        challenge.attempts += 1
        db.session.commit()
        raise ApiError("That OTP is invalid", 422, "otp_invalid")
    challenge.consumed_at = now
    return challenge
