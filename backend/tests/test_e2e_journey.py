from app.core.db import db
from app.models import User
from tests.conftest import auth
from tests.user_factory import _make
from tests.test_demo_checkout import execute


def balance(client, user):
    return client.get('/api/wallet', headers=auth(user)).json['wallet']


def test_three_account_direct_transfer_and_notification_isolation(client, buyer, seller):
    user_c = _make(client, 'charlie@example.com', '0744444444', 'Charlie Customer')
    assert balance(client, buyer)['available'] == '0.00'
    assert balance(client, seller)['available'] == '0.00'
    assert balance(client, user_c)['available'] == '0.00'

    execute(client, buyer, 'deposit', '1000')
    assert balance(client, buyer)['available'] == '1000.00'
    assert balance(client, seller)['available'] == '0.00'
    assert balance(client, user_c)['available'] == '0.00'

    seller_card = db.session.get(User, seller['id']).card_number
    sent = execute(client, buyer, 'send', '200', recipient_card=seller_card)
    assert sent.status_code == 200

    assert balance(client, buyer)['available'] == '800.00'
    assert balance(client, seller)['available'] == '200.00'
    assert balance(client, user_c)['available'] == '0.00'

    buyer_notes = client.get('/api/notifications', headers=auth(buyer)).json['notifications']
    seller_notes = client.get('/api/notifications', headers=auth(seller)).json['notifications']
    user_c_notes = client.get('/api/notifications', headers=auth(user_c)).json['notifications']

    assert any('200' in n['message'] for n in seller_notes)
    assert len(user_c_notes) == 0

    buyer_ledger = client.get('/api/wallet/ledger', headers=auth(buyer)).json['entries']
    seller_ledger = client.get('/api/wallet/ledger', headers=auth(seller)).json['entries']
    user_c_ledger = client.get('/api/wallet/ledger', headers=auth(user_c)).json['entries']

    assert len(buyer_ledger) == 2
    assert len(seller_ledger) == 1 and seller_ledger[0]['direction'] == 'credit'
    assert len(user_c_ledger) == 0
