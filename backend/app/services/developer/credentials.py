import hashlib
import secrets
from app.core.db import db
from app.core.errors import ApiError
from app.models.mixins import utcnow
from app.models.developer_application import ApiCredential
from .applications import owned_app
from .schemas import CredentialSchema


def describe(key):
    from app.services.escrow_details import iso
    return {'id': key.id, 'name': key.name, 'public_key': key.public_key, 'prefix': key.prefix,
            'permissions': key.permissions, 'active': key.revoked_at is None,
            'created_at': iso(key.created_at), 'revoked_at': iso(key.revoked_at)}


def generate(app, payload):
    if not app.active:
        raise ApiError('Only active applications can generate keys', 403, 'environment_disabled')
    data = CredentialSchema().load(payload)
    from .environments import require_environment
    require_environment(app.environment)
    prefix = 'be_live_' if app.environment == 'production' else 'be_test_'
    raw = prefix + 'sk_' + secrets.token_urlsafe(32)
    key = ApiCredential(app_id=app.id, name=data['name'].strip() or 'Default key',
        public_key=prefix + 'pk_' + secrets.token_urlsafe(24),
        secret_hash=hashlib.sha256(raw.encode()).hexdigest(), prefix=raw[:22],
        permissions=sorted(set(data['permissions'])))
    db.session.add(key)
    db.session.flush()
    return key, raw


def create(identifier, payload):
    key, raw = generate(owned_app(identifier), payload)
    db.session.commit()
    return {'credential': describe(key), 'secret_key': raw}


def own_key(kid):
    key = db.session.get(ApiCredential, kid)
    if not key:
        raise ApiError('Credential not found', 404, 'not_found')
    app = owned_app(key.app_id)
    return key, app


def revoke(kid):
    key, _ = own_key(kid)
    key.revoked_at = key.revoked_at or utcnow()
    db.session.commit()
    return {'credential': describe(key)}


def rotate(kid):
    old, app = own_key(kid)
    if old.revoked_at:
        raise ApiError('This key is revoked', 409, 'key_revoked')
    key, raw = generate(app, {'name': old.name, 'permissions': old.permissions})
    old.revoked_at = utcnow()
    db.session.commit()
    return {'credential': describe(key), 'secret_key': raw}
