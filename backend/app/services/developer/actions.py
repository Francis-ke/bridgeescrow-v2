from marshmallow import Schema, fields, validate
from app.core.db import db
from app.models import Dispute
from app.models.protected_payment import ProtectedEvent
from app.services.protected.common import require, event
from app.services.protected.disputes import open_dispute
from app.services.notifications import add
from .orders import protected


class RequestSchema(Schema):
    reason = fields.String(load_default='', validate=validate.Length(max=400))


def release_request(application, order, payload):
    data = RequestSchema().load(payload)
    payment = protected(order)
    require(payment.escrow.status == 'funded', 'Only held payments can request release')
    previous = ProtectedEvent.query.filter_by(payment_id=payment.id, action='release_requested').first()
    if not previous:
        event(payment, application.user_id, 'release_requested', data['reason'])
        add(order.buyer_id, None, f'dev-release-request-{order.id}',
            'The seller requested release. Open your checkout link to confirm completion or raise a dispute.')
    db.session.commit()
    return {'status': 'awaiting_buyer_confirmation', 'escrow_id': order.id,
            'message': 'Buyer confirmation is required. No funds have been released.'}


def dispute(order, actor_id, payload):
    data = RequestSchema().load(payload)
    require(len(data['reason'].strip()) >= 10, 'Describe the problem in at least 10 characters', 422)
    payment = protected(order)
    previous = Dispute.query.filter_by(escrow_id=payment.escrow_id, status='open').first()
    if previous:
        require(previous.raised_by == actor_id and previous.reason == data['reason'].strip(), 'A dispute is already open')
        return previous
    row = open_dispute(payment, actor_id, data)
    db.session.commit()
    return row
