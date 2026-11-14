from app.core.db import db
from app.models.mixins import TimestampMixin


class ApiUsageLog(TimestampMixin, db.Model):
    __tablename__ = 'api_usage_logs'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('developer_applications.id'), nullable=True, index=True)
    credential_id = db.Column(db.Integer, db.ForeignKey('api_credentials.id'), nullable=True, index=True)
    request_id = db.Column(db.String(64), unique=True, nullable=False)
    path = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    idempotency_key = db.Column(db.String(128), nullable=True)


class ApiRateWindow(db.Model):
    __tablename__ = 'api_rate_windows'
    credential_id = db.Column(db.Integer, db.ForeignKey('api_credentials.id'), primary_key=True)
    window_start = db.Column(db.DateTime, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=0)
