from tests.conftest import auth


def test_web_withdrawals_obey_shared_pin_lockout(client, buyer):
    headers = auth(buyer)
    client.post('/api/auth/pin', headers=headers, json={'pin': '1234'})
    client.post('/api/wallet/deposit', headers=headers, json={'amount': '100'})
    for _ in range(5):
        response = client.post('/api/wallet/withdraw', headers=headers,
                               json={'amount': '10', 'pin': '9999'})
        assert response.status_code == 403
    locked = client.post('/api/wallet/withdraw', headers=headers,
                         json={'amount': '10', 'pin': '1234'})
    assert locked.status_code == 429
    assert client.get('/api/wallet', headers=headers).json['wallet']['available'] == '100.00'
