from app.models import User
from app.core.db import db
from tests.conftest import auth


def test_delivery_uses_receiving_card_without_account_password(client, buyer, seller):
    provider = db.session.get(User, seller['id'])
    response = client.post('/api/protected/delivery', headers=auth(buyer), json={
        'recipient_card': provider.card_number, 'account_holder': provider.full_name,
        'duration_hours': 24, 'amount': '300'})
    assert response.status_code == 201
    payment = response.json['payment']
    assert payment['escrow']['transaction']['recipient']['id'] == seller['id']
    assert payment['escrow']['amount'] == '300.00'
    assert payment['state'] == 'awaiting_acceptance'


def test_delivery_validates_receiver_card_and_name(client, buyer, seller):
    provider = db.session.get(User, seller['id'])
    body = {'recipient_card': provider.card_number, 'account_holder': 'Wrong name',
            'duration_hours': 24, 'amount': '300'}
    assert client.post('/api/protected/delivery', headers=auth(buyer), json=body).status_code == 422
    body.update(recipient_card='9900999999999999', account_holder=provider.full_name)
    assert client.post('/api/protected/delivery', headers=auth(buyer), json=body).status_code == 404
    body.update(recipient_card=db.session.get(User, buyer['id']).card_number, account_holder='Brian Buyer')
    assert client.post('/api/protected/delivery', headers=auth(buyer), json=body).status_code == 422
