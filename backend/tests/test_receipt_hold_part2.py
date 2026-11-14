from datetime import timedelta
from app.core.db import db
from app.models import Escrow
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.test_escrow import _funded





def test_sender_can_decline_without_moving_funds(client, buyer, seller, admin):
    eid = _funded(client, buyer, seller)['id']
    endpoint = f'/api/escrows/{eid}/receipt-hold'
    payload = {'hours': 24, 'reason': 'Waiting for the next delivery window.'}
    assert client.put(endpoint, headers=auth(seller), json=payload).status_code == 200
    assert client.put(endpoint, headers=auth(seller), json=payload).status_code == 409
    decision_url = endpoint + '/decision'
    assert client.post(decision_url, headers=auth(seller), json={'decision': 'accept'}).status_code == 403
    assert client.post(decision_url, headers=auth(admin), json={'decision': 'accept'}).status_code == 404
    assert client.post(decision_url, headers=auth(buyer), json={'decision': 'other'}).status_code == 422
    declined = client.post(decision_url, headers=auth(buyer), json={'decision': 'decline'})
    assert declined.status_code == 200
    transaction = declined.json['escrow']['transaction']
    assert transaction['hold_request']['status'] == 'declined'
    assert transaction['receipt_hold_active'] is False
    assert transaction['receipt_hold_until'] is None
    assert declined.json['escrow']['status'] == 'funded'
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '0.00'
    assert client.post(decision_url, headers=auth(buyer), json={'decision': 'accept'}).status_code == 409
    assert client.put(endpoint, headers=auth(seller), json=payload).status_code == 200
