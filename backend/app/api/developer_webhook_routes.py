from flask import Blueprint, request
from app.core.decorators import login_required
from app.core.db import db
from app.models.webhook import WebhookEndpoint
from app.services.developer.applications import owned_app
from app.services.developer import webhook_management as management

bp = Blueprint('developer_webhooks', __name__, url_prefix='/api/v1/developer')


@bp.get('/apps/<app_id>/webhooks')
@login_required
def endpoints(app_id):
    app = owned_app(app_id)
    rows = WebhookEndpoint.query.filter_by(app_id=app.id).order_by(WebhookEndpoint.id.desc()).all()
    return {'webhooks': [row.to_dict() for row in rows]}


@bp.post('/apps/<app_id>/webhooks')
@login_required
def create_endpoint(app_id):
    row, secret = management.create(app_id, request.get_json(silent=True) or {})
    return {'webhook': row.to_dict(), 'signing_secret': secret}, 201


@bp.patch('/webhooks/<int:eid>')
@login_required
def update_endpoint(eid):
    return {'webhook': management.update(eid, request.get_json(silent=True) or {}).to_dict()}


@bp.post('/webhooks/<int:eid>/rotate-secret')
@login_required
def rotate_secret(eid):
    row, secret = management.rotate(eid)
    return {'webhook': row.to_dict(), 'signing_secret': secret}


from app.api import developer_webhook_actions  # noqa: E402,F401
