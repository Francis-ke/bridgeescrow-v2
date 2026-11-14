from app.core.db import db
from app.models.mixins import TimestampMixin, MoneyMixin


class DemoTransaction(TimestampMixin, db.Model):
    __tablename__ = "demo_transactions"
    __table_args__ = (db.UniqueConstraint("user_id", "idempotency_key"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrows.id"), nullable=True)
    idempotency_key = db.Column(db.String(64), nullable=False)
    fingerprint = db.Column(db.String(64), nullable=False)
    reference = db.Column(db.String(32), unique=True, nullable=False)
    kind = db.Column(db.String(16), nullable=False)
    method = db.Column(db.String(8), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    destination = db.Column(db.String(190), nullable=False, default="")
    last4 = db.Column(db.String(4), nullable=False, default="")

    def to_dict(self):
        from app.services.escrow_details import iso
        return {"reference": self.reference, "kind": self.kind, "method": self.method,
                "amount": MoneyMixin.from_cents(self.amount_cents), "destination": self.destination,
                "last4": self.last4, "createdAt": iso(self.created_at), "status": "completed",
                "demo": self.kind != "send", "escrow_id": self.escrow_id}
