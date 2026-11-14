from app.core.db import db
from app.models import User
from app.models.phone_channel import PhoneChallenge, SmsMessage
from tests.conftest import auth
from tests.phone_helpers import verify_phone


def test_phone_login_requires_verified_phone_and_preserves_email_login(client, buyer):
    assert client.post('/api/auth/login', json={'phone': '0711111111', 'password': 'secret123'}).status_code == 401
    user = verify_phone(client, buyer, '0711111111')
    assert user['phone'] == '254711111111' and user['phone_verified']
    for identity in [{'phone': '+254711111111'}, {'phone': '0711111111'}, {'email': 'buyer@example.com'}]:
        response = client.post('/api/auth/login', json={**identity, 'password': 'secret123'})
        assert response.status_code == 200 and response.json['user']['id'] == buyer['id']
    assert client.post('/api/auth/login', json={'phone': '0711111111', 'email': 'buyer@example.com', 'password': 'secret123'}).status_code == 422


def test_phone_challenges_expire_lock_and_cannot_be_stolen(client, buyer, seller):
    response = client.post('/api/phone/verification', json={'phone': '0799999999'}, headers=auth(buyer))
    payload = {'challenge_id': response.json['challenge_id'], 'otp': '000000'}
    assert client.post('/api/phone/verify', json=payload, headers=auth(seller)).status_code == 422
    for _ in range(5):
        assert client.post('/api/phone/verify', json=payload, headers=auth(buyer)).status_code == 422
    assert db.session.get(User, buyer['id']).phone_verified is False
    assert PhoneChallenge.query.one().attempts == 5
    assert client.post('/api/phone/verification', json={'phone': 'bad'}, headers=auth(buyer)).status_code == 422


def test_simulated_sms_is_private_and_test_endpoint_cannot_target_other_users(client, buyer, seller):
    verify_phone(client, buyer, '0711111111')
    response = client.post('/api/phone/sms-test', json={'phone': '0722222222', 'body': 'Forged'}, headers=auth(buyer))
    assert response.status_code == 202
    assert response.json['message']['phone'] == '254711111111'
    assert 'Forged' not in response.json['message']['body']
    assert client.get('/api/phone/messages', headers=auth(seller)).json['messages'] == []
    assert client.get('/api/phone/messages').status_code == 401


def test_live_payments_cannot_use_simulated_phone_ownership(app, client, buyer):
    verify_phone(client, buyer, '0711111111')
    app.config['PAYMENT_MODE'] = 'daraja_live'
    response = client.post('/api/payments/stk-push', json={'amount': '10'}, headers={**auth(buyer), 'Idempotency-Key': 'phone-sim-test-12345'})
    assert response.status_code == 403
    assert response.json['error']['code'] == 'live_phone_verification_required'


def test_sms_provider_worker_acceptance_and_retry(app, client, buyer, monkeypatch):
    verify_phone(client, buyer, '0711111111')
    app.config.update(SMS_MODE='africastalking', AT_USERNAME='test', AT_API_KEY='test')
    assert client.post('/api/phone/sms-test', headers=auth(buyer)).status_code == 202
    from app.services.sms_worker import deliver
    monkeypatch.setattr('app.services.sms_transport.send', lambda phone, body, environment=None: 'provider-id')
    assert deliver() == 1
    assert SmsMessage.query.filter_by(mode='africastalking').one().status == 'accepted'
    rows = client.get('/api/phone/messages', headers=auth(buyer)).json['messages']
    assert rows[0]['body'] is None
