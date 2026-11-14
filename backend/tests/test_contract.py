from tests.conftest import auth

TERMS = "Seller delivers one 14-inch laptop in working condition."


def test_buyer_drafts_and_both_sign(client, buyer, seller):
    esc = client.post("/api/escrows", json={"seller_account": seller["account"],
                                            "amount": "100", "title": "Laptop purchase"},
                      headers=auth(buyer)).json["escrow"]
    r = client.put(f"/api/escrows/{esc['id']}/contract",
                   json={"terms": TERMS, "delivery_days": 5}, headers=auth(buyer))
    assert r.status_code == 200 and r.json["contract"]["delivery_days"] == 5
    client.post(f"/api/escrows/{esc['id']}/contract/sign", headers=auth(buyer))
    done = client.post(f"/api/escrows/{esc['id']}/contract/sign",
                       headers=auth(seller)).json["contract"]
    assert done["fully_signed"] is True


def test_seller_cannot_draft_contract(client, buyer, seller):
    esc = client.post("/api/escrows", json={"seller_account": seller["account"],
                                            "amount": "100", "title": "Thing"},
                      headers=auth(buyer)).json["escrow"]
    r = client.put(f"/api/escrows/{esc['id']}/contract", json={"terms": TERMS},
                   headers=auth(seller))
    assert r.status_code == 403
