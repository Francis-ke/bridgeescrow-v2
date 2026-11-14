from flask import Blueprint, request
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.core.db import db
from app.core.errors import ApiError
from app.models.escrow import Escrow
from app.services import escrow_service
from app.services.escrow_funding import fund
from app.schemas.money import EscrowCreateSchema

bp = Blueprint("escrow", __name__, url_prefix="/api/escrows")


def visible_escrow(escrow_id: int) -> Escrow:
    """Load an escrow only if the caller is its buyer or seller."""
    esc = db.session.get(Escrow, escrow_id)
    uid = current_user_id()
    if not esc or uid not in (esc.buyer_id, esc.seller_id):
        raise ApiError("Escrow not found", 404, "not_found")
    return esc


@bp.get("")
@login_required
def list_escrows():
    uid = current_user_id()
    direction = request.args.get("direction")
    if direction not in (None, "sent", "received"):
        raise ApiError("Choose sent or received escrows", 422, "invalid_direction")
    condition = {"sent": Escrow.buyer_id == uid,
                 "received": Escrow.seller_id == uid}.get(direction)
    if condition is None:
        condition = (Escrow.buyer_id == uid) | (Escrow.seller_id == uid)
    view = request.args.get("view")
    if view not in (None, "progress", "history"):
        raise ApiError("Choose in-progress or history escrows", 422, "invalid_view")
    query = Escrow.query.filter(condition)
    if view:
        statuses = ("hold", "funded", "disputed") if view == "progress" else (
            "released", "refunded", "cancelled")
        query = query.filter(Escrow.status.in_(statuses))
    rows = query.order_by(Escrow.id.desc()).limit(100).all()
    return {"escrows": [e.to_dict() for e in rows]}


@bp.post("")
@login_required
def create_escrow():
    data = EscrowCreateSchema().load(request.get_json(silent=True) or {})
    esc = escrow_service.create(current_user_id(), data["seller_account"],
                                data["amount"], data["title"])
    return {"escrow": esc.to_dict()}, 201


@bp.get("/<int:escrow_id>")
@login_required
def get_escrow(escrow_id):
    return {"escrow": visible_escrow(escrow_id).to_dict()}


@bp.post("/<int:escrow_id>/fund")
@login_required
def fund_escrow(escrow_id):
    return {"escrow": fund(escrow_id, current_user_id()).to_dict()}
