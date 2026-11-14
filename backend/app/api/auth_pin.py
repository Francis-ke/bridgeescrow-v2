from flask import request
from app.core.db import db
from app.core.errors import ApiError
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.core.security import new_salt, hash_pin
from app.models import User
from app.schemas.auth import PinSchema, ProfileSchema
from app.api.auth_routes import bp


@bp.post("/pin")
@login_required
def set_pin():
    pin = PinSchema().load(request.get_json(silent=True) or {})["pin"]
    user = db.session.get(User, current_user_id())
    user.pin_salt, user.pin_hash = new_salt(), None
    user.pin_hash = hash_pin(pin, user.pin_salt)
    user.pin_attempts, user.pin_locked_until = 0, None
    db.session.commit()
    return {"status": "pin_set"}


@bp.get("/me")
@login_required
def me():
    user = db.session.get(User, current_user_id())
    return {"user": user.to_dict(include_card_security=True)}


@bp.put("/me")
@login_required
def update_profile():
    data = ProfileSchema().load(request.get_json(silent=True) or {})
    user = db.session.get(User, current_user_id())
    user.full_name = data["full_name"].strip()
    db.session.commit()
    return {"user": user.to_dict(include_card_security=True)}
