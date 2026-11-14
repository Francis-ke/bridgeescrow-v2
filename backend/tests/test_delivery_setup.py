from tests.conftest import auth
from tests.protected_helpers import payload
from app.models.protected_payment import ProtectedPayment
from app.models import LedgerEntry


def test_simple_delivery_requires_password_and_persists_duration(client, buyer, seller):
    body = {'provider_id': seller['id'], 'amount': '125.50', 'duration_hours': 48, 'password': 'incorrect'}
    assert client.post('/api/protected/delivery', headers=auth(buyer), json=body).status_code == 401
    assert ProtectedPayment.query.count() == 0
    body['password'] = 'secret123'
    result = client.post('/api/protected/delivery', headers=auth(buyer), json=body)
    assert result.status_code == 201
    payment = result.json['payment']
    assert payment['category'] == 'delivery'
    assert payment['escrow']['amount'] == '125.50'
    assert payment['state'] == 'awaiting_acceptance'
    assert payment['rules']['release'] == 'client_approval'
    assert 'password' not in str(payment).lower()
    assert LedgerEntry.query.count() == 0
    assert client.get(f'/api/protected/{payment["escrow"]["id"]}', headers=auth(buyer)).status_code == 200


def test_generic_delivery_endpoint_cannot_bypass_password(client, buyer, seller):
    body = payload(seller, 'delivery')
    body.pop('password')
    assert client.post('/api/protected', headers=auth(buyer), json=body).status_code == 401


def test_delivery_duration_and_authentication_are_validated(client, buyer, seller):
    body = {'provider_id': seller['id'], 'amount': '100', 'password': 'secret123'}
    assert client.post('/api/protected/delivery', json={**body, 'duration_hours': 24}).status_code == 401
    for duration in [0, -1, 2161, 1.5]:
        result = client.post('/api/protected/delivery', headers=auth(buyer), json={**body, 'duration_hours': duration})
        assert result.status_code == 422
