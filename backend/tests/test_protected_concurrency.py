from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import func, case
from app.core.db import db
from app.models import LedgerEntry, Wallet
from tests.conftest import auth
from tests.protected_concurrency_helpers import seed


def race(app, buyer, payment, action, body):
    barrier = Barrier(2)
    def request(_):
        barrier.wait(timeout=10)
        with app.test_client() as client:
            return client.post(f'/api/protected/{payment["escrow"]["id"]}/{action}',
                               headers=auth(buyer), json=body).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        return sorted(executor.map(request, range(2)))


def test_simultaneous_funding_does_not_double_debit(tmp_path):
    app, buyer, seller, p = seed(tmp_path)
    assert race(app, buyer, p, 'fund', {}) == [200, 409]
    with app.app_context():
        wallet = Wallet.query.filter_by(user_id=buyer['id']).one()
        assert wallet.available_cents == 90000 and wallet.escrow_cents == 10000
        assert LedgerEntry.query.filter_by(escrow_id=p['escrow']['id'], entry_type='hold').count() == 2


def test_simultaneous_approval_cannot_pay_twice(tmp_path):
    app, buyer, seller, p = seed(tmp_path, submit=True)
    assert race(app, buyer, p, 'approve', {'milestone_id': p['milestones'][0]['id']}) == [200, 409]
    with app.app_context():
        assert Wallet.query.filter_by(user_id=seller['id']).one().available_cents == 9900
        assert Wallet.query.filter_by(user_id=buyer['id']).one().escrow_cents == 0
        rows = db.session.query(LedgerEntry.batch_reference, func.sum(case(
            (LedgerEntry.direction == 'debit', LedgerEntry.amount_cents), else_=-LedgerEntry.amount_cents)))
        assert all(total == 0 for _, total in rows.filter(LedgerEntry.batch_reference.isnot(None)).group_by(LedgerEntry.batch_reference))


def test_simultaneous_overlapping_reservations_cannot_both_confirm(tmp_path):
    from tests.protected_helpers import create
    app, buyer, seller, _ = seed(tmp_path)
    with app.app_context():
        client = app.test_client()
        payments = [create(client, buyer, seller, 'booking') for _ in range(2)]
    barrier = Barrier(2)
    def reserve(index):
        barrier.wait(timeout=10)
        with app.test_client() as client:
            return client.post(f'/api/protected/{payments[index]["escrow"]["id"]}/accept',
                               headers=auth(seller), json={}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(reserve, range(2))) == [200, 409]
