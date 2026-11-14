from app.core.db import db
from app.models.mixins import TimestampMixin

# Double-entry ledger: every movement writes 2+ rows that net to zero.
ENTRY_TYPES = ("deposit", "withdrawal", "hold", "release", "refund", "fee")


class LedgerEntry(TimestampMixin, db.Model):
    __tablename__ = "ledger_entries"
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False,
                          index=True)
    account_bucket = db.Column(db.String(16), nullable=False, default='available')
    batch_reference = db.Column(db.String(40), nullable=True, index=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrows.id"), nullable=True,
                          index=True)
    entry_type = db.Column(db.String(16), nullable=False)
    direction = db.Column(db.String(6), nullable=False)  # debit / credit
    amount_cents = db.Column(db.BigInteger, nullable=False)
    reference = db.Column(db.String(40), unique=True, nullable=False, index=True)
    description = db.Column(db.String(190), nullable=False, default="")
    idempotency_key = db.Column(db.String(80), unique=True, nullable=True)

    def to_dict(self) -> dict:
        from app.models import Escrow
        from app.services.protected.rules import CATEGORIES
        escrow = db.session.get(Escrow, self.escrow_id) if self.escrow_id else None
        category = escrow.protection.category if escrow and escrow.protection else None
        return {"payment_category": category, "category_label": CATEGORIES.get(category, "Wallet"), "id": self.id, "account_bucket": self.account_bucket,
                "batch_reference": self.batch_reference, "entry_type": self.entry_type,
                "direction": self.direction, "amount_cents": self.amount_cents,
                "reference": self.reference, "escrow_id": self.escrow_id,
                "description": self.description,
                "created_at": self.created_at.isoformat()}
