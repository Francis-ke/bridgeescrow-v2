from app.models.mixins import utcnow
from .common import require, event, booking_available
from . import ledger


def accept(payment, uid, data):
    require(payment.state == 'awaiting_acceptance', 'Acceptance is already complete or unavailable')
    require(utcnow() < (payment.booking_start or payment.deadline_at), 'The acceptance deadline has passed')
    if uid == payment.escrow.buyer_id:
        require(not payment.client_accepted, 'You already accepted')
        payment.client_accepted = True
    else:
        require(not payment.provider_accepted, 'You already accepted')
        booking_available(payment)
        payment.provider_accepted = True
        if payment.category == 'booking':
            payment.reservation_confirmed_at = utcnow()
    if payment.client_accepted and payment.provider_accepted:
        payment.state = 'accepted'
    event(payment, uid, 'accepted', 'Terms and cancellation rules accepted.')


def fund(payment, uid, data):
    require(uid == payment.escrow.buyer_id, 'Only the client can fund this payment', 403)
    require(payment.state == 'accepted' and payment.escrow.status == 'hold', 'Both parties must accept before funding')
    require(utcnow() < (payment.booking_start or payment.deadline_at), 'Funding deadline has passed')
    booking_available(payment)
    ledger.fund(payment)
    payment.state, payment.escrow.status = 'funded', 'funded'
    event(payment, uid, 'funded', 'Protected funds are secured in escrow.')
