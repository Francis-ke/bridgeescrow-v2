import smtplib
from unittest.mock import MagicMock
from app.models import User
from app.services import otp_service


def registration(email="delivery@example.com"):
    return {"full_name": "Email User", "national_id": "77889900", "email": email,
            "password": "secret123", "password_confirm": "secret123"}


def test_otp_goes_to_each_users_email_for_registration_and_reset(client, app, monkeypatch):
    import importlib
    send = importlib.reload(otp_service)._send_email
    monkeypatch.setattr(otp_service, "_send_email", send)
    app.config.update(MAIL_PASSWORD="test-app-password", MAIL_USERNAME="sender@example.com",
                      MAIL_FROM="sender@example.com")
    smtp = MagicMock()
    monkeypatch.setattr(otp_service.smtplib, "SMTP", smtp)
    for index, email in enumerate(["first@example.com", "second@example.com"]):
        payload = registration(email)
        payload["national_id"] = f"9000000{index}"
        assert client.post("/api/auth/register", json=payload).status_code == 202
        connection = smtp.return_value.__enter__.return_value
        assert connection.send_message.call_args.args[0]["To"] == email
        assert client.post("/api/auth/password/forgot", json={"email": email}).status_code == 200
        message = connection.send_message.call_args.args[0]
        assert message["To"] == email
        assert message["From"] == "sender@example.com"
