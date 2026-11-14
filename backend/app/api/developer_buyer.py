from flask import request
from app.core.db import db
from app.models import Escrow
from app.services.integration_common import lock_order, require
from app.services.checkout_session import authorize
from app.services.checkout_settlement import complete
from app.services.protected.common import load
from app.services.developer.checkout import ensure_active, failure
from app.services.developer.actions import dispute
from app.api.checkout_routes import bp


def verified_order(token):
    order = lock_order(token=token)
    require(order.developer_application_id is not None, 'Sandbox checkout not found', 404)
    _, buyer = authorize(order)
    return order, buyer


@bp.post('/<token>/confirm')
def confirm_completion(token):
    order, buyer = verified_order(token)
    if order.state == 'completed':
        return {'state': 'completed', 'escrow_id': order.escrow_id}
    ensure_active(order)
    require(order.buyer_id == buyer.id and order.state == 'paid', 'Only the verified paying buyer can confirm')
    escrow = db.session.get(Escrow, order.escrow_id)
    payment = load(escrow.id, escrow.buyer_id)
    require(payment.state == 'funded' and payment.escrow.status == 'funded', 'Disputed payments cannot be released')
    return complete(order, payment, buyer.id)


@bp.post('/<token>/sandbox-failure')
def simulate_failure(token):
    order, buyer = verified_order(token)
    return failure(order, buyer, request.get_json(silent=True) or {})


@bp.post('/<token>/dispute')
def buyer_dispute(token):
    order, buyer = verified_order(token)
    require(order.buyer_id == buyer.id, 'Only the paying buyer can dispute this payment', 403)
    row = dispute(order, buyer.id, request.get_json(silent=True) or {})
    return {'dispute': row.to_dict()}, 201
