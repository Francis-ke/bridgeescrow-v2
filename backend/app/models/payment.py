from app.core.db import db
from app.models.mixins import TimestampMixin

# A payment intent represents money coming in from M-Pesa (STK Push) or a
# paybill/till settlement. It is the audit trail between a phone and the wallet.
KINDS = ("stk_push", "till", "paybill")
STATES = ("pending", "confirmed", "failed", "cancelled")


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(32), unique=True, nullable=False, index=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False,
                          index=True)
    kind = db.Column(db.String(16), default="stk_push", nullable=False)
    msisdn = db.Column(db.String(20), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(16), default="pending", nullable=False, index=True)
    checkout_request_id = db.Column(db.String(64), nullable=True, index=True)
    provider = db.Column(db.String(24), default='simulated', nullable=False)
    checkout_order_id = db.Column(db.Integer, db.ForeignKey('checkout_orders.id'), nullable=True, index=True)
    client_key = db.Column(db.String(100), nullable=True)
    __table_args__ = (db.UniqueConstraint('wallet_id', 'client_key', name='uq_payment_wallet_key'),
                      db.UniqueConstraint('provider', 'checkout_request_id', name='uq_payment_provider_checkout'))
    receipt = db.Column(db.String(32), nullable=True)

    def to_dict(self) -> dict:
        return {"id": self.id, "reference": self.reference, "kind": self.kind,
                "msisdn": self.msisdn, "status": self.status,
                "amount_cents": int(self.amount_cents),
                "checkout_order_id": self.checkout_order_id, "receipt": self.receipt, "provider": self.provider,
                "created_at": self.created_at.isoformat()}
