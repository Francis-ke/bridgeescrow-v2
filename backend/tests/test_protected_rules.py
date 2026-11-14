from datetime import timedelta
from app.core.db import db
from app.models.protected_payment import ProtectedPayment
from app.models.mixins import utcnow
from tests.conftest import auth
from tests.protected_helpers import create, funded, act, stamp, payload, balance


def test_extensions_need_other_party_approval_and_are_bounded(client, buyer, seller):
    p = funded(client, buyer, seller)
    act(client, seller, p, 'request-extension', {'deadline': stamp(20), 'reason': 'Extra time for additional project work.'}, status=422)
    p = act(client, seller, p, 'request-extension', {'deadline': stamp(8), 'reason': 'Additional time for final quality checks.'})
    old = p['deadline']
    act(client, seller, p, 'decide-extension', {'decision': 'accept'}, status=403)
    p = act(client, buyer, p, 'decide-extension', {'decision': 'accept'})
    assert p['deadline'] != old and p['extension']['status'] == 'accepted'


def test_expired_work_cannot_be_submitted_without_agreed_extension(client, buyer, seller):
    p = funded(client, buyer, seller)
    row = ProtectedPayment.query.filter_by(escrow_id=p['escrow']['id']).one()
    row.milestones[0].deadline_at = utcnow() - timedelta(minutes=1)
    db.session.commit()
    act(client, seller, p, 'submit', {'milestone_id': p['milestones'][0]['id'], 'submission': 'Finished work delivered after the deadline.'}, status=409)


def test_funded_freelance_cancellation_requires_mutual_decision(client, buyer, seller):
    p = funded(client, buyer, seller)
    p = act(client, buyer, p, 'cancel', {'reason': 'The project requirements have substantially changed.'})
    assert p['state'] == 'funded'
    act(client, buyer, p, 'decide-cancel', {'decision': 'accept'}, status=403)
    p = act(client, seller, p, 'decide-cancel', {'decision': 'accept'})
    assert p['refunded'] == '100.00'
    assert balance(client, buyer)['escrow'] == '0.00'


def test_invalid_milestones_dates_and_booking_policy_are_rejected(client, buyer, seller):
    data = payload(seller, milestones=[{'title': 'Wrong amount', 'amount': '20', 'deadline': stamp(3)}])
    assert client.post('/api/protected', headers=auth(buyer), json=data).status_code == 422
    data = payload(seller, 'booking')
    data['rules'].pop('late_refund_percent')
    assert client.post('/api/protected', headers=auth(buyer), json=data).status_code == 422
    data = payload(seller, 'booking', booking_start=stamp(6), booking_end=stamp(5))
    assert client.post('/api/protected', headers=auth(buyer), json=data).status_code == 422


def test_provider_cannot_accept_overlapping_reservations(client, buyer, seller, admin):
    first = create(client, buyer, seller, 'booking')
    act(client, seller, first, 'accept')
    second = create(client, admin, seller, 'booking')
    act(client, seller, second, 'accept', status=409)
