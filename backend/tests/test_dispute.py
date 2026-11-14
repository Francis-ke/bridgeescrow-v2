from tests.conftest import auth


def _funded(client, buyer, seller):
    client.post("/api/wallet/deposit", json={"amount": "3000"}, headers=auth(buyer))
    esc = client.post("/api/escrows", json={"seller_account": seller["account"],
                                            "amount": "1000", "title": "Television set"},
                      headers=auth(buyer)).json["escrow"]
    client.post(f"/api/escrows/{esc['id']}/fund", headers=auth(buyer))
    return esc


def test_dispute_freezes_escrow_and_blocks_release(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    r = client.post(f"/api/escrows/{esc['id']}/disputes",
                    json={"reason": "The TV arrived cracked and unusable"},
                    headers=auth(buyer))
    assert r.status_code == 201 and r.json["dispute"]["status"] == "open"
    rel = client.post(f"/api/escrows/{esc['id']}/release", headers=auth(buyer))
    assert rel.status_code == 409


def test_short_reason_rejected(client, buyer, seller):
    esc = _funded(client, buyer, seller)
    r = client.post(f"/api/escrows/{esc['id']}/disputes", json={"reason": "bad"},
                    headers=auth(buyer))
    assert r.status_code == 422


def test_admin_lists_and_resolves(client, admin, buyer, seller):
    esc = _funded(client, buyer, seller)
    d = client.post(f"/api/escrows/{esc['id']}/disputes",
                    json={"reason": "Item never shipped at all"}, headers=auth(buyer)
                    ).json["dispute"]
    rows = client.get("/api/admin/disputes", headers=auth(admin)).json["disputes"]
    assert rows and rows[0]["id"] == d["id"]
    done = client.post(f"/api/admin/disputes/{d['id']}/resolve",
                       json={"resolution": "Refunded buyer"}, headers=auth(admin))
    assert done.json["dispute"]["status"] == "resolved"
