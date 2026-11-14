from datetime import timedelta
from app.core.db import db
from app.models import Escrow
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.test_escrow import _funded





def test_notifications_are_private_and_can_be_read(client, buyer, seller, admin):
    escrow = _funded(client, buyer, seller)
    assert client.get('/api/notifications').status_code == 401
    received = client.get('/api/notifications', headers=auth(seller)).json
    assert received['unread_count'] == 1
    item = received['notifications'][0]
    assert item['escrow_id'] == escrow['id']
    assert 'Brian Buyer' in item['message'] and '5' in item['message']
    assert client.get('/api/notifications', headers=auth(admin)).json['notifications'] == []
    assert client.put(f"/api/notifications/{item['id']}/read", headers=auth(buyer)).status_code == 404
    assert client.put(f"/api/notifications/{item['id']}/read", headers=auth(seller)).status_code == 200
    assert client.get('/api/notifications', headers=auth(seller)).json['unread_count'] == 0
    eid = escrow['id']
    code = client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).json['demo_code']
    assert client.post(f'/api/escrows/{eid}/confirm', headers=auth(buyer),
                       json={'code': code}).status_code == 200
    paid = client.get('/api/notifications', headers=auth(seller)).json
    assert paid['unread_count'] == 1
    assert any('You received KES 4950.00' in row['message'] for row in paid['notifications'])


def test_hold_request_decision_and_expiry_notifications(client, buyer, seller):
    eid = _funded(client, buyer, seller)['id']
    client.put(f'/api/escrows/{eid}/receipt-hold', headers=auth(seller), json={
        'hours': 24, 'reason': 'Waiting for a suitable delivery time.'})
    pending = client.get('/api/notifications', headers=auth(buyer)).json['notifications']
    assert sum('requested 24 hours' in row['message'] for row in pending) == 1
    client.post(f'/api/escrows/{eid}/receipt-hold/decision', headers=auth(buyer),
                json={'decision': 'accept'})
    seller_notifications = client.get('/api/notifications', headers=auth(seller)).json['notifications']
    assert any('accepted your hold-time request' in row['message'] for row in seller_notifications)
    esc = db.session.get(Escrow, eid)
    esc.receipt_hold_until = utcnow() - timedelta(minutes=1)
    db.session.commit()
    first = client.get('/api/notifications', headers=auth(seller)).json['notifications']
    second = client.get('/api/notifications', headers=auth(seller)).json['notifications']
    assert len(first) == len(second)
    assert sum('has ended' in row['message'] for row in first) == 1
    assert any('Buyer confirmation is still required' in row['message'] for row in first)


def test_demo_deposit_notifies_once_and_links_to_wallet(client, buyer, seller):
    import uuid
    payload = {'kind': 'deposit', 'method': 'card', 'amount': '123.45',
               'idempotency_key': str(uuid.uuid4())}
    first = client.post('/api/payments/demo-checkout', headers=auth(buyer), json=payload)
    assert first.status_code == 200
    assert client.post('/api/payments/demo-checkout', headers=auth(buyer), json=payload).status_code == 200
    result = client.get('/api/notifications', headers=auth(buyer)).json
    assert result['unread_count'] == 1
    row = result['notifications'][0]
    assert '123.45' in row['message'] and first.json['receipt']['reference'] in row['message']
    assert row['escrow_id'] is None and row['url'] == '/?statements=1'
    assert client.get('/api/notifications', headers=auth(seller)).json['notifications'] == []
    assert client.put(f"/api/notifications/{row['id']}/read", headers=auth(buyer)).status_code == 200
    assert client.get('/api/notifications', headers=auth(buyer)).json['unread_count'] == 0


def test_wallet_topup_notifies_once_for_retried_request(client, buyer):
    payload = {'amount': '50', 'idempotency_key': 'topup-notification-test'}
    for _ in range(2):
        assert client.post('/api/wallet/deposit', headers=auth(buyer), json=payload).status_code == 201
    result = client.get('/api/notifications', headers=auth(buyer)).json
    assert result['unread_count'] == 1
    assert '50.00' in result['notifications'][0]['message']
