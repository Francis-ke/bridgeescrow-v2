from app.core.db import db
from app.models import Wallet
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox, key
from tests.developer_flow_helpers import application, bill, buyer_session


def test_application_scoping_environment_and_existing_seller_api_isolation(client, buyer, seller):
    appid, first = application(client, seller)
    otherid, second = application(client, seller, name='Second App')
    one, payload = bill(client, first)
    two, _ = bill(client, second)
    assert one['id'] != two['id']
    assert client.get('/api/v1/escrows/' + str(one['id']), headers=second).status_code == 404
    assert client.post('/api/v1/checkout/sessions', headers=second, json={'escrow_id': one['id']}).status_code == 404
    secret, _ = key(client, seller)
    assert client.get('/api/integrations/orders/' + str(one['id']), headers={'Authorization': 'Bearer ' + secret}).status_code == 404
    payload['environment'] = 'production'
    assert client.post('/api/v1/escrows', headers=first, json=payload).status_code == 422
    assert client.get(f'/api/v1/developer/apps/{appid}/sandbox', headers=auth(buyer)).status_code == 404


def test_mpesa_failure_retries_are_isolated_and_amount_tampering_rejected(client, buyer, seller, checkout_mailbox):
    before = {w.id: (w.available_cents, w.escrow_cents) for w in Wallet.query.all()}
    _, headers = application(client, seller)
    order, _ = bill(client, headers)
    created = client.post('/api/v1/checkout/sessions', headers=headers,
        json={'escrow_id': order['id'], 'method': 'mpesa', 'phone_number': '0712345678'})
    assert created.status_code == 201 and '?method=mpesa' in created.json['checkout_session']['url']
    url, scope = buyer_session(client, order, checkout_mailbox)
    failed = client.post(url + '/sandbox-failure', headers=scope, json={'method': 'mpesa'})
    assert failed.status_code == 200 and failed.json['retry_allowed']
    assert client.post(url + '/pay', headers=scope, json={'method': 'mpesa', 'phone_number': 'invalid'}).status_code == 422
    assert client.post(url + '/pay', headers=scope, json={'method': 'mpesa', 'phone_number': '0712345678', 'amount': '1'}).status_code == 422
    paid = client.post(url + '/pay', headers=scope, json={'method': 'mpesa', 'phone_number': '0712345678'})
    assert paid.status_code == 200
    assert all((db.session.get(Wallet, wid).available_cents, db.session.get(Wallet, wid).escrow_cents) == amount
               for wid, amount in before.items())
