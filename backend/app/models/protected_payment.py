from app.core.db import db
from app.models.mixins import TimestampMixin


class ProtectedPayment(TimestampMixin, db.Model):
    __tablename__ = 'protected_payments'
    id = db.Column(db.Integer, primary_key=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey('escrows.id'), unique=True, nullable=False)
    category = db.Column(db.String(24), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(32), nullable=False, default='awaiting_acceptance')
    client_accepted = db.Column(db.Boolean, nullable=False, default=False)
    provider_accepted = db.Column(db.Boolean, nullable=False, default=False)
    deadline_at = db.Column(db.DateTime, nullable=False)
    booking_start = db.Column(db.DateTime, nullable=True)
    booking_end = db.Column(db.DateTime, nullable=True)
    reservation_confirmed_at = db.Column(db.DateTime, nullable=True)
    provider_confirmed_at = db.Column(db.DateTime, nullable=True)
    client_confirmed_at = db.Column(db.DateTime, nullable=True)
    released_cents = db.Column(db.BigInteger, nullable=False, default=0)
    refunded_cents = db.Column(db.BigInteger, nullable=False, default=0)
    earned_fee_cents = db.Column(db.BigInteger, nullable=False, default=0)
    rules = db.Column(db.JSON, nullable=False)
    extension = db.Column(db.JSON, nullable=True)
    cancellation = db.Column(db.JSON, nullable=True)
    pre_dispute_state = db.Column(db.String(32), nullable=True)
    escrow = db.relationship('Escrow', back_populates='protection')
    milestones = db.relationship('WorkMilestone', order_by='WorkMilestone.id')


class WorkMilestone(TimestampMixin, db.Model):
    __tablename__ = 'work_milestones'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('protected_payments.id'), nullable=False, index=True)
    title = db.Column(db.String(140), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    deadline_at = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.String(24), nullable=False, default='pending')
    submission = db.Column(db.Text, nullable=True)
    revision_reason = db.Column(db.Text, nullable=True)
    revision_count = db.Column(db.Integer, nullable=False, default=0)
    submitted_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    revision_due_at = db.Column(db.DateTime, nullable=True)


class ProtectedEvent(TimestampMixin, db.Model):
    __tablename__ = 'protected_events'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('protected_payments.id'), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(40), nullable=False)
    detail = db.Column(db.Text, nullable=False, default='')
