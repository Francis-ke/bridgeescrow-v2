from datetime import datetime, timezone
from app.core.db import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow,
                           nullable=False)


class MoneyMixin:
    @staticmethod
    def to_cents(amount) -> int:
        """Convert a KES amount (string/float/Decimal) to integer cents."""
        from decimal import Decimal, ROUND_HALF_UP
        value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int(value * 100)

    @staticmethod
    def from_cents(cents: int) -> str:
        return f"{cents // 100}.{cents % 100:02d}"
