from sqlalchemy import func, case
from app.core.db import db
from app.models import LedgerEntry
from tests.conftest import auth
from tests.protected_helpers import create, funded, act, balance, stamp


def test_freelance_accept_fund_revise_approve_and_balanced_ledger(client, buyer, seller):
    payment = create(client, buyer, seller)
    act(client, buyer, payment, 'fund', status=409)
    act(client, buyer, payment, 'accept')
    act(client, seller, payment, 'accept')
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '100'})
    payment = act(client, buyer, payment, 'fund')
    act(client, buyer, payment, 'fund', status=409)
    assert balance(client, buyer)['available'] == '0.00'
    assert balance(client, seller)['incoming_escrow'] == '99.00'
    mid = payment['milestones'][0]['id']
    act(client, buyer, payment, 'approve', {'milestone_id': mid}, status=409)
    payment = act(client, seller, payment, 'submit', {'milestone_id': mid, 'submission': 'Finished project https://example.com/work'})
    payment = act(client, buyer, payment, 'revise', {'milestone_id': mid, 'reason': 'Please revise the final paragraph.'})
    assert payment['state'] == 'revision_requested'
    payment = act(client, seller, payment, 'submit', {'milestone_id': mid, 'submission': 'Updated project with all requested revisions.'})
    payment = act(client, buyer, payment, 'approve', {'milestone_id': mid})
    assert payment['state'] == 'completed'
    assert payment['earned_fees'] == '1.00'
    assert balance(client, seller)['available'] == '99.00'
    assert balance(client, buyer)['escrow'] == '0.00'
    act(client, buyer, payment, 'approve', {'milestone_id': mid}, status=409)
    batches = db.session.query(LedgerEntry.batch_reference, func.sum(case(
        (LedgerEntry.direction == 'debit', LedgerEntry.amount_cents), else_=-LedgerEntry.amount_cents)))
    assert all(total == 0 for _, total in batches.filter(LedgerEntry.batch_reference.isnot(None)).group_by(LedgerEntry.batch_reference))
    assert client.get('/api/notifications', headers=auth(seller)).json['unread_count'] > 0


def test_optional_milestones_release_only_approved_amounts(client, buyer, seller):
    payment = funded(client, buyer, seller, milestones=[
        {'title': 'First phase', 'amount': '40', 'deadline': stamp(4)},
        {'title': 'Second phase', 'amount': '60', 'deadline': stamp(6)}])
    first, second = payment['milestones']
    act(client, seller, payment, 'submit', {'milestone_id': second['id'], 'submission': 'Out of order submission details'}, status=409)
    for item in [first, second]:
        payment = act(client, seller, payment, 'submit', {'milestone_id': item['id'], 'submission': 'The milestone is ready for your review.'})
        payment = act(client, buyer, payment, 'approve', {'milestone_id': item['id']})
        if item == first:
            assert payment['released'] == '40.00' and payment['remaining'] == '60.00'
            assert balance(client, buyer)['escrow'] == '60.00'
            assert balance(client, seller)['incoming_escrow'] == '59.40'
    assert payment['state'] == 'completed'
    assert balance(client, seller)['available'] == '99.00'
