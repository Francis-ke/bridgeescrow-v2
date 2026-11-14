from tests.conftest import auth
from tests.user_factory import _make
from tests.protected_helpers import create, act, balance


def test_complete_escrow_lifecycle_and_third_party_isolation(client, buyer, seller):
    user_c = _make(client, 'charlie_escrow@example.com', '0755555555', 'Charlie Escrow')
    client.post('/api/wallet/deposit', headers=auth(buyer), json={'amount': '500'})
    assert balance(client, buyer)['available'] == '500.00'
    assert balance(client, seller)['available'] == '0.00'
    assert balance(client, user_c)['available'] == '0.00'

    # 1. User A creates escrow agreement with User B
    payment = create(client, buyer, seller, amount='200')
    eid = payment['escrow']['id']

    # 2. Both parties accept
    act(client, buyer, payment, 'accept')
    act(client, seller, payment, 'accept')

    # 3. User A funds the escrow
    payment = act(client, buyer, payment, 'fund')
    assert balance(client, buyer)['available'] == '300.00'
    assert balance(client, buyer)['escrow'] == '200.00'
    assert balance(client, seller)['incoming_escrow'] == '198.00'
    assert balance(client, user_c)['available'] == '0.00'

    # 4. User B fulfills / submits work
    mid = payment['milestones'][0]['id']
    payment = act(client, seller, payment, 'submit', {
        'milestone_id': mid, 'submission': 'Work completed with documentation'
    })
    assert payment['state'] == 'submitted'

    # 5. User A confirms completion and authorizes release
    payment = act(client, buyer, payment, 'approve', {'milestone_id': mid})
    assert payment['state'] == 'completed'

    # 6. Balances update correctly
    assert balance(client, buyer)['available'] == '300.00'
    assert balance(client, buyer)['escrow'] == '0.00'
    assert balance(client, seller)['available'] == '198.00'
    assert balance(client, seller)['incoming_escrow'] == '0.00'

    # 7. User C remains completely unchanged
    assert balance(client, user_c)['available'] == '0.00'
    assert balance(client, user_c)['incoming_escrow'] == '0.00'
    assert client.get('/api/notifications', headers=auth(user_c)).json['unread_count'] == 0
    assert len(client.get('/api/wallet/ledger', headers=auth(user_c)).json['entries']) == 0
