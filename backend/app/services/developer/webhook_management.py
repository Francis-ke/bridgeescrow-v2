from marshmallow import Schema, fields, validate
from app.core.db import db
from app.core.errors import ApiError
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from .applications import owned_app
from .webhook_events import EVENTS
from .webhook_urls import validate_url
from .webhook_secrets import issue


class EndpointSchema(Schema):
    url = fields.String(required=True, validate=validate.Length(min=1, max=500))
    events = fields.List(fields.String(validate=validate.OneOf(EVENTS)), required=True,
                         validate=validate.Length(min=1, max=6))
    active = fields.Boolean(load_default=True)


def owned_endpoint(eid):
    row = db.session.get(WebhookEndpoint, eid)
    if not row:
        raise ApiError('Webhook not found', 404, 'not_found')
    owned_app(row.app_id)
    return row


def create(app_id, body):
    app = owned_app(app_id)
    if app.environment != 'sandbox' or not app.active:
        raise ApiError('An active sandbox application is required', 409, 'application_unavailable')
    data = EndpointSchema().load(body)
    validate_url(data['url'])
    secret, encrypted = issue()
    row = WebhookEndpoint(app_id=app.id, secret_ciphertext=encrypted, **data)
    db.session.add(row)
    db.session.commit()
    return row, secret


def update(eid, body):
    row = owned_endpoint(eid)
    data = EndpointSchema(partial=True).load(body)
    if 'url' in data:
        validate_url(data['url'])
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return row


def rotate(eid):
    row = owned_endpoint(eid)
    secret, row.secret_ciphertext = issue()
    db.session.commit()
    return row, secret


def owned_delivery(did):
    row = db.session.get(WebhookDelivery, did)
    if not row:
        raise ApiError('Delivery not found', 404, 'not_found')
    owned_endpoint(row.endpoint_id)
    return row
