import secrets
from app.core.db import db
from app.models.mixins import TimestampMixin


class DeveloperApplication(TimestampMixin, db.Model):
    __tablename__ = 'developer_applications'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), unique=True, nullable=False,
                          default=lambda: 'app_' + secrets.token_urlsafe(18))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    website = db.Column(db.String(500), nullable=False, default='')
    type = db.Column(db.String(16), nullable=False)
    environment = db.Column(db.String(16), nullable=False, default='sandbox')
    active = db.Column(db.Boolean, nullable=False, default=True)


class ApiCredential(TimestampMixin, db.Model):
    __tablename__ = 'api_credentials'
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('developer_applications.id'), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False, default='Default key')
    public_key = db.Column(db.String(100), unique=True, nullable=False)
    secret_hash = db.Column(db.String(64), unique=True, nullable=False)
    prefix = db.Column(db.String(32), nullable=False)
    permissions = db.Column(db.JSON, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)
