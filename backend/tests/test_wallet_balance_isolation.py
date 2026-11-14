from tests.conftest import auth
from tests.test_escrow import _funded


def test_available_and_escrow_balances_belong_to_each_account(client, buyer, seller, admin):
    escrow = _funded(client, buyer, seller)
    wallets = {user['id']: client.get('/api/wallet', headers=auth(user)).json['wallet']
               for user in (buyer, seller, admin)}
    assert wallets[buyer['id']]['escrow'] == '5000.00'
    assert wallets[seller['id']]['escrow'] == '0.00'
    assert wallets[seller['id']]['incoming_escrow'] == '4950.00'
    assert wallets[admin['id']]['available'] == '0.00'
    assert wallets[admin['id']]['incoming_escrow'] == '0.00'
    assert wallets[admin['id']]['escrow'] == '0.00'
    for user in (buyer, seller, admin):
        response = client.get('/api/wallet', headers=auth(user))
        assert response.json['wallet']['user_id'] == user['id']
        assert response.headers['Cache-Control'] == 'private, no-store'
    assert client.get('/api/wallet/ledger', headers=auth(admin)).json['entries'] == []
