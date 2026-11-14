from datetime import datetime, timedelta, timezone
from tests.conftest import auth


def stamp(days=7, hours=0):
    return (datetime.now(timezone.utc) + timedelta(days=days, hours=hours)).isoformat()


def payload(seller, category='freelancing', **updates):
    data = {'password': 'secret123', 'category': category, 'provider_id': seller['id'], 'title': 'Protected project',
        'description': 'Deliver the agreed project with all required documentation.',
        'amount': '100', 'deadline': stamp(7),
        'rules': {'cancellation_deadline': stamp(2), 'late_refund_percent': 0 if category == 'booking' else 80}}
    if category == 'booking':
        data.update(booking_start=stamp(4), booking_end=stamp(5))
    return {**data, **updates}


def create(client, buyer, seller, category='freelancing', **updates):
    response = client.post('/api/protected', json=payload(seller, category, **updates), headers=auth(buyer))
    assert response.status_code == 201, response.json
    return response.json['payment']


def act(client, user, payment, action, body=None, status=200):
    response = client.post(f'/api/protected/{payment["escrow"]["id"]}/{action}',
                           headers=auth(user), json=body or {})
    assert response.status_code == status, response.json
    return response.json.get('payment', response.json)


def funded(client, buyer, seller, category='freelancing', **updates):
    payment = create(client, buyer, seller, category, **updates)
    act(client, buyer, payment, 'accept')
    act(client, seller, payment, 'accept')
    result = client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '1000'})
    assert result.status_code == 201
    return act(client, buyer, payment, 'fund')


def balance(client, user):
    return client.get('/api/wallet', headers=auth(user)).json['wallet']
