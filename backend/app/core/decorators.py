from functools import wraps
from app.core.errors import ApiError
from app.core.jwt import current_user_id, current_role


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        current_user_id()
        return fn(*a, **kw)
    return wrapper


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            current_user_id()
            if current_role() not in roles:
                raise ApiError("You are not allowed to do that", 403, "forbidden")
            return fn(*a, **kw)
        return wrapper
    return deco
