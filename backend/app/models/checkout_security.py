from app.core.db import db
from app.models.mixins import TimestampMixin


class CheckoutAuth(TimestampMixin, db.Model):
    __tablename__ = 'checkout_auth'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('checkout_orders.id'), nullable=False, index=True)
    challenge = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(190), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    otp_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    sent_at = db.Column(db.DateTime, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_hash = db.Column(db.String(64), nullable=True, unique=True)
    session_expires = db.Column(db.DateTime, nullable=True)
