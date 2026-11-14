import pytest
from sqlalchemy.exc import IntegrityError
from app.core.db import db
from app.models import User
from tests.conftest import auth


def test_users_have_distinct_persistent_card_numbers(client, buyer, seller):
    first = client.get('/api/auth/me', headers=auth(buyer)).json['user']['card_number']
    second = client.get('/api/auth/me', headers=auth(seller)).json['user']['card_number']
    assert first != second
    assert all(len(value) == 16 and value.isdigit() for value in [first, second])
    assert first != '5399401212874821'
    assert client.get('/api/auth/me', headers=auth(buyer)).json['user']['card_number'] == first
    signed_in = client.post('/api/auth/login', json={
        'email': 'buyer@example.com', 'password': 'secret123'})
    assert signed_in.json['user']['card_number'] == first
    seller_user = db.session.get(User, seller['id'])
    seller_user.card_number = first
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_new_registration_gets_its_own_card(client):
    result = client.post('/api/auth/register', json={
        'full_name': 'Card Member', 'national_id': '88554422', 'email': 'card@example.com',
        'password': 'secret123', 'password_confirm': 'secret123'})
    assert result.status_code == 202
    verified = client.post('/api/auth/register/verify', json={
        'email': 'card@example.com', 'otp': client.mailbox['card@example.com'],
        'challenge_id': result.json['challenge_id']})
    number = verified.json['user']['card_number']
    assert len(number) == 16 and number.isdigit()
    assert User.query.filter_by(email='card@example.com').one().card_number == number


def test_card_cvv_is_individual_persistent_and_owner_only(client, buyer, seller, admin):
    first = client.get('/api/auth/me', headers=auth(buyer)).json['user']['card_cvv']
    second = client.get('/api/auth/me', headers=auth(seller)).json['user']['card_cvv']
    assert first != second
    assert len(first) == len(second) == 3
    assert first.isdigit() and second.isdigit()
    assert first != '942' and second != '942'
    again = client.post('/api/auth/login', json={
        'email': 'buyer@example.com', 'password': 'secret123'}).json
    assert again['user']['card_cvv'] == first
    users = client.get('/api/admin/users', headers=auth(admin)).json['users']
    assert all('card_cvv' not in user for user in users)
    created = client.post('/api/escrows', headers=auth(buyer), json={
        'seller_account': seller['account'], 'amount': '100', 'title': 'Private CVV test'}).json
    assert 'card_cvv' not in created['escrow']['transaction']['sender']
    assert 'card_cvv' not in created['escrow']['transaction']['recipient']
