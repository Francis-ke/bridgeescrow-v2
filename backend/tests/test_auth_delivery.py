import smtplib
from unittest.mock import MagicMock
from app.models import User
from app.services import otp_service


def registration(email="delivery@example.com"):
    return {"full_name": "Email User", "national_id": "77889900", "email": email,
            "password": "secret123", "password_confirm": "secret123"}


def test_smtp_delivery_and_no_code_exposure(client, app, monkeypatch):
    # Exercise the actual email function instead of the test mailbox substitute.
    import importlib
    send = importlib.reload(otp_service)._send_email
    monkeypatch.setattr(otp_service, "_send_email", send)
    app.config.update(MAIL_PASSWORD="test-app-password",
                      MAIL_USERNAME="sender@example.com", MAIL_FROM="sender@example.com")
    smtp = MagicMock()
    monkeypatch.setattr(otp_service.smtplib, "SMTP", smtp)
    r = client.post("/api/auth/register", json=registration())
    assert r.status_code == 202
    assert r.json["email_sent"] is True
    assert "demo_otp" not in r.json
    connection = smtp.return_value.__enter__.return_value
    connection.starttls.assert_called_once()
    connection.login.assert_called_once_with("sender@example.com", "test-app-password")
    message = connection.send_message.call_args.args[0]
    assert message["To"] == "delivery@example.com"
    assert message["From"] == "sender@example.com"
    assert "expires" in message.get_content()


def test_delivery_failure_rolls_back_registration(client, app, monkeypatch):
    import importlib
    send = importlib.reload(otp_service)._send_email
    monkeypatch.setattr(otp_service, "_send_email", send)
    app.config.update(MAIL_PASSWORD="test-app-password",
                      MAIL_USERNAME="sender@example.com", MAIL_FROM="sender@example.com")
    monkeypatch.setattr(otp_service.smtplib, "SMTP", MagicMock(
        side_effect=smtplib.SMTPAuthenticationError(535, b"Rejected")))
    r = client.post("/api/auth/register", json=registration())
    assert r.status_code == 503
    assert r.json["error"]["code"] == "email_unavailable"
    # Removing the request session must discard the failed registration.
    client.get("/api/health")
    assert User.query.filter_by(email="delivery@example.com").first() is None


def test_resend_replaces_code_and_consumed_code_cannot_be_reused(client):
    first = client.post("/api/auth/register", json=registration()).json
    old_code = client.mailbox[first["email"]]
    second = client.post("/api/auth/register/resend", json={"email": first["email"]}).json
    stale = client.post("/api/auth/register/verify", json={
        "email": first["email"], "otp": old_code, "challenge_id": first["challenge_id"]})
    assert stale.status_code == 422
    payload = {"email": first["email"], "otp": client.mailbox[first["email"]],
               "challenge_id": second["challenge_id"]}
    assert client.post("/api/auth/register/verify", json=payload).status_code == 200
    assert client.post("/api/auth/register/verify", json=payload).status_code == 422


def test_email_only_login_and_password_strength(client, buyer):
    r = client.post("/api/auth/login", json={
        "email": buyer["account"], "password": "secret123"})
    assert r.status_code == 422
    challenge = client.post("/api/auth/password/forgot", json={
        "email": "buyer@example.com"}).json
    payload = {"email": "buyer@example.com", "otp": client.mailbox["buyer@example.com"],
               "challenge_id": challenge["challenge_id"], "password": "short",
               "password_confirm": "short"}
    assert client.post("/api/auth/password/reset", json=payload).status_code == 422
    payload.update(password="replacement123", password_confirm="replacement123")
    assert client.post("/api/auth/password/reset", json=payload).status_code == 200
    assert client.post("/api/auth/password/reset", json=payload).status_code == 422
