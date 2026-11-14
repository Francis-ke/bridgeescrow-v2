from flask import Blueprint, request
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.services import dispute_service

from app.api.escrow_routes import bp


@bp.get("/<int:escrow_id>/disputes")
@login_required
def list_disputes(escrow_id):
    from app.api.escrow_routes import visible_escrow
    visible_escrow(escrow_id)
    return {"disputes": dispute_service.list_for(escrow_id)}


@bp.post("/<int:escrow_id>/disputes")
@login_required
def open_dispute(escrow_id):
    reason = (request.get_json(silent=True) or {}).get("reason", "")
    row = dispute_service.raise_dispute(escrow_id, current_user_id(), reason)
    return {"dispute": row.to_dict()}, 201
