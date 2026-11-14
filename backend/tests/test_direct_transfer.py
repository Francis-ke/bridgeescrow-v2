import uuid
from app.core.db import db
from app.models import User
from tests.conftest import auth
from tests.test_demo_checkout import execute


def test_send_credits_recipient_directly_and_retries_once(client, buyer, seller):
    from app.models import Escrow
    execute(client, buyer, 'deposit', '500')
    number = db.session.get(User, seller['id']).card_number
    key = str(uuid.uuid4())
    for _ in range(2):
        sent = execute(client, buyer, 'send', '100', recipient_card=number, idempotency_key=key)
        assert sent.status_code == 200
        assert sent.json['wallet']['available'] == '400.00'
        assert sent.json['wallet']['escrow'] == '0.00'
        assert sent.json['receipt']['escrow_id'] is None
    assert Escrow.query.count() == 0
    balance = client.get('/api/wallet', headers=auth(seller)).json['wallet']
    assert balance['available'] == '100.00'
    assert balance['incoming_escrow'] == '0.00'
    entries = client.get('/api/wallet/ledger', headers=auth(seller)).json['entries']
    assert len(entries) == 1 and entries[0]['direction'] == 'credit'
    assert client.get('/api/notifications', headers=auth(seller)).json['unread_count'] == 1


def test_direct_transfer_works_in_provider_mode_and_isolates_other_accounts(client, buyer, seller, admin, app):
    execute(client, buyer, 'deposit', '200')
    number = db.session.get(User, seller['id']).card_number
    app.config['PAYMENT_MODE'] = 'provider'
    sent = execute(client, buyer, 'send', '0.50', recipient_card=number)
    assert sent.status_code == 200
    assert sent.json['wallet']['available'] == '199.50'
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '0.50'
    assert client.get('/api/wallet', headers=auth(admin)).json['wallet']['available'] == '0.00'
    assert client.get('/api/wallet/ledger', headers=auth(admin)).json['entries'] == []
