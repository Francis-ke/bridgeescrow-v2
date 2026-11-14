import hashlib
from flask import g, request
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.models.developer_application import DeveloperApplication, ApiCredential
from .rate_limit import consume


def authenticate(permission):
    authorization = request.headers.get('Authorization', '')
    raw = authorization[7:].strip() if authorization.startswith('Bearer ') else ''
    if not raw.startswith(('be_test_sk_', 'be_live_sk_')):
        raise ApiError('A secret API key is required', 401, 'api_key_required')
    credential = ApiCredential.query.filter_by(secret_hash=hashlib.sha256(raw.encode()).hexdigest()).first()
    if not credential:
        raise ApiError('Invalid API credentials', 401, 'invalid_api_key')
    app = db.session.get(DeveloperApplication, credential.app_id)
    g.developer_app_id, g.developer_credential_id = credential.app_id, credential.id
    if credential.revoked_at is not None:
        raise ApiError('This API credential has been revoked', 401, 'key_revoked')
    if not app or not app.active:
        raise ApiError('This application is inactive', 403, 'application_inactive')
    user = db.session.get(User, app.user_id)
    if not user or not user.is_active or not user.email_verified:
        raise ApiError('Application owner is unavailable', 403, 'account_unavailable')
    from .environments import require_environment, live_enabled
    if app.environment != 'sandbox' and not live_enabled():
        raise ApiError('Production financial operations are disabled', 403, 'environment_disabled')
    require_environment(app.environment, user if app.environment == 'production' else None)
    expected = 'be_live_sk_' if app.environment == 'production' else 'be_test_sk_'
    if not raw.startswith(expected):
        raise ApiError('Credential environment mismatch', 403, 'environment_mismatch')
    consume(credential.id)
    if permission not in credential.permissions:
        raise ApiError('This API key does not have the required permission', 403, 'insufficient_scope')
    return app, credential
