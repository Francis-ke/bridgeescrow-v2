from tests.conftest import auth
from tests.developer_helpers import setup, create


def test_app_creation_listing_editing_and_ownership(app):
    client, owner, other = setup(app)
    application = create(client, owner)
    second = create(client, owner, name='Mobile Companion', type='mobile', website='')
    assert application['app_id'] != second['app_id']
    assert application['environment'] == 'sandbox'
    rows = client.get('/api/v1/developer/apps', headers=auth(owner)).json['applications']
    assert len(rows) == 2
    assert client.get('/api/v1/developer/apps', headers=auth(other)).json['applications'] == []
    path = f'/api/v1/developer/apps/{application["app_id"]}'
    assert client.get(path, headers=auth(other)).status_code == 404
    assert client.patch(path, headers=auth(other), json={'active': False}).status_code == 404
    edited = client.patch(path, headers=auth(owner), json={'name': 'Updated Shop', 'active': False})
    assert edited.status_code == 200 and edited.json['application']['active'] is False
    assert edited.json['application']['name'] == 'Updated Shop'
    assert edited.json['application']['description'] == application['description']


def test_app_validation_and_authenticated_creation(app):
    client, owner, _ = setup(app)
    assert client.get('/api/v1/developer/apps').status_code == 401
    original = {'name': 'Example Shop', 'description': 'A meaningful description.', 'type': 'website'}
    for changes in [{'environment': 'production'}, {'type': 'desktop'}, {'website': 'javascript:alert(1)'}, {'website': 'https://['},
                    {'name': '   '}, {'description': '          '}, {'active': 'false'}]:
        response = client.post('/api/v1/developer/apps', headers=auth(owner), json={**original, **changes})
        assert response.status_code == 422, response.json


def test_application_owner_and_order_recipient_are_bound_to_secret_key(app):
    from app.models.merchant_api import CheckoutOrder
    from tests.developer_helpers import key, api_auth
    client, owner, other = setup(app)
    application = create(client, owner)
    assert application['owner'] == {'name': 'Developer Owner', 'account_number': owner['account']}
    headers = api_auth(key(client, owner, application)['secret_key'])
    payload = {'order_id': 'OWNER-LINK', 'items': [
        {'description': 'Website purchase', 'quantity': 1, 'unit_amount': '100.00'}]}
    response = client.post('/api/v1/escrows', headers=headers, json=payload)
    assert response.status_code == 201
    with app.app_context():
        order = CheckoutOrder.query.filter_by(id=response.json['escrow']['id']).one()
        assert order.seller_id == owner['id']
        assert order.developer_application_id == application['id']
        assert order.seller_snapshot['name'] == application['name']
    for field in ['seller_id', 'user_id', 'account_number']:
        value = other['account'] if field == 'account_number' else other['id']
        assert client.post('/api/v1/escrows', headers=headers,
                           json={**payload, field: value}).status_code == 422
    assert client.patch(f'/api/v1/developer/apps/{application["id"]}', headers=auth(owner),
                        json={'user_id': other['id']}).status_code == 422
