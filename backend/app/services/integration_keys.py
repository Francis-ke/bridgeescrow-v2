import secrets
from marshmallow import Schema, fields, validate
from app.core.db import db
from app.models.merchant_api import IntegrationProfile, MerchantApiKey
from app.models.mixins import utcnow
from app.services.escrow_details import iso
from .integration_common import safe_url, digest, require


class ProfileSchema(Schema):
    business_name = fields.String(required=True, validate=validate.Length(min=3, max=140))
    website = fields.String(required=True, validate=validate.Length(max=500))
    contact_email = fields.Email(required=True, validate=validate.Length(max=190))
    key_name = fields.String(load_default='Website', validate=validate.Length(min=1, max=80))


def describe(key):
    return {'id': key.id, 'name': key.name, 'prefix': key.key_prefix,
            'revoked': key.revoked_at is not None, 'created_at': iso(key.created_at)}


def create_key(user, payload):
    data = ProfileSchema().load(payload)
    require(safe_url(data['website']), 'Use an HTTPS website URL (HTTP is allowed for localhost)', 422)
    require(len(data['business_name'].strip()) >= 3, 'Enter your business name', 422)
    profile = db.session.get(IntegrationProfile, user.id) or IntegrationProfile(user_id=user.id)
    profile.business_name, profile.website = data['business_name'].strip(), data['website']
    profile.contact_email = data['contact_email'].lower()
    db.session.add(profile)
    raw = 'be_sk_' + secrets.token_urlsafe(32)
    key = MerchantApiKey(user_id=user.id, name=data['key_name'], key_hash=digest(raw), key_prefix=raw[:12])
    db.session.add(key)
    if user.role == 'customer':
        user.role = 'merchant'
    db.session.commit()
    from app.api.auth_routes import token_payload
    return {'key': describe(key), 'secret': raw, 'session': token_payload(user)}


def revoke(user, kid):
    key = MerchantApiKey.query.filter_by(user_id=user.id, id=kid).first()
    require(key is not None, 'API key not found', 404)
    key.revoked_at = utcnow()
    db.session.commit()
    return {'key': describe(key)}
