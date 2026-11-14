from datetime import timedelta
from sqlalchemy import update
from app.core.db import db
from app.core.errors import ApiError
from app.core.security import pin_matches
from app.models import User
from app.models.mixins import utcnow


def verify(user, pin):
    if not user.pin_hash:
        raise ApiError('Set a transaction PIN on the website first', 403, 'pin_required')
    if user.pin_locked_until and user.pin_locked_until > utcnow():
        raise ApiError('PIN locked for 15 minutes after repeated attempts', 429, 'pin_locked')
    if not pin_matches(str(pin), user.pin_salt, user.pin_hash):
        attempts = user.pin_attempts + 1
        db.session.execute(update(User).where(User.id == user.id).values(
            pin_attempts=attempts, pin_locked_until=utcnow() + timedelta(minutes=15) if attempts >= 5 else None))
        db.session.commit()
        raise ApiError('Incorrect transaction PIN', 403, 'invalid_pin')
    user.pin_attempts, user.pin_locked_until = 0, None
