import re
from tests.conftest import auth


def application(client, user, name='Checkout App'):
    response = client.post('/api/v1/developer/apps', headers=auth(user), json={
        'name': name, 'description': 'Website checkout integration', 'type': 'website', 'environment': 'sandbox'})
    assert response.status_code == 201, response.json
    appid = response.json['application']['id']
    response = client.post(f'/api/v1/developer/apps/{appid}/keys', headers=auth(user), json={})
    assert response.status_code == 201, response.json
    return appid, {'Authorization': 'Bearer ' + response.json['secret_key']}


def bill(client, headers, reference='DEV-1'):
    payload = {'order_id': reference, 'items': [{'description': 'Package', 'quantity': 1, 'unit_amount': '100.00'}]}
    response = client.post('/api/v1/escrows', headers=headers, json=payload)
    assert response.status_code == 201, response.json
    return response.json['escrow'], payload


def buyer_session(client, order, messages, email='buyer@example.com'):
    token = order['checkout_url'].rsplit('/', 1)[-1]
    url = '/api/checkout/' + token
    response = client.post(url + '/request-otp', json={'email': email, 'full_name': 'Verified Buyer',
        'phone': '0712345678', 'address': 'Nairobi delivery address'})
    assert response.status_code == 200, response.json
    code = re.search(r'OTP is (\d{6})', messages[-1][2]).group(1)
    response = client.post(url + '/verify', json={'challenge_id': response.json['challenge_id'], 'otp': code})
    assert response.status_code == 200, response.json
    return url, {'X-Checkout-Session': response.json['session_token']}
