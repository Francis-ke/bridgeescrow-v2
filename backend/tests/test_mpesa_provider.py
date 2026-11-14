from app.core.db import db
from app.models import User, Payment
from tests.conftest import auth
from tests.phone_helpers import verify_phone


def configured(app, client, buyer, monkeypatch, mode='daraja_live'):
    verify_phone(client, buyer, '0711111111')
    user = db.session.get(User, buyer['id'])
    user.phone_verification_source = 'africastalking_live'
    db.session.commit()
    app.config.update(PAYMENT_MODE=mode, MPESA_CONSUMER_KEY='test', MPESA_CONSUMER_SECRET='test',
        MPESA_SHORTCODE='174379', MPESA_PASSKEY='test', MPESA_CALLBACK_URL='https://example.com/api/callbacks/mpesa',
        MPESA_CALLBACK_TOKEN='test-callback-token')
    monkeypatch.setattr('app.services.providers.daraja.stk', lambda pay: {'ResponseCode': '0', 'CheckoutRequestID': 'ws_provider_1'})
    monkeypatch.setattr('app.services.providers.daraja.query', lambda cid: {'ResultCode': '0'})
    return {**auth(buyer), 'Idempotency-Key': 'provider-order-123456'}


def callback(amount=100, phone=254711111111):
    return {'Body': {'stkCallback': {'CheckoutRequestID': 'ws_provider_1', 'ResultCode': 0,
        'CallbackMetadata': {'Item': [{'Name': 'Amount', 'Value': amount},
            {'Name': 'PhoneNumber', 'Value': phone}, {'Name': 'MpesaReceiptNumber', 'Value': 'REAL123'}]}}}}


def test_live_stk_uses_verified_account_phone_and_confirmed_provider_result(app, client, buyer, seller, monkeypatch):
    headers = configured(app, client, buyer, monkeypatch)
    response = client.post('/api/payments/stk-push', headers=headers, json={'amount': '100', 'msisdn': '0722222222'})
    assert response.status_code == 202
    pay = response.json['payment']
    assert pay['msisdn'] == '254711111111' and pay['provider'] == 'daraja_live'
    assert client.post(f'/api/payments/{pay["id"]}/simulate', headers=auth(buyer)).status_code == 403
    assert client.post(f'/api/payments/{pay["id"]}/simulate', headers=auth(seller)).status_code == 404
    assert client.post('/api/callbacks/mpesa', json=callback()).status_code == 401
    url = '/api/callbacks/mpesa/test-callback-token'
    assert client.post(url, json=callback(amount=1)).status_code == 422
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '0.00'
    for _ in range(2):
        assert client.post(url, json=callback()).status_code == 200
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '100.00'
    assert client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'}).json['payment']['id'] == pay['id']
    assert client.post('/api/payments/stk-push', headers=headers, json={'amount': '200'}).status_code == 409


def test_provider_sandbox_does_not_create_spendable_account_money(app, client, buyer, monkeypatch):
    headers = configured(app, client, buyer, monkeypatch, mode='daraja_sandbox')
    assert client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'}).status_code == 202
    assert client.post('/api/callbacks/mpesa/test-callback-token', json=callback()).status_code == 200
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '0.00'
    assert client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '100'}).status_code == 403
    assert client.post('/api/payments/demo-checkout', headers=auth(buyer), json={}).status_code == 403


def test_unknown_provider_result_cannot_be_simulated_or_retried_as_new_payment(app, client, buyer, monkeypatch):
    headers = configured(app, client, buyer, monkeypatch)
    from app.core.errors import ApiError
    calls = []
    def timeout(pay):
        calls.append(pay.id)
        raise ApiError('Provider timed out', 502, 'provider_unavailable')
    monkeypatch.setattr('app.services.providers.daraja.stk', timeout)
    assert client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'}).status_code == 502
    assert client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'}).status_code == 202
    assert len(calls) == 1 and Payment.query.one().status == 'pending'
