import re
from datetime import timedelta
from app.core.db import db
from app.models.checkout_security import CheckoutAuth
from app.models.merchant_api import CheckoutOrder
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox, key, order, verified, pay, delivery_code


def test_otp_attempts_cooldown_and_no_code_exposure(client, seller, checkout_mailbox):
    bill, _ = order(client, seller)
    token = bill['checkout_url'].rsplit('/', 1)[-1]
    details = {'email': 'guest@example.com', 'full_name': 'Buyer Person', 'phone': '0712345678', 'address': 'Delivery address'}
    sent = client.post(f'/api/checkout/{token}/request-otp', json=details)
    assert sent.status_code == 200 and 'otp' not in sent.json
    assert client.post(f'/api/checkout/{token}/request-otp', json=details).status_code == 429
    code = re.search(r'OTP is (\d{6})', checkout_mailbox[-1][2]).group(1)
    body = {'challenge_id': sent.json['challenge_id'], 'otp': 'incorrect'}
    for _ in range(5):
        assert client.post(f'/api/checkout/{token}/verify', json=body).status_code == 422
    body['otp'] = code
    assert client.post(f'/api/checkout/{token}/verify', json=body).status_code == 422


def test_checkout_sessions_are_order_scoped_and_seller_data_is_private(client, buyer, seller, admin, checkout_mailbox):
    bill, token, session, secret = verified(client, seller, checkout_mailbox)
    other, _ = order(client, seller, external='SECOND')
    other_token = other['checkout_url'].rsplit('/', 1)[-1]
    assert pay(client, other_token, session).status_code == 401
    assert pay(client, token, session).status_code == 200
    assert client.get(f'/api/checkout/{token}').json['order'].get('buyer') is None
    _, _ = key(client, admin)
    assert client.post(f'/api/seller/orders/{bill["id"]}/redeem', headers=auth(admin), json={'code': '12345678'}).status_code == 404
    rows = client.get('/api/seller/orders', headers=auth(seller)).json['orders']
    paid_order = next(row for row in rows if row['id'] == bill['id'])
    assert paid_order['buyer']['email'] == 'buyer@example.com'
    assert 'cvv' not in str(rows).lower() and 'card_cvv' not in str(rows)


def test_delivery_code_locks_and_buyer_can_rotate_it(client, buyer, seller, checkout_mailbox):
    bill, token, session, secret = verified(client, seller, checkout_mailbox)
    assert pay(client, token, session).status_code == 200
    original = delivery_code(checkout_mailbox)
    url = f'/api/seller/orders/{bill["id"]}/redeem'
    for _ in range(5):
        assert client.post(url, headers=auth(seller), json={'code': 'wrong'}).status_code == 422
    assert client.post(url, headers=auth(seller), json={'code': original}).status_code == 429
    row = db.session.get(CheckoutOrder, bill['id'])
    row.code_sent_at = utcnow() - timedelta(seconds=61)
    db.session.commit()
    resent = client.post(f'/api/checkout/{token}/delivery-code', headers={'X-Checkout-Session': session}, json={})
    assert resent.json['code_email_sent'] is True
    fresh = delivery_code(checkout_mailbox)
    assert client.post(url, headers=auth(seller), json={'code': fresh}).status_code == 200
