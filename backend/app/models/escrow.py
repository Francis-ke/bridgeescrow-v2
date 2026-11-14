import secrets
from app.core.db import db
from app.models.mixins import TimestampMixin, utcnow

# hold -> funded -> released | refunded | disputed -> resolved
STATUSES = ("hold", "funded", "released", "refunded", "disputed", "cancelled")


class Escrow(TimestampMixin, db.Model):
    __tablename__ = "escrows"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(24), unique=True, nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    fee_cents = db.Column(db.BigInteger, default=0, nullable=False)
    currency = db.Column(db.String(3), default="KES", nullable=False)
    title = db.Column(db.String(140), nullable=False)
    status = db.Column(db.String(16), default="hold", nullable=False, index=True)
    release_expires_at = db.Column(db.DateTime, nullable=True)
    release_attempts = db.Column(db.Integer, default=0, nullable=False)
    release_code_hash = db.Column(db.String(128), nullable=True)
    receipt_hold_until = db.Column(db.DateTime, nullable=True)
    receipt_hold_reason = db.Column(db.String(400), nullable=True)
    hold_request_hours = db.Column(db.Integer, nullable=True)
    hold_request_reason = db.Column(db.String(400), nullable=True)
    hold_request_status = db.Column(db.String(16), nullable=True)
    hold_requested_at = db.Column(db.DateTime, nullable=True)
    hold_decided_at = db.Column(db.DateTime, nullable=True)
    protection = db.relationship('ProtectedPayment', back_populates='escrow', uselist=False)
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])

    @property
    def money_cents(self) -> int:
        """Integer cents (DB may hand back Decimal on SQLite)."""
        return int(self.amount_cents)

    @property
    def fee_money_cents(self) -> int:
        return int(self.fee_cents or 0)

    @staticmethod
    def new_reference() -> str:
        return "ESC" + secrets.token_hex(5).upper()

    @property
    def in_terminal_state(self) -> bool:
        return self.status in ("released", "refunded", "cancelled")

    def to_dict(self) -> dict:
        from app.models.mixins import MoneyMixin
        from app.services.escrow_details import transaction_details
        from app.services.protected.serialization import summary
        return {"id": self.id, "reference": self.reference,
                "title": self.title, "status": self.status,
                "amount": MoneyMixin.from_cents(self.money_cents),
                "fee": MoneyMixin.from_cents(self.fee_money_cents),
                "currency": self.currency,
                "buyer": self.buyer.full_name if self.buyer else None,
                "seller": self.seller.full_name if self.seller else None,
                "created_at": (self.created_at or utcnow()).isoformat(),
                "transaction": transaction_details(self),
                "protection": summary(self.protection) if self.protection else None}
