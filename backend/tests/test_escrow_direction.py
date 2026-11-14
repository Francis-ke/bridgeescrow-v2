from tests.conftest import auth


def test_sent_and_received_are_scoped_to_current_user(client, buyer, seller, admin):
    def create(sender, recipient):
        result = client.post('/api/escrows', headers=auth(sender), json={
            'seller_account': recipient['account'], 'amount': '100', 'title': 'Direction test'})
        assert result.status_code == 201
        return result.json['escrow']['id']

    sent = create(buyer, seller)
    received = create(seller, buyer)
    unrelated = create(seller, admin)
    for user, sent_id, received_id in [(buyer, sent, received)]:
        for direction, expected in [('sent', sent_id), ('received', received_id)]:
            result = client.get(f'/api/escrows?direction={direction}', headers=auth(user))
            assert result.status_code == 200
            assert [row['id'] for row in result.json['escrows']] == [expected]
            assert unrelated not in [row['id'] for row in result.json['escrows']]
    all_rows = client.get('/api/escrows', headers=auth(buyer)).json['escrows']
    assert {row['id'] for row in all_rows} == {sent, received}
    assert client.get('/api/escrows?direction=invalid', headers=auth(buyer)).status_code == 422


def test_direction_requires_authentication(client):
    assert client.get('/api/escrows?direction=sent').status_code == 401
    assert client.get('/api/escrows?direction=received').status_code == 401


def test_received_progress_and_history_filter_status_and_ownership(client, buyer, seller, admin):
    from app.core.db import db
    from app.models import Escrow
    expected = {'progress': set(), 'history': set()}
    for status in ['hold', 'funded', 'disputed', 'released', 'refunded', 'cancelled']:
        response = client.post('/api/escrows', headers=auth(buyer), json={
            'seller_account': seller['account'], 'amount': '100', 'title': f'{status} filter test'})
        assert response.status_code == 201
        eid = response.json['escrow']['id']
        row = db.session.get(Escrow, eid)
        row.status = status
        db.session.commit()
        expected['progress' if status in ['hold', 'funded', 'disputed'] else 'history'].add(eid)
    # Another recipient's escrow must never appear in either list.
    unrelated = client.post('/api/escrows', headers=auth(buyer), json={
        'seller_account': admin['account'], 'amount': '100', 'title': 'Unrelated payment'})
    assert unrelated.status_code == 201
    for view, expected_ids in expected.items():
        result = client.get(f'/api/escrows?direction=received&view={view}', headers=auth(seller))
        assert result.status_code == 200
        assert {row['id'] for row in result.json['escrows']} == expected_ids
    invalid = client.get('/api/escrows?direction=received&view=wrong', headers=auth(seller))
    assert invalid.status_code == 422
    assert invalid.json['error']['code'] == 'invalid_view'
    assert client.get('/api/escrows?direction=received&view=history').status_code == 401
