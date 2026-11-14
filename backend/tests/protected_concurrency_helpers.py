from app import create_app
from app.core.db import db
from tests.user_factory import _make
from tests.conftest import auth
from tests.protected_helpers import create, act


def seed(tmp_path, submit=False):
    app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'concurrent.sqlite'),
        'SQLALCHEMY_ENGINE_OPTIONS': {'connect_args': {'timeout': 10}}, 'TESTING': True})
    with app.app_context():
        db.create_all()
        client = app.test_client()
        buyer = _make(client, 'concurrent-buyer@example.com', '0711111111', 'Concurrent Buyer')
        seller = _make(client, 'concurrent-seller@example.com', '0722222222', 'Concurrent Seller')
        p = create(client, buyer, seller)
        act(client, buyer, p, 'accept')
        act(client, seller, p, 'accept')
        client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '1000'})
        if submit:
            p = act(client, buyer, p, 'fund')
            p = act(client, seller, p, 'submit', {'milestone_id': p['milestones'][0]['id'],
                                               'submission': 'Complete project ready for approval.'})
    return app, buyer, seller, p
