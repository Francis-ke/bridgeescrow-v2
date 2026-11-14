import pytest
from tests.conftest import auth
from tests.protected_helpers import funded, create, act


@pytest.mark.parametrize('category', ['delivery', 'services', 'events', 'deposits', 'contracts', 'other'])
def test_existing_payment_categories_use_complete_workflow(client, buyer, seller, category):
    p = funded(client, buyer, seller, category)
    item = p['milestones'][0]
    p = act(client, seller, p, 'submit', {'milestone_id': item['id'], 'submission': 'The agreed service has been completed in full.'})
    p = act(client, buyer, p, 'approve', {'milestone_id': item['id']})
    assert p['state'] == 'completed'


def test_categories_flow_into_history_merchant_and_admin_reports(client, buyer, seller, admin):
    p = funded(client, buyer, seller)
    item = p['milestones'][0]
    act(client, seller, p, 'submit', {'milestone_id': item['id'], 'submission': 'All deliverables ready for the client.'})
    act(client, buyer, p, 'approve', {'milestone_id': item['id']})
    rows = client.get('/api/escrows?direction=received&view=history', headers=auth(seller)).json['escrows']
    assert rows[0]['protection']['category'] == 'freelancing'
    merchant = client.get('/api/merchant/sales', headers=auth(seller)).json
    assert merchant['protected_categories'][0]['category'] == 'freelancing'
    analytics = client.get('/api/admin/analytics', headers=auth(admin)).json
    summary = analytics['protected_categories'][0]
    assert summary['released_cents'] == 10000 and summary['fee_cents'] == 100
    assert client.get('/api/admin/analytics', headers=auth(buyer)).status_code == 403
    assert client.get('/api/merchant/sales', headers=auth(buyer)).status_code == 403


def test_parties_must_be_verified_and_provider_cannot_self_select(client, buyer):
    assert client.post('/api/protected', json={}).status_code == 401
    response = client.post('/api/protected', headers=auth(buyer), json={
        'category': 'booking', 'provider_id': buyer['id']})
    assert response.status_code == 422
