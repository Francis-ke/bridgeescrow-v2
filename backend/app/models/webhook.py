from app.core.db import db
from app.models.mixins import TimestampMixin


class WebhookEndpoint(TimestampMixin, db.Model):
    __tablename__ = 'webhook_endpoints'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('developer_applications.id'), nullable=False, index=True)
    url = db.Column(db.String(500), nullable=False)
    secret_ciphertext = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    events = db.Column(db.JSON, nullable=False)

    def to_dict(self):
        from app.services.escrow_details import iso
        return {'id': self.id, 'app_id': self.app_id, 'url': self.url,
                'active': self.active, 'events': self.events,
                'created_at': iso(self.created_at), 'updated_at': iso(self.updated_at)}


class WebhookDelivery(TimestampMixin, db.Model):
    __tablename__ = 'webhook_deliveries'
    __table_args__ = (db.UniqueConstraint('endpoint_id', 'event_id'),)
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('webhook_endpoints.id'), nullable=False, index=True)
    event_id = db.Column(db.String(64), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pending')
    attempts = db.Column(db.Integer, nullable=False, default=0)
    next_attempt_at = db.Column(db.DateTime, nullable=True)
    http_status = db.Column(db.Integer, nullable=True)
    error = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        from app.services.escrow_details import iso
        return {'id': self.id, 'endpoint_id': self.endpoint_id, 'event_id': self.event_id,
                'event_type': self.event_type, 'status': self.status, 'attempts': self.attempts,
                'next_attempt_at': iso(self.next_attempt_at), 'http_status': self.http_status,
                'response_status': self.http_status, 'error': self.error, 'last_error': self.error,
                'created_at': iso(self.created_at), 'updated_at': iso(self.updated_at),
                'last_attempt_at': iso(self.updated_at) if self.attempts else None}
