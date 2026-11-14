import re
from tests.conftest import auth


def verify_phone(client, user, number):
    response = client.post('/api/phone/verification', json={'phone': number}, headers=auth(user))
    assert response.status_code == 202, response.json
    messages = client.get('/api/phone/messages', headers=auth(user)).json['messages']
    code = re.search(r'code: (\d{6})', messages[0]['body']).group(1)
    verified = client.post('/api/phone/verify', json={'challenge_id': response.json['challenge_id'], 'otp': code}, headers=auth(user))
    assert verified.status_code == 200, verified.json
    return verified.json['user']
