from datetime import timedelta
from app.core.db import db
from app.models import Escrow
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.test_escrow import _funded





def test_recipient_hold_persists_and_blocks_release(client, buyer, seller):
    escrow = _funded(client, buyer, seller)
    eid = escrow['id']
    code = client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).json['demo_code']
    result = client.put(f'/api/escrows/{eid}/receipt-hold', headers=auth(seller), json={
        'hours': 48, 'reason': 'Waiting for delivery confirmation.'})
    assert result.status_code == 200
    assert result.json['escrow']['transaction']['hold_request']['status'] == 'pending'
    assert result.json['escrow']['transaction']['receipt_hold_active'] is False
    accepted = client.post(f'/api/escrows/{eid}/receipt-hold/decision',
                           headers=auth(buyer), json={'decision': 'accept'})
    assert accepted.status_code == 200
    info = accepted.json['escrow']['transaction']
    assert info['receipt_hold_active'] is True
    assert info['receipt_hold_reason'] == 'Waiting for delivery confirmation.'
    assert info['receipt_hold_until'].endswith('+00:00')
    listed = client.get('/api/escrows?direction=received', headers=auth(seller)).json
    assert listed['escrows'][0]['transaction']['receipt_hold_reason'] == info['receipt_hold_reason']
    for endpoint, payload in [('release', {}), ('confirm', {'code': code})]:
        blocked = client.post(f'/api/escrows/{eid}/{endpoint}', headers=auth(buyer), json=payload)
        assert blocked.status_code == 409
        assert blocked.json['error']['code'] == 'receipt_hold_active'
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '0.00'
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['escrow'] == '5000.00'


def test_hold_authorization_and_validation(client, buyer, seller, admin):
    eid = _funded(client, buyer, seller)['id']
    endpoint = f'/api/escrows/{eid}/receipt-hold'
    data = {'hours': 24, 'reason': 'Awaiting the shipment arrival.'}
    assert client.put(endpoint, json=data).status_code == 401
    assert client.put(endpoint, headers=auth(buyer), json=data).status_code == 403
    assert client.put(endpoint, headers=auth(admin), json=data).status_code == 404
    for payload in [dict(data, hours=0), dict(data, hours=721), dict(data, hours=1.5),
                    dict(data, reason='short'), dict(data, reason=' ' * 12), {'hours': 24}]:
        assert client.put(endpoint, headers=auth(seller), json=payload).status_code == 422
    assert client.put(endpoint, headers=auth(seller), json=dict(data, hours=48)).status_code == 200
    assert client.post(f'/api/escrows/{eid}/receipt-hold/decision', headers=auth(buyer),
                       json={'decision': 'accept'}).status_code == 200
    assert client.put(endpoint, headers=auth(seller), json=data).status_code == 409
    assert client.put(endpoint, headers=auth(seller), json=dict(data, hours=72)).status_code == 200


def test_expired_hold_allows_normal_release(client, buyer, seller):
    eid = _funded(client, buyer, seller)['id']
    esc = db.session.get(Escrow, eid)
    esc.receipt_hold_until = utcnow() - timedelta(minutes=1)
    esc.receipt_hold_reason = 'Previous hold period has elapsed.'
    db.session.commit()
    code = client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).json['demo_code']
    result = client.post(f'/api/escrows/{eid}/confirm', headers=auth(buyer), json={'code': code})
    assert result.status_code == 200
    assert result.json['escrow']['status'] == 'released'
    assert result.json['escrow']['transaction']['receipt_hold_active'] is False
    assert client.put(f'/api/escrows/{eid}/receipt-hold', headers=auth(seller), json={
        'hours': 24, 'reason': 'Cannot hold released payments.'}).status_code == 409
