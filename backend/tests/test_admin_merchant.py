from tests.conftest import auth


def test_merchant_onboard_sets_role_and_till(client, seller):
    r = client.post("/api/merchant/onboard", json={"business_name": "Sara Shoes",
                                                   "till_number": "123456"},
                    headers=auth(seller))
    assert r.status_code == 201 and r.json["merchant"]["status"] == "pending"
    prof = client.get("/api/merchant/profile", headers=auth(seller)).json
    assert prof["merchant"]["till_number"] == "123456"


def test_merchant_onboard_rejects_bad_till(client, buyer):
    r = client.post("/api/merchant/onboard", json={"business_name": "X",
                                                   "till_number": "12"},
                    headers=auth(buyer))
    assert r.status_code == 400


def test_customer_cannot_reach_admin(client, buyer):
    assert client.get("/api/admin/overview", headers=auth(buyer)).status_code == 403


def test_admin_overview_counts(client, admin, buyer, seller):
    client.post("/api/wallet/deposit", json={"amount": "100"}, headers=auth(buyer))
    data = client.get("/api/admin/overview", headers=auth(admin)).json
    assert data["users"] == 3 and data["escrows"] == 0


def test_admin_can_suspend_and_login_blocked(client, admin, buyer):
    uid = buyer["id"]
    client.post(f"/api/admin/users/{uid}/suspend", headers=auth(admin))
    r = client.post("/api/auth/login", json={"email": "buyer@example.com",
                                             "password": "secret123"})
    assert r.status_code == 403


def test_admin_refund_disputed_escrow(client, admin, buyer, seller):
    from app.core.db import db
    from app.models import Escrow
    client.post("/api/wallet/deposit", json={"amount": "2000"}, headers=auth(buyer))
    esc = client.post("/api/escrows", json={"seller_account": seller["account"],
                                            "amount": "1000", "title": "Cable"},
                      headers=auth(buyer)).json["escrow"]
    client.post(f"/api/escrows/{esc['id']}/fund", headers=auth(buyer))
    row = db.session.get(Escrow, esc["id"])
    row.status = "disputed"
    db.session.commit()
    r = client.post(f"/api/admin/escrows/{esc['id']}/refund", headers=auth(admin))
    assert r.json["escrow"]["status"] == "refunded"
