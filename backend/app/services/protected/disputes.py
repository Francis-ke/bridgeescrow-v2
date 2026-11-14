from app.core.db import db
from app.models import Dispute
from .common import require, event
from .work import text


def open_dispute(payment, uid, data):
    require(payment.escrow.status == 'funded', 'Only secured funds can be disputed')
    require(not Dispute.query.filter_by(escrow_id=payment.escrow_id, status='open').with_for_update().first(),
            'A dispute is already open')
    reason = text(data, 'reason')
    require(len(reason) <= 400, 'Dispute reason must be at most 400 characters', 422)
    row = Dispute(escrow_id=payment.escrow_id, raised_by=uid, reason=reason)
    db.session.add(row)
    payment.pre_dispute_state = payment.state
    payment.state, payment.escrow.status = 'disputed', 'disputed'
    event(payment, uid, 'dispute_opened', reason)
    return row
