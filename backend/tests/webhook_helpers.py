from app.core.db import db
from app.models.developer_application import DeveloperApplication
from app.models.webhook import WebhookEndpoint
from app.services.developer.webhook_secrets import issue
from app.services.developer.webhook_events import EVENTS


def application(user):
    app = DeveloperApplication(user_id=user['id'], name='Webhook Test',
        description='Webhook application used by automated tests.', type='backend', environment='sandbox')
    db.session.add(app)
    db.session.commit()
    return app.id


def endpoint(user, events=None):
    app_id = application(user)
    secret, encrypted = issue()
    row = WebhookEndpoint(app_id=app_id, url='https://merchant.example/hooks',
                          secret_ciphertext=encrypted, events=list(events or EVENTS))
    db.session.add(row)
    db.session.commit()
    return app_id, row.id, secret


def public_dns(monkeypatch):
    monkeypatch.setattr('app.services.developer.webhook_urls.socket.getaddrinfo',
        lambda *args, **kwargs: [(2, 1, 6, '', ('93.184.216.34', 443))])
