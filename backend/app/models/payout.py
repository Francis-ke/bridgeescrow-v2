from app.core.db import db
from app.models.mixins import TimestampMixin, MoneyMixin


class Payout(TimestampMixin, db.Model):
    __tablename__ = 'payouts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reference = db.Column(db.String(40), nullable=False, unique=True)
    client_key = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(24), nullable=False, default='reserved')
    conversation_id = db.Column(db.String(100), nullable=True, unique=True)
    originator_id = db.Column(db.String(100), nullable=True)
    receipt = db.Column(db.String(40), nullable=True, unique=True)
    __table_args__ = (db.UniqueConstraint('user_id', 'client_key', name='uq_payout_user_key'),)

    def to_dict(self):
        return {'reference': self.reference, 'phone': self.phone,
                'amount': MoneyMixin.from_cents(self.amount_cents), 'status': self.status,
                'receipt': self.receipt, 'created_at': self.created_at.isoformat()}
