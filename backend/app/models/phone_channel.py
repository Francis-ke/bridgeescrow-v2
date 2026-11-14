from app.core.db import db
from app.models.mixins import TimestampMixin


class PhoneChallenge(TimestampMixin, db.Model):
    __tablename__ = 'phone_challenges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(24), nullable=False, default='simulated')
    token = db.Column(db.String(64), nullable=False, unique=True)
    code_hash = db.Column(db.String(64), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=False)
    consumed_at = db.Column(db.DateTime, nullable=True)


class SmsMessage(TimestampMixin, db.Model):
    __tablename__ = 'sms_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text, nullable=False)
    event_key = db.Column(db.String(160), nullable=False, unique=True)
    environment = db.Column(db.String(16), nullable=False, default='local')
    mode = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    provider_id = db.Column(db.String(100), nullable=True)
    error = db.Column(db.String(160), nullable=True)
    next_attempt_at = db.Column(db.DateTime, nullable=True)


class UssdSession(TimestampMixin, db.Model):
    __tablename__ = 'ussd_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    request_hash = db.Column(db.String(64), nullable=True)
    reply = db.Column(db.Text, nullable=True)
    closed = db.Column(db.Boolean, nullable=False, default=False)


class ChannelRequest(TimestampMixin, db.Model):
    __tablename__ = 'channel_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scope = db.Column(db.String(24), nullable=False)
    __table_args__ = (db.Index('ix_channel_request_rate', 'user_id', 'scope', 'created_at'),)
