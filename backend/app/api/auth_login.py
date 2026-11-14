from flask import request
from sqlalchemy import func
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.schemas.auth import LoginSchema
from app.api.auth_routes import bp, token_payload


@bp.post("/login")
def login():
    data = LoginSchema().load(request.get_json(silent=True) or {})
    if data.get('phone'):
        from app.services.phone_numbers import find
        user = find(data['phone'])
        if user and not user.phone_verified:
            user = None
    else:
        user = User.query.filter(func.lower(User.email) == data['email'].strip().lower()).first()
    if user:
        from app.services.channel_limits import consume
        consume(user.id, 'login', limit=15, seconds=900)
    if not user or not user.check_password(data["password"]):
        raise ApiError("Wrong credentials", 401, "bad_credentials")
    if not user.email_verified:
        raise ApiError("Verify your email before signing in", 403, "email_not_verified")
    if not user.is_active:
        raise ApiError("This account is suspended", 403, "account_suspended")
    user.touch_login()
    db.session.commit()
    return token_payload(user)
