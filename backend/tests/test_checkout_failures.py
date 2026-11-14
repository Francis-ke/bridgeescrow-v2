from app.core.db import db
from app.core.errors import ApiError
from app.models.checkout_security import CheckoutAuth
from app.models.merchant_api import CheckoutOrder
from app.services import checkout_mail
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox, verified, pay, delivery_code


def test_paid_order_is_not_double_charged_if_delivery_email_fails(client, buyer, seller, checkout_mailbox, monkeypatch):
    bill, token, session, _ = verified(client, seller, checkout_mailbox)
    def fail(*args):
        raise ApiError('Mail failed', 503, 'email_unavailable')
    monkeypatch.setattr(checkout_mail, 'send', fail)
    result = pay(client, token, session)
    assert result.status_code == 200 and result.json['code_email_sent'] is False
    assert pay(client, token, session).json['escrow_id'] == result.json['escrow_id']
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['escrow'] == '100.00'


def test_dispute_blocks_delivery_redemption_and_admin_refund_updates_status(client, buyer, seller, admin, checkout_mailbox):
    bill, token, session, _ = verified(client, seller, checkout_mailbox)
    paid = pay(client, token, session)
    eid = paid.json['escrow_id']
    issue = client.post(f'/api/escrows/{eid}/disputes', headers=auth(buyer), json={
        'reason': 'The package did not contain the items that were ordered.'})
    assert issue.status_code == 201
    code = delivery_code(checkout_mailbox)
    assert client.post(f'/api/seller/orders/{bill["id"]}/redeem', headers=auth(seller), json={'code': code}).status_code == 409
    resolved = client.post(f'/api/admin/disputes/{issue.json["dispute"]["id"]}/resolve', headers=auth(admin), json={
        'outcome': 'refund', 'resolution': 'The administrator approves refunding the non-delivered order.'})
    assert resolved.status_code == 200
    assert client.get(f'/api/checkout/{token}').json['order']['state'] == 'refunded'
    assert pay(client, token, session).json['state'] == 'refunded'
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '100.00'
