from datetime import datetime
from app.models.mixins import utcnow
from .common import require, event, utc
from .work import text
from . import ledger


def finish(payment, uid, percent, reason):
    amount = ledger.remaining(payment)
    if payment.escrow.status == 'funded':
        ledger.distribute(payment, amount, refund=amount * percent // 100)
    payment.state = 'cancelled'
    payment.escrow.status = 'refunded' if payment.refunded_cents else 'cancelled'
    event(payment, uid, 'cancelled', reason)


def request(payment, uid, data):
    require(payment.state not in ['completed', 'cancelled', 'disputed'], 'Cancellation is unavailable')
    reason = text(data, 'reason')
    if payment.escrow.status == 'hold':
        finish(payment, uid, 100, reason)
        return
    require(not payment.cancellation or payment.cancellation['status'] != 'pending', 'Cancellation already requested')
    cutoff = utc(datetime.fromisoformat(payment.rules['cancellation_deadline'].replace('Z', '+00:00')))
    percent = payment.rules['early_refund_percent' if utcnow() <= cutoff else 'late_refund_percent']
    if payment.category == 'booking':
        require(utcnow() < payment.booking_end and not payment.client_confirmed_at and
                not payment.provider_confirmed_at, 'Service is confirmed/completed; open a dispute instead')
        if uid == payment.escrow.seller_id:
            percent = 100
        finish(payment, uid, percent, reason)
    else:
        payment.cancellation = {'status': 'pending', 'requested_by': uid,
                                'refund_percent': percent, 'reason': reason}
        event(payment, uid, 'cancellation_requested', reason)


def decide(payment, uid, data):
    request = payment.cancellation
    require(request and request['status'] == 'pending', 'No pending cancellation')
    require(uid != request['requested_by'], 'The other party must decide', 403)
    require(payment.state not in ['completed', 'cancelled', 'disputed'], 'Cancellation is unavailable')
    decision = data.get('decision')
    require(decision in ['accept', 'decline'], 'Choose accept or decline', 422)
    if decision == 'accept':
        finish(payment, uid, request['refund_percent'], request['reason'])
    payment.cancellation = {**request, 'status': 'accepted' if decision == 'accept' else 'declined'}
    event(payment, uid, 'cancellation_decided', decision)
