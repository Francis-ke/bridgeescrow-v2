from tests.conftest import auth


def test_stk_push_creates_pending_payment(client, buyer):
    r = client.post("/api/payments/stk-push",
                    json={"amount": "250", "msisdn": "254711111111"},
                    headers=auth(buyer))
    assert r.status_code == 201 and r.json["payment"]["status"] == "pending"
    assert client.get("/api/wallet", headers=auth(buyer)).json["wallet"]["available"] == "0.00"


def test_confirmed_payment_credits_once(client, buyer):
    pid = client.post("/api/payments/stk-push",
                      json={"amount": "250", "msisdn": "254711111111"},
                      headers=auth(buyer)).json["payment"]["id"]
    client.post(f"/api/payments/{pid}/simulate", headers=auth(buyer))
    client.post(f"/api/payments/{pid}/simulate", headers=auth(buyer))
    wallet = client.get("/api/wallet", headers=auth(buyer)).json["wallet"]
    assert wallet["available"] == "250.00"


def test_unauthenticated_mpesa_callback_cannot_credit_wallet(client, buyer):
    pid = client.post("/api/payments/stk-push",
                      json={"amount": "99", "msisdn": "254711111111"},
                      headers=auth(buyer)).json["payment"]["id"]
    body = {"Body": {"stkCallback": {"ResultCode": 0, "AccountReference": str(pid),
                                     "CallbackMetadata": {"Item": [
                                         {"Name": "MpesaReceiptNumber",
                                          "Value": "QK12345"}]}}}}
    r = client.post("/api/callbacks/mpesa", json=body)
    assert r.status_code == 401
    assert client.get("/api/wallet", headers=auth(buyer)).json["wallet"]["available"] == "0.00"


def test_analytics_for_customer(client, buyer):
    client.post("/api/wallet/deposit", json={"amount": "400"}, headers=auth(buyer))
    data = client.get("/api/analytics/me", headers=auth(buyer)).json
    assert data["inflow_cents"] == 40000 and data["available_cents"] == 40000
