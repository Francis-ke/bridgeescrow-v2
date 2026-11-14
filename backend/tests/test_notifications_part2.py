from datetime import timedelta
from app.core.db import db
from app.models import Escrow
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.test_escrow import _funded





def test_read_all_is_private_and_preserves_messages(client, buyer, seller):
    _funded(client, buyer, seller)
    mine = client.get('/api/notifications', headers=auth(buyer)).json
    theirs = client.get('/api/notifications', headers=auth(seller)).json
    assert mine['unread_count'] > 0 and theirs['unread_count'] > 0
    assert client.put('/api/notifications/read-all').status_code == 401
    assert client.put('/api/notifications/read-all', headers=auth(buyer)).status_code == 200
    updated = client.get('/api/notifications', headers=auth(buyer)).json
    assert updated['unread_count'] == 0
    assert len(updated['notifications']) == len(mine['notifications'])
    assert client.get('/api/notifications', headers=auth(seller)).json['unread_count'] == theirs['unread_count']
    assert all(item['title'] and item['kind'] for item in updated['notifications'])
