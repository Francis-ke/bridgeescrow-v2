from tests.conftest import auth
from tests.test_mpesa_provider import configured, callback


def funding(app, client, buyer, monkeypatch):
    headers = configured(app, client, buyer, monkeypatch)
    client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'})
    assert client.post('/api/callbacks/mpesa/test-callback-token', json=callback()).status_code == 200
    app.config.update(MPESA_B2C_ENABLED=True, MPESA_B2C_INITIATOR='test', MPESA_B2C_SECURITY_CREDENTIAL='test',
        MPESA_B2C_RESULT_URL='https://example.com/api/payouts/result', MPESA_B2C_TIMEOUT_URL='https://example.com/api/payouts/timeout')
    calls = []
    def send(payout):
        calls.append(payout.reference)
        return {'ResponseCode': '0', 'ConversationID': 'provider-conversation', 'OriginatorConversationID': 'provider-origin'}
    monkeypatch.setattr('app.services.providers.daraja_payout.send', send)
    client.post('/api/auth/pin', headers=auth(buyer), json={'pin': '1234'})
    return calls


def request(client, buyer):
    return client.post('/api/payouts', headers=auth(buyer), json={
        'amount': '10', 'pin': '1234', 'idempotency_key': 'withdrawal-request-1234'})


def test_payout_reserves_once_and_releases_reservation_after_confirmed_result(app, client, buyer, seller, monkeypatch):
    calls = funding(app, client, buyer, monkeypatch)
    response = request(client, buyer)
    assert response.status_code == 202
    payout = response.json['payout']
    assert payout['status'] == 'pending' and payout['phone'] == '254711111111'
    assert request(client, buyer).json['payout']['reference'] == payout['reference'] and len(calls) == 1
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '90.00'
    assert client.get('/api/payouts', headers=auth(seller)).json['payouts'] == []
    result = {'Result': {'ResultCode': 0, 'ConversationID': 'provider-conversation', 'TransactionID': 'PAYOUT123',
                        'ResultParameters': {'ResultParameter': [{'Key': 'TransactionAmount', 'Value': 10}]}}}
    url = '/api/payouts/result/' + payout['reference'] + '/test-callback-token'
    for _ in range(2):
        assert client.post(url, json=result).status_code == 200
    assert client.get('/api/payouts', headers=auth(buyer)).json['payouts'][0]['status'] == 'succeeded'
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '90.00'


def test_failed_payout_refunds_once_and_timeout_does_not_refund_unconfirmed_money(app, client, buyer, monkeypatch):
    funding(app, client, buyer, monkeypatch)
    payout = request(client, buyer).json['payout']
    url = '/api/payouts/timeout/' + payout['reference'] + '/test-callback-token'
    assert client.post(url, json={}).status_code == 200
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '90.00'
    url = '/api/payouts/result/' + payout['reference'] + '/test-callback-token'
    body = {'Result': {'ResultCode': 1, 'ConversationID': 'provider-conversation'}}
    for _ in range(2):
        assert client.post(url, json=body).status_code == 200
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '100.00'


def test_simulated_deposits_cannot_become_live_withdrawable_money(app, client, buyer):
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '100'})
    app.config['PAYMENT_MODE'] = 'daraja_live'
    response = client.post('/api/payouts', headers=auth(buyer), json={'amount': '100'})
    assert response.status_code == 503 and response.json['error']['code'] == 'live_database_required'
