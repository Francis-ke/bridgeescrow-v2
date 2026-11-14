import uuid
from app.api.developer_webhook_routes import bp
from app.core.db import db
from app.core.decorators import login_required
from app.core.errors import ApiError
from app.models.mixins import utcnow
from app.models.webhook import WebhookDelivery
from app.services.developer.webhook_management import owned_endpoint, owned_delivery
from app.services.developer.applications import owned_app
from app.services.developer.webhook_claims import MAX_ATTEMPTS


@bp.post('/webhooks/<int:eid>/test')
@login_required
def test_endpoint(eid):
    endpoint = owned_endpoint(eid)
    app = owned_app(endpoint.app_id)
    if not endpoint.active or not app.active or app.environment != 'sandbox':
        raise ApiError('An active sandbox endpoint is required', 409, 'endpoint_unavailable')
    event_id = 'evt_' + uuid.uuid4().hex
    row = WebhookDelivery(endpoint_id=eid, event_id=event_id, event_type='payment.pending',
        payload={'id': event_id, 'type': 'payment.pending', 'created_at': utcnow().isoformat() + 'Z',
                 'data': {'test': True, 'application_id': app.public_id}}, next_attempt_at=utcnow())
    db.session.add(row)
    db.session.commit()
    return {'delivery': row.to_dict(), 'queued': True}, 202


@bp.get('/webhooks/<int:eid>/deliveries')
@login_required
def deliveries(eid):
    owned_endpoint(eid)
    rows = WebhookDelivery.query.filter_by(endpoint_id=eid).order_by(WebhookDelivery.id.desc()).limit(100).all()
    return {'deliveries': [row.to_dict() for row in rows]}


@bp.post('/webhook-deliveries/<int:did>/retry')
@login_required
def retry(did):
    row = owned_delivery(did)
    endpoint = owned_endpoint(row.endpoint_id)
    app = owned_app(endpoint.app_id)
    if not endpoint.active or not app.active:
        raise ApiError('An active endpoint is required', 409, 'endpoint_unavailable')
    if row.status not in ['retry', 'failed'] or row.attempts >= MAX_ATTEMPTS:
        raise ApiError('Delivery cannot be retried in its current state', 409, 'retry_unavailable')
    row.status, row.next_attempt_at = 'pending', utcnow()
    db.session.commit()
    return {'delivery': row.to_dict()}
