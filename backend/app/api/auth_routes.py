from flask import Blueprint, request
from app.core.db import db
from app.core.errors import ApiError
from app.core.jwt import issue_token
from app.models import User
from app.services.accounts import next_account_number
from app.services.otp_service import REGISTER, issue, response
from app.services.wallet_service import wallet_for
from app.schemas.auth import RegisterSchema

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def token_payload(user: User) -> dict:
    return {"token": issue_token(user.id, user.role), "user": user.to_dict(include_card_security=True),
            "wallet": wallet_for(user.id).to_dict()}


@bp.post("/register")
def register():
    data = RegisterSchema().load(request.get_json(silent=True) or {})
    if data["password"] != data["password_confirm"]:
        raise ApiError("Passwords do not match", 422, "password_mismatch")
    if User.query.filter_by(email=data["email"].lower()).first():
        raise ApiError("An account with this email already exists", 409, "email_taken")
    if data.get("national_id") and User.query.filter_by(
            national_id=data["national_id"]).first():
        raise ApiError("An account with this ID already exists", 409, "id_taken")
    account_number = next_account_number()
    phone = f"WEB-{account_number}"
    user = User(account_number=account_number, full_name=data["full_name"],
                email=data["email"].lower(), national_id=data.get("national_id"),
                phone=phone, role="customer", email_verified=False)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()
    wallet_for(user.id)
    challenge, code, sent = issue(user, REGISTER)
    db.session.commit()
    return response(user, challenge, code, sent), 202
