from app.core.db import db
from app.models import Dispute
from app.models.mixins import utcnow
from .common import load, require, event
from . import ledger


def resolve(dispute_id, uid, data):
    dispute = db.session.get(Dispute, dispute_id)
    require(dispute is not None, 'Dispute not found', 404)
    payment = load(dispute.escrow_id, uid, admin=True)
    require(dispute.status == 'open' and payment.state == 'disputed', 'Dispute is already resolved')
    reason = data.get('resolution', '')
    require(isinstance(reason, str) and 10 <= len(reason.strip()) <= 400,
            'Describe the resolution in 10–400 characters', 422)
    outcome = data.get('outcome', 'resume')
    require(outcome in ['resume', 'release', 'refund', 'split'], 'Choose a valid resolution', 422)
    if outcome == 'resume':
        payment.state = payment.pre_dispute_state or 'funded'
        payment.escrow.status = 'funded'
    else:
        percent = {'release': 0, 'refund': 100}.get(outcome, data.get('refund_percent'))
        require(type(percent) is int and 0 <= percent <= 100, 'Enter a refund percentage from 0 to 100', 422)
        amount = ledger.remaining(payment)
        ledger.distribute(payment, amount, refund=amount * percent // 100)
        payment.state = 'completed' if percent == 0 else 'cancelled'
        payment.escrow.status = 'released' if percent == 0 else 'refunded'
        for item in payment.milestones:
            if item.state != 'approved':
                item.state = 'approved' if percent == 0 else 'cancelled'
                item.approved_at = utcnow() if percent == 0 else None
    dispute.status, dispute.resolution = 'resolved', reason.strip()
    event(payment, uid, 'dispute_resolved', f'{outcome}: {reason.strip()}')
    db.session.commit()
    return dispute
