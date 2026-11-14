from app.core.db import db
from app.models import Wallet
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from app.services.developer.webhook_secrets import issue
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox
from tests.developer_flow_helpers import application, bill, buyer_session


def test_sandbox_dispute_blocks_release_and_admin_refund_preserves_normal_wallets(client, buyer, seller, admin, checkout_mailbox):
    before = {w.id: (w.available_cents, w.escrow_cents) for w in Wallet.query.all()}
    appid, headers = application(client, seller)
    db.session.add(WebhookEndpoint(app_id=appid, url='https://example.com/hook',
        events=['escrow.disputed', 'escrow.refunded'], secret_ciphertext=issue()[1]))
    db.session.commit()
    order, _ = bill(client, headers)
    url, scope = buyer_session(client, order, checkout_mailbox)
    assert client.post(url + '/pay', headers=scope, json={'last4': '1234'}).status_code == 200
    body = {'reason': 'The delivered package did not match the order.'}
    raised = client.post(url + '/dispute', headers=scope, json=body)
    assert raised.status_code == 201, raised.json
    assert client.post(url + '/confirm', headers=scope, json={}).status_code == 409
    assert client.post(f'/api/v1/escrows/{order["id"]}/release-requests', headers=headers, json={}).status_code == 409
    did = raised.json['dispute']['id']
    resolved = client.post(f'/api/admin/disputes/{did}/resolve', headers=auth(admin),
        json={'outcome': 'refund', 'resolution': 'Sandbox order has not been correctly delivered.'})
    assert resolved.status_code == 200, resolved.json
    assert client.get(f'/api/v1/escrows/{order["id"]}', headers=headers).json['escrow']['state'] == 'REFUNDED'
    assert all((db.session.get(Wallet, wid).available_cents, db.session.get(Wallet, wid).escrow_cents) == amount
               for wid, amount in before.items())
    assert sorted(row.event_type for row in WebhookDelivery.query.all()) == ['escrow.disputed', 'escrow.refunded']
