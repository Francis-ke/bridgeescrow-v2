import hashlib, hmac, secrets
from werkzeug.security import generate_password_hash, check_password_hash

ITERATIONS = 120_000


def hash_password(raw: str) -> str:
    return generate_password_hash(raw, method="pbkdf2:sha256:260000")


def verify_password(raw: str, hashed: str) -> bool:
    return check_password_hash(hashed, raw)


def hash_pin(pin: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), ITERATIONS).hex()


def new_salt() -> str:
    return secrets.token_hex(16)


def pin_matches(pin: str, salt: str, expected: str) -> bool:
    return hmac.compare_digest(hash_pin(pin, salt), expected)


def random_token(n: int = 32) -> str:
    return secrets.token_urlsafe(n)
