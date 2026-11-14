from app.models.merchant_api import MerchantApiKey, CheckoutOrder
from tests.conftest import auth
from tests.integration_helpers import key


def test_seller_keys_are_private_hashed_and_revocable(client, buyer, seller):
    secret, kid = key(client, seller)
    stored = MerchantApiKey.query.filter_by(id=kid).one()
    assert stored.key_hash != secret and len(stored.key_hash) == 64
    listing = client.get('/api/seller/api', headers=auth(seller)).json
    assert secret not in str(listing) and listing['keys'][0]['prefix'] == secret[:12]
    assert client.delete(f'/api/seller/api/keys/{kid}', headers=auth(buyer)).status_code == 404
    assert client.delete(f'/api/seller/api/keys/{kid}', headers=auth(seller)).status_code == 200
    assert client.post('/api/integrations/orders', headers={'Authorization': 'Bearer ' + secret}, json={}).status_code == 401
    assert client.get('/api/seller/api').status_code == 401


def test_merchant_bill_is_immutable_and_order_creation_idempotent(client, seller):
    secret, _ = key(client, seller)
    headers = {'Authorization': 'Bearer ' + secret}
    payload = {'order_id': 'SHOP-42', 'items': [{'description': 'One item', 'quantity': 2, 'unit_amount': '50.25'}]}
    first = client.post('/api/integrations/orders', headers=headers, json=payload)
    assert first.status_code == 201
    assert first.json['order']['amount'] == '100.50'
    again = client.post('/api/integrations/orders', headers=headers, json=payload)
    assert first.json['order']['checkout_url'] == again.json['order']['checkout_url']
    payload['items'][0]['unit_amount'] = '60'
    assert client.post('/api/integrations/orders', headers=headers, json=payload).status_code == 409
    assert CheckoutOrder.query.count() == 1
    payload['order_id'] = 'SECOND'
    payload['return_url'] = 'javascript:alert(1)'
    assert client.post('/api/integrations/orders', headers=headers, json=payload).status_code == 422


def test_new_seller_receives_a_current_merchant_session(client, buyer):
    result = client.post('/api/seller/api/keys', headers=auth(buyer), json={
        'business_name': 'Buyer Shop', 'website': 'https://shop.example', 'contact_email': 'owner@example.com'})
    assert result.status_code == 201
    assert result.json['session']['user']['role'] == 'merchant'
    headers = {'Authorization': 'Bearer ' + result.json['session']['token']}
    assert client.get('/api/merchant/sales', headers=headers).status_code == 200
