from sqlalchemy import case, func
from app.core.db import db
from app.models import User, Wallet, LedgerEntry
from app.models.merchant_api import CheckoutOrder
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox, verified, pay, delivery_code


def test_checkout_verifies_email_secures_payment_and_releases_once(client, buyer, seller, checkout_mailbox):
    bill, token, session, secret = verified(client, seller, checkout_mailbox)
    assert client.post(f'/api/checkout/{token}/pay', json={'last4': '1234'}).status_code == 401
    response = pay(client, token, session)
    assert response.status_code == 200 and response.json['code_email_sent'] is True
    code = delivery_code(checkout_mailbox)
    assert code not in str(response.json)
    assert pay(client, token, session).json['escrow_id'] == response.json['escrow_id']
    wallet = client.get('/api/wallet', headers=auth(buyer)).json['wallet']
    assert wallet['available'] == '0.00' and wallet['escrow'] == '100.00'
    public = client.get(f'/api/checkout/{token}').json['order']
    assert 'buyer' not in public and public['amount'] == '100.00'
    stored = CheckoutOrder.query.filter_by(id=bill['id']).one()
    assert stored.delivery_hash != code and stored.buyer_snapshot['email'] == 'buyer@example.com'
    assert stored.card_last4 == '1234'
    eid = response.json['escrow_id']
    assert client.post(f'/api/protected/{eid}/approve', headers=auth(buyer), json={'milestone_id': 1}).status_code == 409
    assert client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).status_code == 409
    url = f'/api/integrations/orders/{bill["id"]}/redeem'
    headers = {'Authorization': 'Bearer ' + secret}
    assert client.post(url, headers=headers, json={'code': 'wrong'}).status_code == 422
    assert client.post(url, headers=headers, json={'code': code}).status_code == 200
    assert client.post(url, headers=headers, json={'code': code}).status_code == 200
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '99.00'
    assert client.get(f'/api/checkout/{token}').json['order']['state'] == 'completed'
    batches = db.session.query(LedgerEntry.batch_reference, func.sum(case(
        (LedgerEntry.direction == 'debit', LedgerEntry.amount_cents), else_=-LedgerEntry.amount_cents)))
    assert all(total == 0 for _, total in batches.filter(LedgerEntry.batch_reference.isnot(None)).group_by(LedgerEntry.batch_reference))


def test_guest_buyer_is_created_only_after_otp_and_card_secrets_are_rejected(client, seller, checkout_mailbox):
    bill, token, session, _ = verified(client, seller, checkout_mailbox, email='newguest@example.com')
    user = User.query.filter_by(email='newguest@example.com').one()
    assert user.email_verified is True
    bad = client.post(f'/api/checkout/{token}/pay', headers={'X-Checkout-Session': session},
                      json={'last4': '1234', 'cvv': '123', 'amount': '1'})
    assert bad.status_code == 422
    assert CheckoutOrder.query.filter_by(id=bill['id']).one().state == 'pending'
    assert pay(client, token, session).status_code == 200
