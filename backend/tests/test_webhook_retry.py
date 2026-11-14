from app.core.db import db
from app.models.webhook import WebhookDelivery
from app.services.developer.webhook_events import enqueue
from app.services.developer.webhook_worker import deliver
from tests.conftest import auth
from tests.webhook_helpers import endpoint


def test_owner_can_retry_due_failure_without_resetting_attempt_count(client, buyer, seller):
    aid, _, _ = endpoint(buyer)
    enqueue(aid, 'payment.pending', {'order_id': 1})
    db.session.commit()
    deliver(sender=lambda *args: 500)
    row = WebhookDelivery.query.one()
    did = row.id
    route = f'/api/v1/developer/webhook-deliveries/{did}/retry'
    assert client.post(route, headers=auth(seller)).status_code == 404
    result = client.post(route, headers=auth(buyer))
    assert result.status_code == 200
    assert result.json['delivery']['attempts'] == 1
    assert result.json['delivery']['status'] == 'pending'
    assert deliver(sender=lambda *args: 200)['delivered'] == 1
    assert WebhookDelivery.query.one().attempts == 2
