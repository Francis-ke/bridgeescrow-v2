def test_health(client):
    assert client.get("/api/health").json["status"] == "ok"


def test_register_login_flow(client):
    r = client.post("/api/auth/register", json={
        "full_name": "Amina Wanjiku", "email": "amina@example.com",
        "national_id": "12345678", "password": "secret123", "password_confirm": "secret123"})
    assert r.status_code == 202, r.json
    verified = client.post("/api/auth/register/verify", json={
        "email": "amina@example.com", "otp": client.mailbox["amina@example.com"],
        "challenge_id": r.json["challenge_id"]})
    assert verified.status_code == 200, verified.json
    acc = verified.json["user"]["account_number"]
    assert acc.startswith("BE") and len(acc) == 9
    login = client.post("/api/auth/login", json={
        "email": "amina@example.com", "password": "secret123"})
    assert login.status_code == 200
    token = login.json["token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json["user"]["email"] == "amina@example.com"
