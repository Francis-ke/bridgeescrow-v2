from flask import Blueprint, request
from app.core.db import db
from app.core.errors import ApiError
from app.core.decorators import role_required
from app.models import Dispute, Merchant
from app.services import dispute_service
from app.api.admin_routes import bp as _admin_bp

bp = _admin_bp


@bp.get("/disputes")
@role_required("admin")
def disputes():
    rows = Dispute.query.order_by(Dispute.id.desc()).limit(100).all()
    return {"disputes": [d.to_dict() for d in rows]}


@bp.post("/disputes/<int:dispute_id>/resolve")
@role_required("admin")
def resolve(dispute_id):
    from app.models import Dispute, Escrow
    from app.core.jwt import current_user_id
    dispute = db.session.get(Dispute, dispute_id)
    if dispute and db.session.get(Escrow, dispute.escrow_id).protection:
        from app.services.protected.admin import resolve as protected_resolve
        row = protected_resolve(dispute_id, current_user_id(), request.get_json(silent=True) or {})
        return {'dispute': row.to_dict()}
    row = dispute_service.resolve(dispute_id,
                                  (request.get_json(silent=True) or {})
                                  .get("resolution", ""))
    return {"dispute": row.to_dict()}


@bp.post("/merchants/<int:merchant_id>/approve")
@role_required("admin")
def approve_merchant(merchant_id):
    merchant = db.session.get(Merchant, merchant_id)
    if not merchant:
        raise ApiError("Merchant not found", 404, "not_found")
    merchant.status = "approved"
    db.session.commit()
    return {"merchant": merchant.to_dict()}
