from app.services.developer.authentication import authenticate
from app.core.db import db
from app.models import Wallet
from tests.user_factory import _make
from tests.conftest import auth


def setup(app):
    @app.get('/api/v1/test-auth/<permission>')
    def developer_auth_probe(permission):
        application, credential = authenticate(permission)
        return {'app_id': application.id, 'credential_id': credential.id}
    @app.get('/api/v1/test-rollback/<int:status>')
    def developer_rollback_probe(status):
        application, _ = authenticate('escrow:write')
        wallet = Wallet.query.filter_by(user_id=application.user_id).one()
        wallet.available_cents += 999
        db.session.flush()
        return {'message': 'uncommitted test mutation'}, status
    client = app.test_client()
    owner = _make(client, 'developer@example.com', '0700000111', 'Developer Owner')
    other = _make(client, 'other-developer@example.com', '0700000222', 'Other Developer')
    return client, owner, other


def create(client, owner, **changes):
    payload = {'name': 'Example Shop', 'description': 'Protected checkout for our shop.',
               'website': 'https://shop.example.com', 'type': 'website', 'environment': 'sandbox', **changes}
    response = client.post('/api/v1/developer/apps', headers=auth(owner), json=payload)
    assert response.status_code == 201, response.json
    return response.json['application']


def key(client, owner, application, **changes):
    response = client.post(f'/api/v1/developer/apps/{application["id"]}/keys', headers=auth(owner), json=changes)
    assert response.status_code == 201, response.json
    return response.json


def api_auth(secret):
    return {'Authorization': 'Bearer ' + secret}
