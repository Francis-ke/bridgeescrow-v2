from tests.conftest import auth


def test_deposit_updates_wallet_and_ledger(client, buyer):
    r = client.post("/api/wallet/deposit", json={"amount": "1500.50"},
                    headers=auth(buyer))
    assert r.status_code == 201
    assert r.json["wallet"]["available"] == "1500.50"
    led = client.get("/api/wallet/ledger", headers=auth(buyer)).json["entries"]
    assert led[0]["entry_type"] == "deposit" and led[0]["amount_cents"] == 150050


def test_deposit_idempotency_blocks_double_credit(client, buyer):
    body = {"amount": "500.00", "idempotency_key": "topup-1"}
    client.post("/api/wallet/deposit", json=body, headers=auth(buyer))
    client.post("/api/wallet/deposit", json=body, headers=auth(buyer))
    wallet = client.get("/api/wallet", headers=auth(buyer)).json["wallet"]
    assert wallet["available"] == "500.00"


def test_withdraw_requires_pin(client, buyer):
    client.post("/api/wallet/deposit", json={"amount": "1000"}, headers=auth(buyer))
    r = client.post("/api/wallet/withdraw", json={"amount": "100"},
                    headers=auth(buyer))
    assert r.status_code == 403


def test_withdraw_with_pin(client, buyer):
    client.post("/api/auth/pin", json={"pin": "1234"}, headers=auth(buyer))
    client.post("/api/wallet/deposit", json={"amount": "1000"}, headers=auth(buyer))
    r = client.post("/api/wallet/withdraw", json={"amount": "400", "pin": "1234"},
                    headers=auth(buyer))
    assert r.json["wallet"]["available"] == "600.00"


def test_withdraw_insufficient_funds(client, buyer):
    client.post("/api/auth/pin", json={"pin": "1234"}, headers=auth(buyer))
    r = client.post("/api/wallet/withdraw", json={"amount": "50", "pin": "1234"},
                    headers=auth(buyer))
    assert r.status_code == 409
