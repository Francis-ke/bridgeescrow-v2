import uuid
import pytest
from app.models import User, DemoTransaction
from app.core.db import db
from tests.conftest import auth


def execute(client, user, kind, amount='100', **kwargs):
    return client.post('/api/payments/demo-checkout', headers=auth(user), json={
        'kind': kind, 'method': 'card', 'amount': amount,
        'idempotency_key': str(uuid.uuid4()), **kwargs})


def test_deposit_withdraw_and_retries_update_balances_once(client, buyer):
    key = str(uuid.uuid4())
    response = execute(client, buyer, 'deposit', '200', idempotency_key=key)
    assert response.status_code == 200
    assert response.json['wallet']['available'] == '200.00'
    receipt = response.json['receipt']
    assert receipt['demo'] is True
    replay = execute(client, buyer, 'deposit', '200', idempotency_key=key)
    assert replay.json['receipt']['reference'] == receipt['reference']
    assert replay.json['wallet']['available'] == '200.00'
    assert execute(client, buyer, 'deposit', '300', idempotency_key=key).status_code == 409
    assert execute(client, buyer, 'withdraw', '50').json['wallet']['available'] == '150.00'
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '150.00'
    entries = client.get('/api/wallet/ledger', headers=auth(buyer)).json['entries']
    assert len(entries) == 2
    assert {row['entry_type'] for row in entries} == {'deposit', 'withdrawal'}


def test_send_creates_funded_escrow_and_notifies_receiver(client, buyer, seller):
    execute(client, buyer, 'deposit', '500')
    number = db.session.get(User, seller['id']).card_number
    sent = execute(client, buyer, 'send', '100', recipient_card=number)
    assert sent.status_code == 200
    assert sent.json['wallet']['available'] == '400.00'
    assert sent.json['wallet']['escrow'] == '100.00'
    eid = sent.json['receipt']['escrow_id']
    received = client.get('/api/escrows?direction=received&view=progress', headers=auth(seller)).json['escrows']
    assert received[0]['id'] == eid and received[0]['status'] == 'funded'
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['incoming_escrow'] == '99.00'
    assert client.get('/api/notifications', headers=auth(seller)).json['unread_count'] == 1
    code = client.post(f'/api/escrows/{eid}/release', headers=auth(buyer)).json['demo_code']
    assert client.post(f'/api/escrows/{eid}/confirm', headers=auth(buyer), json={'code': code}).status_code == 200
    balance = client.get('/api/wallet', headers=auth(seller)).json['wallet']
    assert balance['available'] == '99.00'
    assert balance['incoming_escrow'] == '0.00'


def test_failed_payments_do_not_change_balance_or_leave_receipts(client, buyer, seller):
    number = db.session.get(User, seller['id']).card_number
    assert execute(client, buyer, 'withdraw', '100').status_code == 409
    assert execute(client, buyer, 'send', '100', recipient_card=number).status_code == 409
    assert DemoTransaction.query.count() == 0
    execute(client, buyer, 'deposit', '200')
    assert execute(client, buyer, 'send', '100', recipient_card='9900999999999999').status_code == 404
    own = db.session.get(User, buyer['id']).card_number
    assert execute(client, buyer, 'send', '100', recipient_card=own).status_code == 422
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '200.00'


def test_mpesa_purchases_and_deposits_reflect_on_account(client, buyer, seller):
    assert execute(client, buyer, 'deposit', '300', method='mpesa', destination='0712345678').status_code == 200
    purchase = execute(client, buyer, 'buy', '50', method='mpesa', destination='0799999999')
    assert purchase.status_code == 200 and purchase.json['wallet']['available'] == '250.00'
    internal = execute(client, buyer, 'buy', '100', method='mpesa', destination='+254722222222')
    assert internal.status_code == 200
    assert internal.json['receipt']['escrow_id'] is not None
    assert internal.json['wallet']['available'] == '150.00'
    assert internal.json['wallet']['escrow'] == '100.00'


def test_demo_checkout_rejects_invalid_data_and_card_secrets(client, buyer):
    for amount in ['0', '-1', 'NaN', 'Infinity', '1.234', '5000001']:
        assert execute(client, buyer, 'deposit', amount).status_code == 422
    assert execute(client, buyer, 'deposit', cvv='123').status_code == 422
    assert client.post('/api/payments/demo-checkout', json={}).status_code == 401
