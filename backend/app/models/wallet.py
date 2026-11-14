from app.core.db import db
from app.models.mixins import TimestampMixin


class Wallet(TimestampMixin, db.Model):
    """One wallet per user. Amounts are integer cents; balances are derived
    from the ledger, these columns are a denormalised cache."""
    __tablename__ = "wallets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True,
                        nullable=False)
    currency = db.Column(db.String(3), default="KES", nullable=False)
    available_cents = db.Column(db.BigInteger, default=0, nullable=False)
    escrow_cents = db.Column(db.BigInteger, default=0, nullable=False)
    user = db.relationship("User", back_populates="wallet")

    def to_dict(self) -> dict:
        from app.models.mixins import MoneyMixin
        return {"available": MoneyMixin.from_cents(self.available_cents),
                "escrow": MoneyMixin.from_cents(self.escrow_cents),
                "currency": self.currency}
