import hashlib
from app.models.developer_application import ApiCredential
from tests.conftest import auth
from tests.developer_helpers import setup, create, key, api_auth


def test_credentials_hash_secrets_show_once_and_do_not_leak_to_other_users(app):
    client, owner, other = setup(app)
    application = create(client, owner)
    issued = key(client, owner, application)
    raw, credential = issued['secret_key'], issued['credential']
    assert raw.startswith('be_test_sk_') and credential['public_key'].startswith('be_test_pk_')
    saved = ApiCredential.query.filter_by(id=credential['id']).one()
    assert saved.secret_hash == hashlib.sha256(raw.encode()).hexdigest()
    assert raw != saved.secret_hash and 'secret_hash' not in credential
    listed = client.get(f'/api/v1/developer/apps/{application["id"]}/keys', headers=auth(owner)).json
    assert 'secret_key' not in listed and raw not in str(listed)
    assert client.get(f'/api/v1/developer/apps/{application["id"]}/keys', headers=auth(other)).status_code == 404
    assert client.delete(f'/api/v1/developer/keys/{credential["id"]}', headers=auth(other)).status_code == 404
    assert client.post(f'/api/v1/developer/keys/{credential["id"]}/rotate', headers=auth(other)).status_code == 404
    assert client.get('/api/v1/test-auth/escrow:read', headers=api_auth(credential['public_key'])).status_code == 401


def test_rotation_revokes_old_secret_and_revocation_is_enforced(app):
    client, owner, _ = setup(app)
    application = create(client, owner)
    issued = key(client, owner, application)
    path = f'/api/v1/developer/keys/{issued["credential"]["id"]}'
    rotated = client.post(path + '/rotate', headers=auth(owner))
    assert rotated.status_code == 201
    replacement = rotated.json
    assert replacement['secret_key'] != issued['secret_key']
    assert client.get('/api/v1/test-auth/escrow:read', headers=api_auth(issued['secret_key'])).status_code == 401
    assert client.get('/api/v1/test-auth/escrow:read', headers=api_auth(replacement['secret_key'])).status_code == 200
    deleted = client.delete(f'/api/v1/developer/keys/{replacement["credential"]["id"]}', headers=auth(owner))
    assert deleted.status_code == 200 and deleted.json['credential']['active'] is False
    assert client.get('/api/v1/test-auth/escrow:read', headers=api_auth(replacement['secret_key'])).status_code == 401
