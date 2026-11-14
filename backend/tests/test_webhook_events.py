import pytest
from app.core.db import db
from app.core.errors import ApiError
from app.models.webhook import WebhookDelivery, WebhookEndpoint
from app.services.developer.webhook_events import enqueue
from tests.webhook_helpers import endpoint


def test_events_are_atomic_idempotent_and_subscription_scoped(buyer):
    aid, eid, _ = endpoint(buyer, ['payment.pending'])
    enqueue(aid, 'payment.pending', {'order_id': 7}, event_id='event-one')
    db.session.rollback()
    assert WebhookDelivery.query.count() == 0
    first = enqueue(aid, 'payment.pending', {'order_id': 7}, event_id='event-one')
    db.session.commit()
    original_payload = first[0].payload
    again = enqueue(aid, 'payment.pending', {'order_id': 7}, event_id='event-one')
    db.session.commit()
    assert len(again) == 1 and WebhookDelivery.query.count() == 1
    assert again[0].payload == original_payload
    with pytest.raises(ApiError):
        enqueue(aid, 'payment.pending', {'order_id': 8}, event_id='event-one')
    assert enqueue(aid, 'escrow.released', {'order_id': 7}) == []
    db.session.get(WebhookEndpoint, eid).active = False
    db.session.commit()
    assert enqueue(aid, 'payment.pending', {'order_id': 9}) == []
