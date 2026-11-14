from tests.conftest import auth
from tests.protected_helpers import funded, act, balance


def test_legacy_endpoints_cannot_bypass_approval_or_booking_rules(client, buyer, seller, admin):
    p = funded(client, buyer, seller)
    eid = p['escrow']['id']
    for path, body in [('release', {}), ('confirm', {'code': '123456'}), ('refund', {}), ('fund', {})]:
        assert client.post(f'/api/escrows/{eid}/{path}', headers=auth(buyer), json=body).status_code == 409
    assert client.post(f'/api/admin/escrows/{eid}/refund', headers=auth(admin)).status_code == 409
    assert client.get(f'/api/protected/{eid}', headers=auth(admin)).status_code == 404
    assert client.get(f'/api/escrows/{eid}/disputes', headers=auth(admin)).status_code == 404
    act(client, seller, p, 'approve', {'milestone_id': p['milestones'][0]['id']}, status=403)
    assert balance(client, seller)['available'] == '0.00'


def test_disputes_freeze_funds_and_admin_can_refund_remaining(client, buyer, seller, admin):
    p = funded(client, buyer, seller)
    p = act(client, seller, p, 'dispute', {'reason': 'The agreed deliverables need administrator review.'})
    assert p['state'] == 'disputed'
    act(client, buyer, p, 'cancel', {'reason': 'Trying to cancel during an open dispute.'}, status=409)
    act(client, seller, p, 'submit', {'milestone_id': p['milestones'][0]['id'], 'submission': 'Submission while funds are frozen.'}, status=409)
    issues = client.get('/api/admin/disputes', headers=auth(admin)).json['disputes']
    issue = next(row for row in issues if row['escrow_id'] == p['escrow']['id'])
    assert issue['category'] == 'freelancing'
    url = f'/api/admin/disputes/{issue["id"]}/resolve'
    body = {'outcome': 'refund', 'resolution': 'The administrator approves a full refund to the client.'}
    assert client.post(url, headers=auth(buyer), json=body).status_code == 403
    assert client.post(url, headers=auth(admin), json=body).status_code == 200
    assert client.post(url, headers=auth(admin), json=body).status_code == 409
    assert balance(client, buyer)['escrow'] == '0.00'
    assert balance(client, buyer)['available'] == '1000.00'


def test_admin_review_is_readonly_and_role_protected(client, buyer, seller, admin):
    p = funded(client, buyer, seller)
    url = f'/api/admin/protected/{p["escrow"]["id"]}'
    assert client.get(url).status_code == 401
    assert client.get(url, headers=auth(buyer)).status_code == 403
    result = client.get(url, headers=auth(admin))
    assert result.status_code == 200
    assert result.json['payment']['description'] == p['description']
    assert result.json['payment']['actions'] == []
