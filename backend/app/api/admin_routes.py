from flask import Blueprint, request
from sqlalchemy import func
from app.core.db import db
from app.core.errors import ApiError
from app.core.decorators import role_required
from app.models import User, Escrow, LedgerEntry, Merchant
from app.services.escrow_release import refund

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/overview")
@role_required("admin")
def overview():
    total_held = (db.session.query(func.coalesce(func.sum(Escrow.amount_cents), 0))
                  .filter(Escrow.status == "funded").scalar())
    released = (db.session.query(func.coalesce(func.sum(Escrow.amount_cents), 0))
                .filter(Escrow.status == "released").scalar())
    return {"users": User.query.count(), "escrows": Escrow.query.count(),
            "merchants": Merchant.query.count(),
            "ledger_rows": LedgerEntry.query.count(),
            "held_cents": int(total_held), "released_cents": int(released),
            "disputed": Escrow.query.filter_by(status="disputed").count()}


@bp.get("/users")
@role_required("admin")
def users():
    rows = User.query.order_by(User.id.desc()).limit(200).all()
    return {"users": [u.to_dict() for u in rows]}


@bp.post("/escrows/<int:escrow_id>/refund")
@role_required("admin")
def admin_refund(escrow_id):
    return {"escrow": refund(escrow_id, 0, True).to_dict()}


@bp.post("/users/<int:user_id>/suspend")
@role_required("admin")
def suspend(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError("User not found", 404, "not_found")
    if user.role == "admin":
        raise ApiError("Admins cannot be suspended", 403, "forbidden")
    user.is_active = not user.is_active
    db.session.commit()
    return {"user": user.to_dict()}


@bp.get('/merchants')
@role_required('admin')
def merchants():
    rows = Merchant.query.order_by(Merchant.id.desc()).limit(200).all()
    return {'merchants': [row.to_dict() for row in rows]}
