from datetime import timedelta
from app.core.db import db
from app.models.protected_payment import ProtectedPayment
from app.models.mixins import utcnow
from tests.protected_helpers import funded, act, balance


def test_booking_reservation_and_both_service_confirmations(client, buyer, seller):
    p = funded(client, buyer, seller, 'booking')
    assert p['reservation_confirmed_at'] is not None
    act(client, buyer, p, 'confirm', status=409)
    row = ProtectedPayment.query.filter_by(escrow_id=p['escrow']['id']).one()
    row.booking_start, row.booking_end = utcnow() - timedelta(days=2), utcnow() - timedelta(days=1)
    db.session.commit()
    assert p['rules']['release'] == 'mutual_confirmation'
    p = act(client, buyer, p, 'confirm')
    assert p['state'] == 'service_confirmed'
    p = act(client, seller, p, 'confirm')
    assert p['state'] == 'completed'
    assert balance(client, seller)['available'] == '99.00'


def test_booking_early_cancellation_refunds_full_amount(client, buyer, seller):
    p = funded(client, buyer, seller, 'booking')
    p = act(client, buyer, p, 'cancel', {'reason': 'The customer no longer needs the reservation.'})
    assert p['state'] == 'cancelled' and p['refunded'] == '100.00'
    assert balance(client, buyer)['available'] == '1000.00'
    assert balance(client, seller)['available'] == '0.00'


def test_booking_late_refund_is_configured_not_general_80_20(client, buyer, seller):
    p = funded(client, buyer, seller, 'booking')
    row = ProtectedPayment.query.filter_by(escrow_id=p['escrow']['id']).one()
    row.rules = {**row.rules, 'late_refund_percent': 35,
                 'cancellation_deadline': (utcnow() - timedelta(hours=1)).isoformat() + 'Z'}
    db.session.commit()
    p = act(client, buyer, p, 'cancel', {'reason': 'Cancel after the agreed cancellation deadline.'})
    assert p['refunded'] == '35.00' and p['released'] == '65.00'
    assert balance(client, seller)['available'] == '64.35'
    assert balance(client, buyer)['escrow'] == '0.00'


def test_provider_cancellation_is_full_refund(client, buyer, seller):
    p = funded(client, buyer, seller, 'booking')
    p = act(client, seller, p, 'cancel', {'reason': 'Provider is unavailable for the service dates.'})
    assert p['refunded'] == '100.00' and p['released'] == '0.00'
