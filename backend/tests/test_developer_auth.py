from datetime import datetime
from app.core.db import db
from app.models.developer_application import DeveloperApplication
from app.models.developer_usage import ApiUsageLog, ApiRateWindow
from tests.conftest import auth
from tests.developer_helpers import setup, create, key, api_auth


def test_scope_deactivation_environment_and_failed_auth_are_audited(app):
    client, owner, _ = setup(app)
    application = create(client, owner)
    issued = key(client, owner, application, permissions=['escrow:read'])
    headers = api_auth(issued['secret_key'])
    assert client.get('/api/v1/test-auth/escrow:write', headers=headers).status_code == 403
    assert ApiRateWindow.query.filter_by(credential_id=issued['credential']['id']).one().count == 1
    client.patch(f'/api/v1/developer/apps/{application["id"]}', headers=auth(owner), json={'active': False})
    assert client.get('/api/v1/test-auth/escrow:read', headers=headers).status_code == 403
    row = db.session.get(DeveloperApplication, application['id'])
    row.active, row.environment = True, 'production'
    db.session.commit()
    response = client.get('/api/v1/test-auth/escrow:read', headers=headers)
    assert response.status_code == 403 and response.json['error']['code'] == 'environment_disabled'
    bad = client.get('/api/v1/test-auth/escrow:read', headers=api_auth('be_test_sk_unknown'))
    assert bad.status_code == 401
    logged = ApiUsageLog.query.filter_by(request_id=bad.headers['X-Request-ID']).one()
    assert logged.app_id is None and logged.credential_id is None and logged.status == 401
    assert all(issued['secret_key'] not in str(row.__dict__) for row in ApiUsageLog.query.all())


def test_rate_limit_is_persistent_and_counts_failed_scope_requests(app, monkeypatch):
    monkeypatch.setattr('app.services.developer.rate_limit.utcnow', lambda: datetime(2027, 1, 1, 12, 0, 20))
    client, owner, _ = setup(app)
    application = create(client, owner)
    issued = key(client, owner, application, permissions=['escrow:read'])
    headers = {**api_auth(issued['secret_key']), 'Idempotency-Key': 'audit-request-key'}
    for _ in range(60):
        assert client.get('/api/v1/test-auth/escrow:write', headers=headers).status_code == 403
    blocked = client.get('/api/v1/test-auth/escrow:read', headers=headers)
    assert blocked.status_code == 429 and 'Retry-After' in blocked.headers
    window = ApiRateWindow.query.filter_by(credential_id=issued['credential']['id']).one()
    assert window.count == 61
    logs = ApiUsageLog.query.filter_by(credential_id=issued['credential']['id']).all()
    assert len(logs) == 61 and logs[-1].status == 429
    assert all(row.idempotency_key == 'audit-request-key' for row in logs)
