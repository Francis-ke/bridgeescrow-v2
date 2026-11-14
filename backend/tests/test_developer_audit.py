from app.models import Wallet
from app.models.developer_usage import ApiUsageLog
from tests.developer_helpers import setup, create, key, api_auth


def test_audit_hook_never_commits_unfinished_balance_changes(app):
    client, owner, _ = setup(app)
    application = create(client, owner)
    issued = key(client, owner, application)
    for status in [400, 200]:
        response = client.get(f'/api/v1/test-rollback/{status}', headers=api_auth(issued['secret_key']))
        assert response.status_code == status
        assert Wallet.query.filter_by(user_id=owner['id']).one().available_cents == 0
        log = ApiUsageLog.query.filter_by(request_id=response.headers['X-Request-ID']).one()
        assert log.status == status and log.credential_id == issued['credential']['id']


def test_non_v1_requests_do_not_reuse_audit_context(app):
    from tests.conftest import auth
    client, owner, _ = setup(app)
    create(client, owner)
    count = ApiUsageLog.query.count()
    response = client.get('/api/wallet', headers=auth(owner))
    assert response.status_code == 200
    assert 'X-Request-ID' not in response.headers
    assert ApiUsageLog.query.count() == count
