from datetime import datetime, timedelta
from app.models.mixins import utcnow
from .common import require, utc, event, booking_available
from .work import text


def request(payment, uid, data):
    require(payment.state not in ['completed', 'cancelled', 'disputed'], 'Extension unavailable in this state')
    require(not payment.extension or payment.extension['status'] != 'pending', 'An extension is already pending')
    try:
        deadline = utc(datetime.fromisoformat(data.get('deadline', '').replace('Z', '+00:00')))
    except (ValueError, TypeError, AttributeError):
        require(False, 'Enter an ISO date and timezone', 422)
    require(deadline > max(payment.deadline_at, utcnow()), 'Choose a later future deadline', 422)
    require(deadline <= payment.deadline_at + timedelta(hours=payment.rules['max_extension_hours']),
            'Extension exceeds the agreed maximum', 422)
    payment.extension = {'status': 'pending', 'requested_by': uid, 'deadline': deadline.isoformat() + 'Z',
                         'reason': text(data, 'reason')}
    event(payment, uid, 'extension_requested', payment.extension['reason'])


def decide(payment, uid, data):
    request = payment.extension
    require(request and request['status'] == 'pending', 'No pending extension')
    require(uid != request['requested_by'], 'The other party must decide', 403)
    require(payment.state not in ['completed', 'cancelled', 'disputed'], 'Extension cannot be decided now')
    decision = data.get('decision')
    require(decision in ['accept', 'decline'], 'Choose accept or decline', 422)
    if decision == 'accept':
        deadline = utc(datetime.fromisoformat(request['deadline']))
        require(deadline > utcnow(), 'Requested deadline has already passed')
        delta = deadline - payment.deadline_at
        payment.deadline_at = deadline
        for item in payment.milestones:
            if item.state != 'approved':
                item.deadline_at += delta
                if item.revision_due_at:
                    item.revision_due_at += delta
        if payment.category == 'booking':
            payment.booking_start += delta
            payment.booking_end += delta
            cutoff = datetime.fromisoformat(payment.rules['cancellation_deadline'].replace('Z', '+00:00'))
            payment.rules = {**payment.rules, 'cancellation_deadline': (cutoff + delta).isoformat()}
            booking_available(payment)
    payment.extension = {**request, 'status': 'accepted' if decision == 'accept' else 'declined'}
    event(payment, uid, 'extension_decided', decision)
