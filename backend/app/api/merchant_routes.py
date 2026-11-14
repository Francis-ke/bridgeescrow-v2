from flask import Blueprint, request
from app.core.db import db
from app.core.errors import ApiError
from app.core.decorators import login_required, role_required
from app.core.jwt import current_user_id
from app.models import User, Merchant, Escrow
from app.services.wallet_service import wallet_for

bp = Blueprint("merchant", __name__, url_prefix="/api/merchant")


@bp.post("/onboard")
@login_required
def onboard():
    body = request.get_json(silent=True) or {}
    if Merchant.query.filter_by(user_id=current_user_id()).first():
        raise ApiError("Merchant profile already exists", 409, "exists")
    till = str(body.get("till_number", "")).strip()
    if not till.isdigit() or len(till) != 6:
        raise ApiError("Till number must be 6 digits")
    user = db.session.get(User, current_user_id())
    merchant = Merchant(user_id=user.id, business_name=body.get("business_name", ""),
                        till_number=till, status="pending")
    user.role = "merchant"
    db.session.add(merchant)
    db.session.commit()
    return {"merchant": merchant.to_dict()}, 201


@bp.get("/profile")
@login_required
def profile():
    merchant = Merchant.query.filter_by(user_id=current_user_id()).first()
    if not merchant:
        raise ApiError("No merchant profile yet", 404, "not_found")
    return {"merchant": merchant.to_dict(),
            "wallet": wallet_for(current_user_id()).to_dict()}


@bp.get("/sales")
@role_required("merchant")
def sales():
    rows = Escrow.query.filter_by(seller_id=current_user_id()).order_by(
        Escrow.id.desc()).limit(100).all()
    from app.services.protected.reports import categories
    return {'protected_categories': categories(current_user_id(), merchant=True), "sales": [e.to_dict() for e in rows]}
