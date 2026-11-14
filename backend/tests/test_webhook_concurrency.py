from concurrent.futures import ThreadPoolExecutor
from threading import Event
from app import create_app
from app.core.db import db
from app.models.webhook import WebhookDelivery
from app.services.developer.webhook_events import enqueue
from app.services.developer.webhook_worker import deliver
from tests.user_factory import _make
from tests.webhook_helpers import endpoint


def test_two_workers_cannot_deliver_the_same_attempt(tmp_path):
    app = create_app({'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'webhooks.sqlite'),
        'SQLALCHEMY_ENGINE_OPTIONS': {'connect_args': {'timeout': 10}}})
    with app.app_context():
        db.create_all()
        buyer = _make(app.test_client(), 'webhook@example.com', '0712345678', 'Webhook Owner')
        aid, _, _ = endpoint(buyer)
        enqueue(aid, 'payment.pending', {'order_id': 1})
        db.session.commit()
    started, finish = Event(), Event()
    calls = []
    def sender(*args):
        calls.append(args)
        started.set()
        assert finish.wait(timeout=5)
        return 204
    def worker():
        with app.app_context():
            return deliver(sender=sender)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(worker)
        assert started.wait(timeout=5)
        second = pool.submit(worker)
        assert second.result(timeout=5)['attempted'] == 0
        finish.set()
        assert first.result(timeout=5)['delivered'] == 1
    assert len(calls) == 1
    with app.app_context():
        row = WebhookDelivery.query.one()
        assert row.status == 'delivered' and row.attempts == 1
