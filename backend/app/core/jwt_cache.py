from flask import g
from app.core.jwt import decode_token, bearer_token


def reset_identity() -> None:
    """Flask keeps `g` alive for the whole app context (the test client reuses
    one), so the cached identity must be cleared at the start of each request."""
    g.pop("identity", None)


def identity() -> dict:
    if "identity" not in g:
        from app.core.db import db
        from app.core.errors import ApiError
        from app.models import User
        payload = decode_token(bearer_token())
        user = db.session.get(User, int(payload['sub']))
        if not user or not user.is_active or not user.email_verified:
            raise ApiError('This account is unavailable', 403, 'account_unavailable')
        payload['role'] = user.role
        g.identity = payload
    return g.identity
