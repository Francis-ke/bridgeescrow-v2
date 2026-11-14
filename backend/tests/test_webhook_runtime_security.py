import socket
import pytest
from app.core.db import db
from app.models.webhook import WebhookDelivery, WebhookEndpoint
from app.services.developer.webhook_events import enqueue
from app.services.developer.webhook_worker import deliver
from app.services.developer.webhook_socket import DeadlineSocket
from tests.webhook_helpers import endpoint


def test_delivery_revalidates_dns_to_block_rebinding(buyer, monkeypatch):
    aid, _, _ = endpoint(buyer)
    enqueue(aid, 'payment.pending', {'order_id': 1})
    db.session.commit()
    monkeypatch.setattr('app.services.developer.webhook_urls.socket.getaddrinfo',
        lambda *a, **k: [(2, 1, 6, '', ('169.254.169.254', 443))])
    def forbidden(*args, **kwargs):
        raise AssertionError('Private destination must never be connected')
    monkeypatch.setattr('app.services.developer.webhook_transport.socket.socket', forbidden)
    assert deliver()['failed'] == 1
    assert WebhookDelivery.query.one().error == 'Delivery failed (ApiError)'


def test_disabled_endpoint_never_sends_queued_events(buyer):
    aid, eid, _ = endpoint(buyer)
    enqueue(aid, 'payment.pending', {'order_id': 1})
    db.session.get(WebhookEndpoint, eid).active = False
    db.session.commit()
    def forbidden(*args):
        raise AssertionError('Disabled endpoint must not receive messages')
    assert deliver(sender=forbidden)['skipped'] == 1
    assert WebhookDelivery.query.one().status == 'cancelled'


def test_response_reads_have_an_absolute_deadline(monkeypatch):
    monkeypatch.setattr('app.services.developer.webhook_socket.time.monotonic', lambda: 11)
    wrapped = DeadlineSocket(object(), 10)
    with pytest.raises(socket.timeout):
        wrapped.remaining()
