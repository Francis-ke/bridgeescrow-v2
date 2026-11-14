import hashlib
import hmac
from datetime import timedelta
from app.core.db import db
from app.models.mixins import utcnow
from app.models.webhook import WebhookDelivery
from app.services.developer.webhook_events import enqueue
from app.services.developer.webhook_worker import deliver
from tests.webhook_helpers import endpoint
from tests.conftest import auth


def test_deliveries_are_signed_and_retries_keep_same_event_body(buyer, monkeypatch):
    aid, eid, secret = endpoint(buyer)
    enqueue(aid, 'payment.pending', {'order_id': 1}, event_id='event-stable')
    db.session.commit()
    calls = []
    def sender(url, body, headers):
        calls.append((body, headers))
        return 503 if len(calls) == 1 else 204
    monkeypatch.setattr('app.services.developer.webhook_secrets.time.time', lambda: 1000)
    assert deliver(sender=sender)['failed'] == 1
    row = WebhookDelivery.query.one()
    assert row.status == 'retry' and row.attempts == 1 and row.http_status == 503
    assert deliver(sender=sender)['attempted'] == 0
    row.next_attempt_at = utcnow() - timedelta(seconds=1)
    db.session.commit()
    monkeypatch.setattr('app.services.developer.webhook_secrets.time.time', lambda: 2000)
    assert deliver(sender=sender)['delivered'] == 1
    assert calls[0][0] == calls[1][0]
    for body, headers in calls:
        timestamp, signature = headers['BridgeEscrow-Signature'].split(',')
        timestamp, signature = timestamp[2:], signature[3:]
        expected = hmac.new(secret.encode(), timestamp.encode() + b'.' + body, hashlib.sha256).hexdigest()
        assert hmac.compare_digest(signature, expected)
        assert headers['BridgeEscrow-Event-Id'] == 'event-stable'
    assert calls[0][1]['BridgeEscrow-Signature'] != calls[1][1]['BridgeEscrow-Signature']
    assert WebhookDelivery.query.one().status == 'delivered'


def test_redirects_are_not_success_and_attempts_are_bounded(client, buyer):
    aid, eid, _ = endpoint(buyer)
    enqueue(aid, 'escrow.held', {'order_id': 1})
    db.session.commit()
    for _ in range(5):
        assert deliver(sender=lambda *args: 302)['failed'] == 1
        row = WebhookDelivery.query.one()
        if row.status == 'retry':
            row.next_attempt_at = utcnow() - timedelta(seconds=1)
            db.session.commit()
    row = WebhookDelivery.query.one()
    assert row.status == 'failed' and row.attempts == 5
    assert deliver(sender=lambda *args: 200)['attempted'] == 0
    assert client.post(f'/api/v1/developer/webhook-deliveries/{row.id}/retry', headers=auth(buyer)).status_code == 409
