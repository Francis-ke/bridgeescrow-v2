from app.core.db import db
from app.core.errors import ApiError
from app.models import LedgerEntry, Payment, Wallet
from app.models.merchant_api import CheckoutOrder
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from app.services import checkout_payment
from app.services.developer.webhook_secrets import issue
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox
from tests.developer_flow_helpers import application, bill, buyer_session


def test_external_keys_and_normal_accounts_cannot_settle_sandbox_orders(client, buyer, seller, checkout_mailbox):
    _, first = application(client, seller)
    _, second = application(client, seller, name='Separate Application')
    order, _ = bill(client, first)
    other, _ = bill(client, second)
    url, session = buyer_session(client, order, checkout_mailbox)
    assert client.post(url + '/pay', headers=first, json={'last4': '1234'}).status_code == 401
    other_url = '/api/checkout/' + other['checkout_url'].rsplit('/', 1)[-1]
    assert client.post(other_url + '/pay', headers=session, json={'last4': '1234'}).status_code == 401
    funded = client.post(url + '/pay', headers=session, json={'last4': '1234'})
    assert funded.status_code == 200
    eid = funded.json['escrow_id']
    for user in (buyer, seller):
        assert client.post(f'/api/escrows/{eid}/release', headers=auth(user)).status_code in (404, 409)
        assert client.post(f'/api/protected/{eid}/approve', headers=auth(user), json={}).status_code == 404
    for action in ('release-requests', 'disputes'):
        response = client.post(f'/api/v1/escrows/{order["id"]}/{action}', headers=second,
                               json={'reason': 'Another application cannot act on this payment.'})
        assert response.status_code == 404
    assert client.post(url + '/confirm', headers=first, json={}).status_code == 401
    assert client.get(f'/api/v1/escrows/{order["id"]}', headers=first).json['escrow']['state'] == 'HELD'


def test_funding_error_rolls_back_ledger_payment_and_enqueued_webhook(client, buyer, seller, checkout_mailbox, monkeypatch):
    before = {row.id: (row.available_cents, row.escrow_cents) for row in Wallet.query.all()}
    appid, headers = application(client, seller)
    db.session.add(WebhookEndpoint(app_id=appid, url='https://example.com/webhook',
        events=['escrow.held'], secret_ciphertext=issue()[1]))
    db.session.commit()
    order, _ = bill(client, headers)
    url, session = buyer_session(client, order, checkout_mailbox)
    original_event = checkout_payment.event

    def fail_after_enqueue(*args, **kwargs):
        original_event(*args, **kwargs)
        assert WebhookDelivery.query.count() == 1
        raise ApiError('Simulated precommit failure', 409)

    with monkeypatch.context() as patch:
        patch.setattr(checkout_payment, 'event', fail_after_enqueue)
        assert client.post(url + '/pay', headers=session, json={'last4': '1234'}).status_code == 409
    db.session.remove()
    row = db.session.get(CheckoutOrder, order['id'])
    assert row.state == 'pending' and row.escrow_id is None
    assert LedgerEntry.query.count() == Payment.query.count() == WebhookDelivery.query.count() == 0
    assert {w.id: (w.available_cents, w.escrow_cents) for w in Wallet.query.all()} == before
    assert client.post(url + '/pay', headers=session, json={'last4': '1234'}).status_code == 200
    assert WebhookDelivery.query.count() == 1
