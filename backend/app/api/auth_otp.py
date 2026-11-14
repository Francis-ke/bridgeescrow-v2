from flask import request

from app.api.auth_routes import bp, token_payload
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.schemas.auth import EmailSchema, OtpSchema, PasswordResetSchema
from app.services.otp_service import RESET, REGISTER, issue, response, verify


def _email(payload):
    return EmailSchema().load(payload or {})["email"].lower()


def _user(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ApiError("No account was found for that email", 404, "email_not_found")
    return user


@bp.post("/register/verify")
def verify_registration():
    data = OtpSchema().load(request.get_json(silent=True) or {})
    user = _user(data["email"].lower())
    verify(user, REGISTER, data["otp"], data.get("challenge_id"))
    user.email_verified = True
    db.session.commit()
    return token_payload(user)


@bp.post("/register/resend")
def resend_registration():
    user = _user(_email(request.get_json(silent=True)))
    if user.email_verified:
        raise ApiError("This email is already verified", 409, "email_verified")
    challenge, code, sent = issue(user, REGISTER)
    db.session.commit()
    return response(user, challenge, code, sent)


@bp.post("/password/forgot")
def forgot_password():
    user = _user(_email(request.get_json(silent=True)))
    challenge, code, sent = issue(user, RESET)
    db.session.commit()
    return response(user, challenge, code, sent)


@bp.post("/password/reset")
def reset_password():
    data = PasswordResetSchema().load(request.get_json(silent=True) or {})
    if data["password"] != data["password_confirm"]:
        raise ApiError("Passwords do not match", 422, "password_mismatch")
    user = _user(data["email"].lower())
    verify(user, RESET, data["otp"], data.get("challenge_id"))
    user.set_password(data["password"])
    db.session.commit()
    return {"status": "password_reset"}
