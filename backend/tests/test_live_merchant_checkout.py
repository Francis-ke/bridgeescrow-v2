from app.core.db import db
from app.models import User, Payment
from app.models.merchant_api import CheckoutOrder
from tests.conftest import auth
from tests.phone_helpers import verify_phone
from tests.test_mpesa_provider import configured, callback
from tests.developer_flow_helpers import bill, buyer_session
from tests.integration_helpers import checkout_mailbox


def live_app(app, client, buyer, seller, monkeypatch):
    verify_phone(client, seller, '0722222222')
    user = db.session.get(User, seller['id'])
    user.phone_verification_source = 'africastalking_live'
    db.session.commit()
    configured(app, client, buyer, monkeypatch)
    app.config['DEVELOPER_LIVE_ENABLED'] = True
    response = client.post('/api/v1/developer/apps', headers=auth(seller), json={
        'name': 'Live Store', 'description': 'Production M-PESA store', 'type': 'website', 'environment': 'production'})
    assert response.status_code == 201, response.json
    application = response.json['application']
    key = client.post(f'/api/v1/developer/apps/{application["id"]}/keys', headers=auth(seller), json={})
    assert key.status_code == 201 and key.json['secret_key'].startswith('be_live_sk_')
    return application, {'Authorization': 'Bearer ' + key.json['secret_key']}


def test_live_checkout_moves_confirmed_funds_to_merchant_escrow_then_available(app, client, buyer, seller, monkeypatch, checkout_mailbox):
    application, headers = live_app(app, client, buyer, seller, monkeypatch)
    order, _ = bill(client, headers)
    assert order['environment'] == 'production'
    url, session = buyer_session(client, order, checkout_mailbox)
    response = client.post(url + '/pay', headers=session, json={'method': 'mpesa', 'phone_number': '0711111111'})
    assert response.status_code == 200 and response.json['state'] == 'pending'
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '0.00'
    assert client.post(url + '/sandbox-failure', headers=session, json={'method': 'mpesa'}).status_code == 403
    assert client.post('/api/callbacks/mpesa/test-callback-token', json=callback()).status_code == 200
    actual = client.get('/api/v1/escrows/' + str(order['id']), headers=headers).json['escrow']
    assert actual['state'] == 'HELD'
    wallet = client.get('/api/wallet', headers=auth(seller)).json['wallet']
    assert wallet['incoming_escrow'] == '99.00' and wallet['available'] == '0.00'
    assert wallet['website_sandbox']['application_count'] == 0
    for _ in range(2):
        assert client.post(url + '/confirm', headers=session, json={}).status_code == 200
    wallet = client.get('/api/wallet', headers=auth(seller)).json['wallet']
    assert wallet['available'] == '99.00' and wallet['incoming_escrow'] == '0.00'
    assert client.post('/api/callbacks/mpesa/test-callback-token', json=callback()).status_code == 200
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '99.00'
    assert Payment.query.one().checkout_order_id == order['id']
    row = db.session.get(CheckoutOrder, order['id'])
    assert row.seller_id == seller['id'] and row.buyer_id == buyer['id']
    assert client.patch(f'/api/v1/developer/apps/{application["id"]}', headers=auth(seller), json={'environment': 'sandbox'}).status_code == 422
