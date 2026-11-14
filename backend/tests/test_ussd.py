import re
from app.core.db import db
from app.models import User
from tests.conftest import auth
from tests.phone_helpers import verify_phone


def ready(client, user, phone):
    verify_phone(client, user, phone)
    assert client.post('/api/auth/pin', json={'pin': '1234'}, headers=auth(user)).status_code == 200


def dial(client, user, text='', session='test-session-001'):
    response = client.post('/api/ussd/simulate', json={'session_id': session, 'text': text}, headers=auth(user))
    assert response.status_code == 200, response.json
    return response.json['reply']


def test_first_dial_and_balance_require_verified_phone_and_pin(client, buyer):
    assert client.post('/api/ussd/simulate', json={'session_id': 'session-001'}, headers=auth(buyer)).status_code == 403
    ready(client, buyer, '0711111111')
    assert 'transaction PIN' in dial(client, buyer)
    assert 'Check balance' in dial(client, buyer, '1234')
    client.post('/api/wallet/deposit', json={'amount': '750'}, headers=auth(buyer))
    assert '750.00' in dial(client, buyer, '1234*1')


def test_public_gateway_fails_closed_and_sessions_cannot_change_phones(app, client, buyer, seller):
    assert client.post('/api/ussd', data={'phoneNumber': '0711111111'}).status_code == 401
    ready(client, buyer, '0711111111')
    ready(client, seller, '0722222222')
    app.config['USSD_CALLBACK_TOKEN'] = 'test-gateway-token'
    for user in User.query.filter(User.id.in_([buyer['id'], seller['id']])):
        user.phone_verification_source = 'africastalking_live'
    db.session.commit()
    url = '/api/ussd/gateway/test-gateway-token'
    data = {'phoneNumber': '+254711111111', 'sessionId': 'gateway-1', 'text': ''}
    assert client.post(url, data=data).get_data(as_text=True).startswith('CON')
    data['phoneNumber'] = '+254722222222'
    assert 'mismatch' in client.post(url, data=data).get_data(as_text=True)


def test_send_and_release_share_wallet_and_replayed_send_does_not_double_debit(client, buyer, seller):
    ready(client, buyer, '0711111111')
    client.post('/api/wallet/deposit', json={'amount': '3000'}, headers=auth(buyer))
    text = f"1234*2*{seller['account']}*1200*Shoes"
    first = dial(client, buyer, text)
    assert 'Funds protected' in first and dial(client, buyer, text) == first
    escrows = client.get('/api/escrows', headers=auth(buyer)).json['escrows']
    assert len(escrows) == 1 and escrows[0]['status'] == 'funded'
    reference = escrows[0]['reference']
    assert 'Release code sent' in dial(client, buyer, '1234*3*' + reference, 'release-session')
    messages = client.get('/api/phone/messages', headers=auth(buyer)).json['messages']
    code = re.search(r'release code (\d{6})', messages[0]['body']).group(1)
    assert 'Payment released' in dial(client, buyer, f'1234*3*{reference}*{code}', 'release-session')
    assert client.get('/api/wallet', headers=auth(seller)).json['wallet']['available'] == '1188.00'


def test_pin_attempts_are_locked_across_sessions(client, buyer):
    ready(client, buyer, '0711111111')
    for index in range(5):
        response = client.post('/api/ussd/simulate', json={'session_id': f'bad-pin-session-{index}', 'text': '0000'}, headers=auth(buyer))
        assert response.status_code == 403
    response = client.post('/api/ussd/simulate', json={'session_id': 'correct-but-locked', 'text': '1234'}, headers=auth(buyer))
    assert response.status_code == 429
