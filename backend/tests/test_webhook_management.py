from app.core.db import db
from app.models.webhook import WebhookEndpoint
from tests.conftest import auth
from tests.webhook_helpers import application, public_dns


def test_webhooks_are_owned_and_secret_is_returned_only_once(client, buyer, seller, monkeypatch):
    public_dns(monkeypatch)
    aid = application(buyer)
    url = f'/api/v1/developer/apps/{aid}/webhooks'
    body = {'url': 'https://merchant.example/webhooks', 'events': ['payment.pending']}
    assert client.post(url, json=body).status_code == 401
    assert client.post(url, headers=auth(seller), json=body).status_code == 404
    created = client.post(url, headers=auth(buyer), json=body)
    assert created.status_code == 201, created.json
    secret = created.json['signing_secret']
    eid = created.json['webhook']['id']
    assert secret.startswith('be_whsec_')
    encrypted = db.session.get(WebhookEndpoint, eid).secret_ciphertext
    assert secret not in encrypted
    listed = client.get(url, headers=auth(buyer)).json
    assert secret not in str(listed) and 'secret_ciphertext' not in str(listed)
    root = f'/api/v1/developer/webhooks/{eid}'
    assert client.patch(root, headers=auth(seller), json={'active': False}).status_code == 404
    rotated = client.post(root + '/rotate-secret', headers=auth(buyer))
    assert rotated.status_code == 200 and rotated.json['signing_secret'] != secret
    assert client.patch(root, headers=auth(buyer), json={'active': False}).json['webhook']['active'] is False
    assert client.post(root + '/test', headers=auth(buyer)).status_code == 409


def test_webhook_test_queues_durable_event_without_network(client, buyer, seller, monkeypatch):
    public_dns(monkeypatch)
    aid = application(buyer)
    created = client.post(f'/api/v1/developer/apps/{aid}/webhooks', headers=auth(buyer), json={
        'url': 'https://merchant.example/hooks', 'events': ['escrow.released']})
    eid = created.json['webhook']['id']
    tested = client.post(f'/api/v1/developer/webhooks/{eid}/test', headers=auth(buyer))
    assert tested.status_code == 202 and tested.json['queued'] is True
    assert tested.json['delivery']['status'] == 'pending'
    assert tested.json['delivery']['attempts'] == 0
    rows = client.get(f'/api/v1/developer/webhooks/{eid}/deliveries', headers=auth(buyer)).json['deliveries']
    assert len(rows) == 1 and rows[0]['event_type'] == 'payment.pending'
    assert client.get(f'/api/v1/developer/webhooks/{eid}/deliveries', headers=auth(seller)).status_code == 404
