import uuid
import re
from app.core.db import db
from app.core.errors import ApiError
from app.models.mixins import utcnow
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from .webhook_secrets import canonical

EVENTS = ('payment.pending', 'payment.failed', 'escrow.held',
          'escrow.released', 'escrow.disputed', 'escrow.refunded')


def enqueue(application_id, event_type, data, event_id=None):
    from app.models.developer_application import DeveloperApplication
    app = db.session.get(DeveloperApplication, application_id)
    if not app or not app.active:
        return []
    if event_type not in EVENTS or not isinstance(data, dict):
        raise ApiError('Unsupported webhook event', 422, 'invalid_webhook_event')
    event_id = event_id or 'evt_' + uuid.uuid4().hex
    if not isinstance(event_id, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}', event_id):
        raise ApiError('Invalid webhook event identifier', 422, 'invalid_event_id')
    existing = WebhookDelivery.query.join(WebhookEndpoint).filter(
        WebhookEndpoint.app_id == application_id, WebhookDelivery.event_id == event_id).first()
    payload = {'id': event_id, 'type': event_type,
               'created_at': utcnow().isoformat() + 'Z', 'data': data}
    canonical(payload)
    if existing:
        if existing.event_type != event_type or existing.payload['data'] != data:
            raise ApiError('Event identifier already used', 409, 'webhook_event_conflict')
        payload = existing.payload
    deliveries = []
    for endpoint in WebhookEndpoint.query.filter_by(app_id=application_id, active=True):
        if event_type not in endpoint.events:
            continue
        row = WebhookDelivery.query.filter_by(endpoint_id=endpoint.id, event_id=event_id).first()
        if not row:
            row = WebhookDelivery(endpoint_id=endpoint.id, event_id=event_id,
                event_type=event_type, payload=payload, next_attempt_at=utcnow())
            db.session.add(row)
        deliveries.append(row)
    return deliveries
