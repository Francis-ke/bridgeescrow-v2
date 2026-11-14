import re
import pytest
from tests.conftest import auth
from app.services import checkout_mail


@pytest.fixture()
def checkout_mailbox(monkeypatch):
    messages = []
    monkeypatch.setattr(checkout_mail, 'send', lambda email, subject, body: messages.append((email, subject, body)))
    return messages


def key(client, seller):
    result = client.post('/api/seller/api/keys', headers=auth(seller), json={
        'business_name': 'Test Shop', 'website': 'https://shop.example', 'contact_email': 'shop@example.com'})
    assert result.status_code == 201, result.json
    return result.json['secret'], result.json['key']['id']


def order(client, seller, external='ORDER-1'):
    secret, _ = key(client, seller)
    result = client.post('/api/integrations/orders', headers={'Authorization': 'Bearer ' + secret}, json={
        'order_id': external, 'items': [{'description': 'Package', 'quantity': 1, 'unit_amount': '100.00'}]})
    assert result.status_code == 201, result.json
    return result.json['order'], secret


def verified(client, seller, messages, email='buyer@example.com', external='ORDER-1'):
    bill, secret = order(client, seller, external)
    token = bill['checkout_url'].rsplit('/', 1)[-1]
    sent = client.post(f'/api/checkout/{token}/request-otp', json={
        'email': email, 'full_name': 'Buyer Person', 'phone': '0712345678', 'address': 'Nairobi delivery address'})
    assert sent.status_code == 200, sent.json
    code = re.search(r'OTP is (\d{6})', messages[-1][2]).group(1)
    result = client.post(f'/api/checkout/{token}/verify', json={'challenge_id': sent.json['challenge_id'], 'otp': code})
    assert result.status_code == 200, result.json
    return bill, token, result.json['session_token'], secret


def pay(client, token, session):
    return client.post(f'/api/checkout/{token}/pay', headers={'X-Checkout-Session': session}, json={'last4': '1234'})


def delivery_code(messages):
    return re.search(r'delivery code is (\d{8})', messages[-1][2]).group(1)
