from sqlalchemy import case, func
from app.core.db import db
from app.models import Wallet, LedgerEntry, Payment
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from app.services.developer.webhook_secrets import issue
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox
from tests.developer_flow_helpers import application, bill, buyer_session


def balances():
    return {row.id: (row.available_cents, row.escrow_cents) for row in Wallet.query.all()}


def test_external_checkout_isolated_ledger_and_buyer_authorized_release(client, buyer, seller, checkout_mailbox):
    before = balances()
    appid, headers = application(client, seller)
    endpoint = WebhookEndpoint(app_id=appid, url='https://example.com/hook',
        events=['payment.pending', 'escrow.held', 'escrow.released'], secret_ciphertext=issue()[1])
    db.session.add(endpoint)
    db.session.commit()
    order, payload = bill(client, headers)
    initial = client.get('/api/wallet', headers=auth(seller)).json['wallet']['website_sandbox']
    assert initial['escrow'] == '0.00' and initial['available'] == '0.00'
    repeated = client.post('/api/v1/escrows', headers=headers, json=payload)
    assert repeated.json['escrow']['id'] == order['id']
    url, scope = buyer_session(client, order, checkout_mailbox)
    assert client.post(url + '/pay', headers=scope, json={'last4': '1234', 'method': 'card'}).status_code == 200
    status = client.get('/api/v1/escrows/' + str(order['id']), headers=headers).json['escrow']
    assert status['state'] == 'HELD' and Payment.query.one().status == 'confirmed'
    held = client.get('/api/wallet', headers=auth(seller)).json['wallet']['website_sandbox']
    assert held['escrow'] == '100.00' and held['available'] == '0.00'
    other = client.get('/api/wallet', headers=auth(buyer)).json['wallet']['website_sandbox']
    assert other['application_count'] == 0 and other['escrow'] == '0.00'
    request_url = f'/api/v1/escrows/{order["id"]}/release-requests'
    assert client.post(request_url, headers=headers, json={}).status_code == 202
    assert client.post(request_url, headers=headers, json={}).status_code == 202
    assert client.get('/api/v1/escrows/' + str(order['id']), headers=headers).json['escrow']['state'] == 'HELD'
    assert client.post(url + '/confirm', headers=headers, json={}).status_code == 401
    assert client.post(url + '/confirm', headers=scope, json={}).status_code == 200
    assert client.post(url + '/confirm', headers=scope, json={}).status_code == 200
    assert client.post('/api/v1/escrows', headers=headers, json=payload).json['escrow']['state'] == 'RELEASED'
    overview = client.get(f'/api/v1/developer/apps/{appid}/sandbox', headers=auth(seller)).json
    assert overview['available'] == '99.00' and overview['held'] == '0.00'
    released = client.get('/api/wallet', headers=auth(seller)).json['wallet']['website_sandbox']
    assert released['escrow'] == '0.00' and released['available'] == '99.00'
    assert released['production_enabled'] is False
    after = balances()
    assert all(after[key] == value for key, value in before.items())
    sums = db.session.query(LedgerEntry.batch_reference, func.sum(case(
        (LedgerEntry.direction == 'debit', LedgerEntry.amount_cents), else_=-LedgerEntry.amount_cents)))
    assert all(total == 0 for _, total in sums.group_by(LedgerEntry.batch_reference))
    assert sorted(row.event_type for row in WebhookDelivery.query.all()) == ['escrow.held', 'escrow.released', 'payment.pending']
