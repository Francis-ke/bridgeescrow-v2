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


def test_create_escrow_generates_reference(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    assert esc["reference"].startswith("ESC") and esc["status"] == "hold"
    assert esc["fee"] == "50.00"


def test_funding_moves_money_to_escrow_balance(client, buyer, seller):
    _funded(client, buyer, seller)
    w = client.get("/api/wallet", headers=auth(buyer)).json["wallet"]
    assert w["available"] == "5000.00" and w["escrow"] == "5000.00"


def test_full_release_flow_pays_seller_minus_fee(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    code = client.post(f"/api/escrows/{esc['id']}/release",
                       headers=auth(buyer)).json["demo_code"]
    r = client.post(f"/api/escrows/{esc['id']}/confirm", json={"code": code},
                    headers=auth(buyer))
    assert r.json["escrow"]["status"] == "released"
    seller_w = client.get("/api/wallet", headers=auth(seller)).json["wallet"]
    buyer_w = client.get("/api/wallet", headers=auth(buyer)).json["wallet"]
    assert seller_w["available"] == "4950.00"
    assert buyer_w["escrow"] == "0.00"


def test_wrong_release_code_rejected(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    r = client.post(f"/api/escrows/{esc['id']}/confirm", json={"code": "000000"},
                    headers=auth(buyer))
    assert r.status_code == 403


def test_refund_returns_money_to_buyer(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    r = client.post(f"/api/escrows/{esc['id']}/refund", headers=auth(buyer))
    assert r.json["escrow"]["status"] == "refunded"
    w = client.get("/api/wallet", headers=auth(buyer)).json["wallet"]
    assert w["available"] == "10000.00" and w["escrow"] == "0.00"


def test_cannot_fund_without_balance(client, buyer, seller):
    r = client.post("/api/escrows", json={"seller_account": seller["account"],
                                          "amount": "900", "title": "Gadget"},
                    headers=auth(buyer))
    eid = r.json["escrow"]["id"]
    assert client.post(f"/api/escrows/{eid}/fund",
                       headers=auth(buyer)).status_code == 409


def test_unknown_seller_404(client, buyer):
    r = client.post("/api/escrows", json={"seller_account": "BE0000000",
                                          "amount": "100", "title": "Thing"},
                    headers=auth(buyer))
    assert r.status_code == 404
