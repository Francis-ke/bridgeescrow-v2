from app.models.merchant_api import CheckoutOrder
from tests.developer_flow_helpers import application


def test_idempotency_header_is_application_scoped_and_bound_to_original_request(client, seller):
    _, headers = application(client, seller)
    headers['Idempotency-Key'] = 'shop-request-100'
    payload = {'order_id': 'FIRST', 'items': [{'description': 'Package', 'quantity': 1, 'unit_amount': '100.00'}]}
    first = client.post('/api/v1/escrows', headers=headers, json=payload)
    assert first.status_code == 201
    second = client.post('/api/v1/escrows', headers=headers, json=payload)
    assert second.json['escrow']['id'] == first.json['escrow']['id']
    payload['order_id'] = 'DIFFERENT'
    assert client.post('/api/v1/escrows', headers=headers, json=payload).status_code == 409
    _, other_headers = application(client, seller, name='Another Shop')
    other_headers['Idempotency-Key'] = headers['Idempotency-Key']
    assert client.post('/api/v1/escrows', headers=other_headers, json=payload).status_code == 201
    assert CheckoutOrder.query.count() == 2
