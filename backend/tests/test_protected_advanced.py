from tests.conftest import auth
from tests.protected_helpers import create, funded, act, balance, stamp, payload


def test_revision_limit_does_not_allow_unapproved_payout(client, buyer, seller):
    rules = {**payload(seller)['rules'], 'max_revisions': 1}
    p = funded(client, buyer, seller, rules=rules)
    mid = p['milestones'][0]['id']
    for _ in range(2):
        p = act(client, seller, p, 'submit', {'milestone_id': mid, 'submission': 'Complete work awaiting final review.'})
        if p['milestones'][0]['revision_count'] == 0:
            p = act(client, buyer, p, 'revise', {'milestone_id': mid, 'reason': 'Please revise the remaining issues.'})
    act(client, buyer, p, 'revise', {'milestone_id': mid, 'reason': 'Another revision after the agreed limit.'}, status=409)
    assert balance(client, seller)['available'] == '0.00'
    assert act(client, buyer, p, 'approve', {'milestone_id': mid})['state'] == 'completed'


def test_booking_extension_conflict_rolls_back_dates(client, buyer, seller, admin):
    p = funded(client, buyer, seller, 'booking')
    other = create(client, admin, seller, 'booking', booking_start=stamp(8), booking_end=stamp(10), deadline=stamp(12))
    act(client, seller, other, 'accept')
    original = p['deadline']
    p = act(client, buyer, p, 'request-extension', {'deadline': stamp(11), 'reason': 'Reschedule this reservation four days later.'})
    act(client, seller, p, 'decide-extension', {'decision': 'accept'}, status=409)
    fetched = client.get(f'/api/protected/{p["escrow"]["id"]}', headers=auth(buyer)).json['payment']
    assert fetched['deadline'] == original
    assert fetched['extension']['status'] == 'pending'


def test_partial_milestone_dispute_refunds_only_remaining_funds(client, buyer, seller, admin):
    p = funded(client, buyer, seller, milestones=[
        {'title': 'First delivery', 'amount': '40', 'deadline': stamp(4)},
        {'title': 'Final delivery', 'amount': '60', 'deadline': stamp(6)}])
    mid = p['milestones'][0]['id']
    act(client, seller, p, 'submit', {'milestone_id': mid, 'submission': 'First deliverable completed as agreed.'})
    p = act(client, buyer, p, 'approve', {'milestone_id': mid})
    act(client, buyer, p, 'dispute', {'reason': 'The final delivery cannot be completed as agreed.'})
    dispute = client.get('/api/admin/disputes', headers=auth(admin)).json['disputes'][0]
    result = client.post(f'/api/admin/disputes/{dispute["id"]}/resolve', headers=auth(admin), json={
        'outcome': 'refund', 'resolution': 'Refund only the remaining unfinished milestone to the client.'})
    assert result.status_code == 200
    assert balance(client, buyer)['available'] == '960.00'
    assert balance(client, seller)['available'] == '39.60'
    analytics = client.get('/api/admin/analytics', headers=auth(admin)).json
    assert analytics['fees_earned'] == '0.40'
    assert analytics['protected_categories'][0]['refunded_cents'] == 6000
