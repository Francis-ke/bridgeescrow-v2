import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from app import create_app
from app.core.db import db as _db
from tests.user_factory import _make

TEST_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

@pytest.fixture()
def app(monkeypatch):
    mailbox = {}

    def deliver(user, code, purpose):
        mailbox[user.email] = code
        return True

    monkeypatch.setattr("app.services.otp_service._send_email", deliver)
    app = create_app({"SQLALCHEMY_DATABASE_URI": TEST_URI,
                      "SQLALCHEMY_ENGINE_OPTIONS": {},
                      "SECRET_KEY": "test-secret-key-32-characters-long-value",
                      "JWT_SECRET": "test-jwt-secret-32-characters-long-value", "TESTING": True, "PAYMENT_MODE": "simulated", "SMS_MODE": "simulated",
                      "USSD_CALLBACK_TOKEN": "", "MPESA_CALLBACK_TOKEN": ""})
    app.extensions["test_mailbox"] = mailbox
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture()
def client(app):
    from app.core.db import db
    base = app.test_client()

    class FreshClient:
        mailbox = app.extensions["test_mailbox"]
        def __getattr__(self, name):
            method = getattr(base, name)
            if name not in ("get", "post", "put", "patch", "delete"):
                return method

            def wrapped(*a, **kw):
                db.session.remove()
                return method(*a, **kw)
            return wrapped

    return FreshClient()

@pytest.fixture()
def buyer(client):
    return _make(client, "buyer@example.com", "0711111111", "Brian Buyer")

@pytest.fixture()
def seller(client):
    return _make(client, "seller@example.com", "0722222222", "Sara Seller",
                 role="merchant")

@pytest.fixture()
def admin(client):
    from app.core.db import db
    from app.models import User
    _make(client, "admin@example.com", "0733333333", "Ada Admin")
    user = User.query.filter_by(email="admin@example.com").first()
    user.role = "admin"
    db.session.commit()
    db.session.remove()
    r = client.post("/api/auth/login", json={"email": "admin@example.com",
                                              "password": "secret123"})
    return {"token": r.json["token"], "account": r.json["user"]["account_number"],
            "id": r.json["user"]["id"]}

def auth(subject):
    return {"Authorization": f"Bearer {subject['token']}"}
