from tests.conftest import auth


def _funded(client, buyer, seller, amount="5000.00"):
    client.post("/api/wallet/deposit", json={"amount": "10000"}, headers=auth(buyer))
    r = client.post("/api/escrows", json={
        "seller_account": seller["account"], "amount": amount,
        "title": "Laptop purchase"}, headers=auth(buyer))
    assert r.status_code == 201, r.json
    esc = r.json["escrow"]
    client.post(f"/api/escrows/{esc['id']}/fund", headers=auth(buyer))
    return esc


def test_escrow_not_visible_to_strangers(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    registration = client.post("/api/auth/register", json={
        "full_name": "Nosy Person", "email": "nosy@example.com",
        "national_id": "44444444", "password": "secret123", "password_confirm": "secret123"}).json
    other = client.post("/api/auth/register/verify", json={
        "email": "nosy@example.com", "otp": client.mailbox["nosy@example.com"],
        "challenge_id": registration["challenge_id"]}).json
    r = client.get(f"/api/escrows/{esc['id']}",
                   headers={"Authorization": f"Bearer {other['token']}"})
    assert r.status_code == 404
