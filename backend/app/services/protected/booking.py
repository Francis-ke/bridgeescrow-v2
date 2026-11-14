from app.models.mixins import utcnow
from .common import require, event
from . import ledger


def confirm(payment, uid, data):
    require(payment.category == 'booking', 'This action is for booking payments')
    require(payment.state in ['funded', 'service_confirmed'], 'Booking is not ready for confirmation')
    require(utcnow() >= payment.booking_start, 'The booking has not started yet')
    require(utcnow() >= payment.booking_end, 'Confirm service after the booked service period ends')
    if uid == payment.escrow.seller_id:
        require(not payment.provider_confirmed_at, 'Provider already confirmed service')
        payment.provider_confirmed_at = utcnow()
    else:
        require(not payment.client_confirmed_at, 'Client already confirmed attendance')
        payment.client_confirmed_at = utcnow()
    payment.state = 'service_confirmed'
    ready = payment.client_confirmed_at and (payment.provider_confirmed_at or
                                             payment.rules['release'] == 'client_approval')
    if ready:
        ledger.distribute(payment, ledger.remaining(payment))
        payment.state, payment.escrow.status = 'completed', 'released'
        payment.milestones[0].state = 'approved'
        payment.milestones[0].approved_at = utcnow()
    event(payment, uid, 'service_confirmed', 'Booking service/attendance confirmation recorded.')
