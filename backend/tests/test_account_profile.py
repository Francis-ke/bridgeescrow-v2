from tests.conftest import auth


def test_profile_updates_only_current_account(client, buyer, seller):
    before = client.get('/api/auth/me', headers=auth(seller)).json['user']
    response = client.put('/api/auth/me', headers=auth(buyer),
                          json={'full_name': '  Updated Buyer  '})
    assert response.status_code == 200
    assert response.json['user']['full_name'] == 'Updated Buyer'
    own = client.get('/api/auth/me', headers=auth(buyer)).json['user']
    assert own['full_name'] == 'Updated Buyer'
    assert own['account_number'] == buyer['account']
    assert client.get('/api/auth/me', headers=auth(seller)).json['user'] == before


def test_profile_requires_login(client):
    assert client.put('/api/auth/me', json={'full_name': 'New Name'}).status_code == 401


def test_profile_rejects_invalid_and_protected_fields(client, buyer):
    for data in ({'full_name': '   '}, {}, {'full_name': 'x'},
                 {'full_name': 'New Name', 'role': 'admin'},
                 {'full_name': 'New Name', 'id': 999}):
        assert client.put('/api/auth/me', headers=auth(buyer), json=data).status_code == 422
