import time, jwt
from flask import current_app, g, request
from app.core.errors import ApiError


def issue_token(user_id: int, role: str) -> str:
    cfg = current_app.config
    now = int(time.time())
    payload = {"sub": str(user_id), "role": role, "iat": now,
               "exp": now + cfg["JWT_TTL_SECONDS"]}
    return jwt.encode(payload, cfg["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ApiError("Session expired, please sign in again", 401, "token_expired")
    except jwt.InvalidTokenError:
        raise ApiError("Invalid authentication token", 401, "token_invalid")


def bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise ApiError("Missing bearer token", 401, "token_missing")
    return header[7:].strip()


def current_user_id() -> int:
    from app.core.jwt_cache import identity
    return int(identity()["sub"])


def current_role() -> str:
    from app.core.jwt_cache import identity
    return identity()["role"]
