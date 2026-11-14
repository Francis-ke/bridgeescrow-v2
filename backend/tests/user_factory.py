from app.core.db import db as _db


def _make(client, email, phone, name, role="customer"):
    from app.models import User
    from app.services.accounts import next_account_number
    from app.services.wallet_service import wallet_for
    user = User(full_name=name, email=email, phone=phone, role=role,
                account_number=next_account_number(), email_verified=True)
    user.set_password("secret123")
    _db.session.add(user)
    _db.session.flush()
    wallet_for(user.id)
    _db.session.commit()
    r = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    assert r.status_code == 200, r.json
    return {"token": r.json["token"], "account": r.json["user"]["account_number"],
            "id": r.json["user"]["id"]}

