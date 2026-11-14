





def test_protected_route_requires_token(client):
    assert client.get("/api/dashboard").status_code == 401


def test_bad_password_rejected(client, buyer):
    r = client.post("/api/auth/login", json={
        "email": "buyer@example.com", "password": "nope"})
    assert r.status_code == 401


def test_account_numbers_unique(client):
    a = client.post("/api/auth/register", json={
        "full_name": "One User", "email": "u1@example.com",
        "national_id": "10000001", "password": "secret123", "password_confirm": "secret123"}).json
    b = client.post("/api/auth/register", json={
        "full_name": "Two User", "email": "u2@example.com",
        "national_id": "10000002", "password": "secret123", "password_confirm": "secret123"}).json
    av = client.post("/api/auth/register/verify", json={
        "email": "u1@example.com", "otp": client.mailbox["u1@example.com"],
        "challenge_id": a["challenge_id"]}).json
    bv = client.post("/api/auth/register/verify", json={
        "email": "u2@example.com", "otp": client.mailbox["u2@example.com"],
        "challenge_id": b["challenge_id"]}).json
    assert av["user"]["account_number"] != bv["user"]["account_number"]


def test_duplicate_email_rejected(client, buyer):
    r = client.post("/api/auth/register", json={
        "full_name": "Copy Cat", "email": "buyer@example.com",
        "national_id": "19999999", "password": "secret123", "password_confirm": "secret123"})
    assert r.status_code == 409


def test_registration_requires_id_and_confirmation(client):
    r = client.post("/api/auth/register", json={
        "full_name": "New User", "email": "new@example.com", "password": "secret123"})
    assert r.status_code == 422


def test_registration_verifies_email_before_login(client):
    r = client.post("/api/auth/register", json={
        "full_name": "ID User", "national_id": "A1234567",
        "email": "id@example.com", "password": "secret123",
        "password_confirm": "secret123"})
    assert r.status_code == 202
    blocked = client.post("/api/auth/login", json={
        "email": "id@example.com", "password": "secret123"})
    assert blocked.status_code == 403
    verified = client.post("/api/auth/register/verify", json={
        "email": "id@example.com", "otp": client.mailbox["id@example.com"],
        "challenge_id": r.json["challenge_id"]})
    assert verified.status_code == 200


def test_password_reset_uses_email_otp(client, buyer):
    requested = client.post("/api/auth/password/forgot", json={
        "email": "buyer@example.com"})
    assert requested.status_code == 200
    reset = client.post("/api/auth/password/reset", json={
        "email": "buyer@example.com", "otp": client.mailbox["buyer@example.com"],
        "challenge_id": requested.json["challenge_id"],
        "password": "newsecret123", "password_confirm": "newsecret123"})
    assert reset.status_code == 200
    login = client.post("/api/auth/login", json={
        "email": "buyer@example.com", "password": "newsecret123"})
    assert login.status_code == 200
