





def test_missing_registration_field_is_named(client):
    payload = {"full_name": "New User", "national_id": "12345678",
               "email": "new@example.com", "password": "secret123"}
    result = client.post("/api/auth/register", json=payload)
    assert result.status_code == 422
    assert result.json["error"]["message"] == "Confirm password: Missing data for required field."


def test_unverified_sign_in_can_resend_and_verify(client):
    email = "returning@example.com"
    registered = client.post("/api/auth/register", json={
        "full_name": "Returning User", "national_id": "90909090", "email": email,
        "password": "secret123", "password_confirm": "secret123"})
    assert registered.status_code == 202
    blocked = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    assert blocked.json["error"]["code"] == "email_not_verified"
    resent = client.post("/api/auth/register/resend", json={"email": email})
    assert resent.status_code == 200
    verified = client.post("/api/auth/register/verify", json={
        "email": email, "otp": client.mailbox[email],
        "challenge_id": resent.json["challenge_id"]})
    assert verified.status_code == 200
    assert verified.json["user"]["email_verified"] is True
