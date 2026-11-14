from app.core.db import db
from app.models.mixins import TimestampMixin


class IntegrationProfile(TimestampMixin, db.Model):
    __tablename__ = 'integration_profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    business_name = db.Column(db.String(140), nullable=False)
    website = db.Column(db.String(500), nullable=False)
    contact_email = db.Column(db.String(190), nullable=False)


class MerchantApiKey(TimestampMixin, db.Model):
    __tablename__ = 'merchant_api_keys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    key_hash = db.Column(db.String(64), nullable=False, unique=True)
    key_prefix = db.Column(db.String(16), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)


class CheckoutOrder(TimestampMixin, db.Model):
    __tablename__ = 'checkout_orders'
    __table_args__ = (db.UniqueConstraint('seller_id', 'external_id'),
                     db.UniqueConstraint('developer_application_id', 'idempotency_key', name='uq_checkout_app_idempotency'))
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    developer_application_id = db.Column(db.Integer, db.ForeignKey('developer_applications.id'), nullable=True, index=True)
    client_reference = db.Column(db.String(100), nullable=True)
    idempotency_key = db.Column(db.String(128), nullable=True)
    external_id = db.Column(db.String(100), nullable=False)
    public_token = db.Column(db.String(64), nullable=False, unique=True)
    fingerprint = db.Column(db.String(64), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='KES')
    amount_cents = db.Column(db.BigInteger, nullable=False)
    items = db.Column(db.JSON, nullable=False)
    seller_snapshot = db.Column(db.JSON, nullable=False)
    buyer_snapshot = db.Column(db.JSON, nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey('escrows.id'), nullable=True, unique=True)
    card_last4 = db.Column(db.String(4), nullable=True)
    state = db.Column(db.String(16), nullable=False, default='pending')
    duration_hours = db.Column(db.Integer, nullable=False, default=72)
    expires_at = db.Column(db.DateTime, nullable=False)
    return_url = db.Column(db.String(500), nullable=False, default='')
    delivery_hash = db.Column(db.String(64), nullable=True)
    delivery_expires = db.Column(db.DateTime, nullable=True)
    delivery_attempts = db.Column(db.Integer, nullable=False, default=0)
    code_sent_at = db.Column(db.DateTime, nullable=True)
