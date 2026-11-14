import re
from datetime import timedelta
from app.core.db import db
from app.models.checkout_security import CheckoutAuth
from app.models.merchant_api import CheckoutOrder
from app.models.mixins import utcnow
from tests.integration_helpers import checkout_mailbox, order, verified, pay


def test_new_otp_replaces_previous_unused_code(client, seller, checkout_mailbox):
    bill, _ = order(client, seller)
    token = bill['checkout_url'].rsplit('/', 1)[-1]
    url = f'/api/checkout/{token}'
    data = {'full_name': 'Buyer Name', 'email': 'guest@example.com',
            'phone': '0712345678', 'address': 'Nairobi delivery street'}
    first = client.post(url + '/request-otp', json=data).json
    old_code = re.search(r'OTP is (\d{6})', checkout_mailbox[-1][2]).group(1)
    row = CheckoutAuth.query.filter_by(challenge=first['challenge_id']).one()
    row.sent_at = utcnow() - timedelta(seconds=61)
    db.session.commit()
    second = client.post(url + '/request-otp', json=data).json
    new_code = re.search(r'OTP is (\d{6})', checkout_mailbox[-1][2]).group(1)
    assert client.post(url + '/verify', json={'challenge_id': first['challenge_id'], 'otp': old_code}).status_code == 422
    assert client.post(url + '/verify', json={'challenge_id': second['challenge_id'], 'otp': new_code}).status_code == 200


def test_expired_session_and_unpaid_order_cannot_fund(client, seller, checkout_mailbox):
    bill, token, session, _ = verified(client, seller, checkout_mailbox)
    row = CheckoutAuth.query.filter_by(order_id=bill['id']).one()
    row.session_expires = utcnow() - timedelta(seconds=1)
    db.session.commit()
    assert pay(client, token, session).status_code == 401
    other, _ = order(client, seller, external='EXPIRED')
    order_row = db.session.get(CheckoutOrder, other['id'])
    order_row.expires_at = utcnow() - timedelta(seconds=1)
    db.session.commit()
    data = {'full_name': 'Buyer Name', 'email': 'guest@example.com',
            'phone': '0712345678', 'address': 'Nairobi delivery street'}
    other_token = other['checkout_url'].rsplit('/', 1)[-1]
    assert client.post(f'/api/checkout/{other_token}/request-otp', json=data).status_code == 410


def test_disabled_seller_cannot_receive_new_checkout_funds(client, seller, checkout_mailbox):
    from app.models import User
    bill, token, session, _ = verified(client, seller, checkout_mailbox)
    db.session.get(User, seller['id']).is_active = False
    db.session.commit()
    assert pay(client, token, session).status_code == 403
    assert db.session.get(CheckoutOrder, bill['id']).state == 'pending'
