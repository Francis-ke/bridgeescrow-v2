from tests.conftest import auth
from tests.integration_helpers import checkout_mailbox, delivery_code
from tests.developer_flow_helpers import application, bill, buyer_session


def test_developer_key_requires_buyer_delivery_code_and_correct_application(client, buyer, seller, checkout_mailbox):
    appid, headers = application(client, seller)
    otherid, other = application(client, seller, name='Another App')
    order, _ = bill(client, headers)
    url, scope = buyer_session(client, order, checkout_mailbox)
    assert client.post(url + '/pay', headers=scope, json={'last4': '1234'}).status_code == 200
    code = delivery_code(checkout_mailbox)
    endpoint = f'/api/v1/escrows/{order["id"]}/delivery-confirmations'
    assert client.post(endpoint, headers=headers, json={}).status_code == 422
    assert client.post(endpoint, headers=headers, json={'code': 'wrong'}).status_code == 422
    assert client.post(endpoint, headers=other, json={'code': code}).status_code == 404
    dashboard = f'/api/v1/developer/apps/{appid}/escrows/{order["id"]}/delivery-confirmations'
    assert client.post(dashboard, headers=auth(buyer), json={'code': code}).status_code == 404
    assert client.post(endpoint, headers=headers, json={'code': code}).json['escrow']['state'] == 'RELEASED'
    assert client.post(endpoint, headers=headers, json={'code': code}).json['escrow']['state'] == 'RELEASED'
