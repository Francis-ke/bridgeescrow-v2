from datetime import timedelta
from app.models.mixins import utcnow
from .common import require, event
from . import ledger


def milestone(payment, data):
    mid = data.get('milestone_id')
    require(type(mid) is int, 'Choose an integer milestone identifier', 422)
    item = next((row for row in payment.milestones if row.id == mid), None)
    require(item is not None, 'Choose a valid milestone', 422)
    preceding = [row for row in payment.milestones if row.id < item.id]
    require(all(row.state == 'approved' for row in preceding), 'Complete earlier milestones first')
    return item


def text(data, key):
    value = data.get(key)
    require(isinstance(value, str) and 10 <= len(value.strip()) <= 10000,
            f'{key.replace("_", " ").capitalize()} needs 10–10000 characters', 422)
    return value.strip()


def submit(payment, uid, data):
    require(uid == payment.escrow.seller_id, 'Only the provider can submit work', 403)
    require(payment.category != 'booking', 'Use booking service confirmation')
    require(payment.state in ['funded', 'submitted', 'revision_requested'], 'Payment is not open for work')
    item = milestone(payment, data)
    require(item.state in ['pending', 'revision_requested'], 'This milestone cannot be submitted')
    require(utcnow() <= (item.revision_due_at or item.deadline_at), 'Deadline passed; request an extension')
    item.submission, item.submitted_at = text(data, 'submission'), utcnow()
    item.state, payment.state = 'submitted', 'submitted'
    payment.provider_confirmed_at = utcnow()
    event(payment, uid, 'work_submitted', item.title)


def revise(payment, uid, data):
    require(uid == payment.escrow.buyer_id, 'Only the client can request revisions', 403)
    require(payment.state == 'submitted', 'No submitted work to revise')
    item = milestone(payment, data)
    require(item.state == 'submitted', 'This milestone has no submitted work')
    require(item.revision_count < payment.rules['max_revisions'], 'Revision limit reached; approve or dispute')
    item.revision_reason = text(data, 'reason')
    item.revision_count += 1
    item.revision_due_at = utcnow() + timedelta(hours=payment.rules['revision_hours'])
    item.state, payment.state = 'revision_requested', 'revision_requested'
    event(payment, uid, 'revision_requested', item.revision_reason)


def approve(payment, uid, data):
    require(uid == payment.escrow.buyer_id, 'Only the client can approve work', 403)
    require(payment.category != 'booking' and payment.state == 'submitted', 'No submitted work to approve')
    item = milestone(payment, data)
    require(item.state == 'submitted', 'This milestone is not submitted')
    ledger.distribute(payment, item.amount_cents)
    item.state, item.approved_at = 'approved', utcnow()
    payment.client_confirmed_at = utcnow()
    if ledger.remaining(payment) == 0:
        payment.state, payment.escrow.status = 'completed', 'released'
    else:
        payment.state = 'funded'
    event(payment, uid, 'milestone_approved', item.title)
