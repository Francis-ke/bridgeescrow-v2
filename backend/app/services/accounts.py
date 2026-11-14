import random
from app.core.db import db
from app.models import User, Wallet

ACCOUNT_PREFIX = "BE"


def _candidate() -> str:
    return f"{ACCOUNT_PREFIX}{random.randint(1_000_000, 9_999_999)}"


def next_account_number() -> str:
    """Unique 9-char BridgeEscrow account number, e.g. BE4281337.
    Retries a bounded number of times; uniqueness is also enforced by a
    DB unique index so a race can never create a duplicate."""
    for _ in range(25):
        candidate = _candidate()
        if not db.session.query(User.id).filter_by(account_number=candidate).first():
            return candidate
    raise RuntimeError("Could not allocate a unique account number")
