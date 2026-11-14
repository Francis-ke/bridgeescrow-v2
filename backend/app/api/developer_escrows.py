from flask import Blueprint, request
from app.services.developer.authentication import authenticate
from app.services.developer.orders import new, scoped, describe
from app.services.developer.actions import dispute, release_request

bp = Blueprint('developer_escrows', __name__, url_prefix='/api/v1')


@bp.post('/escrows')
def create_escrow():
    application, _ = authenticate('escrow:write')
    order = new(application, request.get_json(silent=True) or {}, request.headers.get('Idempotency-Key', ''))
    return {'escrow': describe(order), 'checkout_session': {
        'url': describe(order)['checkout_url'], 'escrow_id': order.id, 'environment': 'sandbox'}}, 201


@bp.get('/escrows/<int:oid>')
def get_escrow(oid):
    application, _ = authenticate('escrow:read')
    return {'escrow': describe(scoped(application, oid))}


@bp.post('/escrows/<int:oid>/disputes')
def open_dispute(oid):
    application, _ = authenticate('dispute:write')
    order = scoped(application, oid, locked=True)
    row = dispute(order, application.user_id, request.get_json(silent=True) or {})
    return {'dispute': row.to_dict(), 'escrow': describe(order)}, 201


@bp.post('/escrows/<int:oid>/release-requests')
def request_release(oid):
    application, _ = authenticate('release:request')
    order = scoped(application, oid, locked=True)
    return release_request(application, order, request.get_json(silent=True) or {}), 202
