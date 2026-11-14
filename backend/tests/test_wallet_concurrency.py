from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from app.core.db import db
from app.models import Wallet, LedgerEntry
from tests.conftest import auth
from tests.protected_concurrency_helpers import seed


def race(app, buyer, path, bodies):
    barrier = Barrier(len(bodies))
    def send(body):
        barrier.wait(timeout=10)
        with app.test_client() as client:
            return client.post(path, headers=auth(buyer), json=body).status_code
    with ThreadPoolExecutor(max_workers=len(bodies)) as pool:
        return sorted(pool.map(send, bodies))


def test_concurrent_deposit_retries_credit_once(tmp_path):
    app, buyer, _, _ = seed(tmp_path)
    body = {'amount': '100', 'idempotency_key': 'simultaneous-deposit'}
    assert race(app, buyer, '/api/wallet/deposit', [body, body]) == [201, 201]
    with app.app_context():
        wallet = Wallet.query.filter_by(user_id=buyer['id']).one()
        assert wallet.available_cents == 110000
        assert LedgerEntry.query.filter_by(wallet_id=wallet.id, entry_type='deposit').count() == 2


def test_concurrent_withdrawals_cannot_overdraw(tmp_path):
    app, buyer, _, _ = seed(tmp_path)
    with app.test_client() as client:
        client.post('/api/auth/pin', headers=auth(buyer), json={'pin': '1234'})
    bodies = [{'amount': '700', 'pin': '1234', 'idempotency_key': f'withdraw-{i}'} for i in range(2)]
    assert race(app, buyer, '/api/wallet/withdraw', bodies) == [200, 409]
    with app.app_context():
        wallet = Wallet.query.filter_by(user_id=buyer['id']).one()
        assert wallet.available_cents == 30000
        assert LedgerEntry.query.filter_by(wallet_id=wallet.id, entry_type='withdrawal').count() == 1
