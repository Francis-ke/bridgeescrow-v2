from app.core.db import db
from app.models import Wallet
from tests.conftest import auth


def balance(client, user):
    return client.get('/api/wallet', headers=auth(user)).json['wallet']['available']


def test_same_retry_key_is_independent_for_each_account(client, buyer, seller):
    for user, amount in ((buyer, '120'), (seller, '350')):
        body = {'amount': amount, 'idempotency_key': 'shared-client-key'}
        for _ in range(2):
            assert client.post('/api/wallet/deposit', headers=auth(user), json=body).status_code == 201
    assert balance(client, buyer) == '120.00'
    assert balance(client, seller) == '350.00'
    for user, cents in ((buyer, 12000), (seller, 35000)):
        entries = client.get('/api/wallet/ledger', headers=auth(user)).json['entries']
        assert len(entries) == 1 and entries[0]['amount_cents'] == cents
        assert Wallet.query.filter_by(user_id=user['id']).count() == 1


def test_money_persists_after_logout_and_new_login(client, buyer, seller):
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '250'})
    db.session.remove()
    session = client.post('/api/auth/login', json={
        'email': 'buyer@example.com', 'password': 'secret123'}).json
    assert session['wallet']['available'] == '250.00'
    assert balance(client, {'token': session['token']}) == '250.00'
    assert balance(client, seller) == '0.00'


def test_cannot_redirect_wallet_operations_to_another_account(client, buyer, seller):
    client.post('/api/wallet/deposit', headers=auth(buyer), json={
        'amount': '100', 'user_id': seller['id'], 'wallet_id': seller['id']})
    assert balance(client, buyer) == '100.00'
    assert balance(client, seller) == '0.00'
    result = client.get('/api/wallet', headers=auth(buyer))
    assert result.json['wallet']['user_id'] == buyer['id']


def test_retry_cannot_change_amount_and_withdrawal_always_requires_pin(client, buyer):
    body = {'amount': '100', 'idempotency_key': 'same-key'}
    client.post('/api/wallet/deposit', headers=auth(buyer), json=body)
    changed = client.post('/api/wallet/deposit', headers=auth(buyer),
                          json={**body, 'amount': '200'})
    assert changed.status_code == 409
    client.post('/api/auth/pin', headers=auth(buyer), json={'pin': '1234'})
    withdrawal = {**body, 'amount': '20', 'pin': '1234'}
    assert client.post('/api/wallet/withdraw', headers=auth(buyer), json=withdrawal).status_code == 200
    assert client.post('/api/wallet/withdraw', headers=auth(buyer),
                       json={**withdrawal, 'pin': '9999'}).status_code == 403
    assert balance(client, buyer) == '80.00'


def test_withdrawals_with_shared_keys_debit_only_the_owners(client, buyer, seller):
    for user in (buyer, seller):
        client.post('/api/auth/pin', headers=auth(user), json={'pin': '1234'})
        client.post('/api/wallet/deposit', headers=auth(user), json={'amount': '100'})
        body = {'amount': '30', 'pin': '1234', 'idempotency_key': 'shared-withdrawal'}
        for _ in range(2):
            assert client.post('/api/wallet/withdraw', headers=auth(user), json=body).status_code == 200
        assert balance(client, user) == '70.00'


def test_invalid_money_never_changes_wallet(client, buyer):
    for amount in ('NaN', 'Infinity', '-1', '0', '5000001'):
        result = client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': amount})
        assert result.status_code == 422
    assert balance(client, buyer) == '0.00'
