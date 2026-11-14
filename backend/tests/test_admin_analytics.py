from tests.conftest import auth


def test_admin_analytics_shape(client, admin, buyer, seller):
    client.post("/api/wallet/deposit", json={"amount": "500"}, headers=auth(buyer))
    data = client.get("/api/admin/analytics", headers=auth(admin)).json
    assert data["customers"] == 1 and data["merchants"] == 0
    assert "volume_cents" in data
    assert "fees_earned" in data


def test_merchant_approval(client, admin, seller):
    m = client.post("/api/merchant/onboard",
                    json={"business_name": "Sara Shoes", "till_number": "555111"},
                    headers=auth(seller)).json["merchant"]
    r = client.post(f"/api/admin/merchants/{m['id']}/approve", headers=auth(admin))
    assert r.json["merchant"]["status"] == "approved"


def test_customer_cannot_read_admin_analytics(client, buyer):
    assert client.get("/api/admin/analytics", headers=auth(buyer)).status_code == 403
