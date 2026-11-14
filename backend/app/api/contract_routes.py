from flask import Blueprint, request
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.core.errors import ApiError
from app.services import contract_service

from app.api.escrow_routes import bp


def _terms(body: dict) -> tuple[str, int]:
    terms = str(body.get("terms", "")).strip()
    if len(terms) < 20:
        raise ApiError("Contract terms need at least 20 characters", 422)
    try:
        days = int(body.get("delivery_days", 7))
    except (TypeError, ValueError):
        days = 0
    if not 1 <= days <= 90:
        raise ApiError("Delivery window must be 1-90 days", 422)
    return terms, days


@bp.get("/<int:escrow_id>/contract")
@login_required
def get_contract(escrow_id):
    contract = contract_service.for_escrow(escrow_id, current_user_id())
    return {"contract": contract.to_dict() if contract else None}


@bp.put("/<int:escrow_id>/contract")
@login_required
def put_contract(escrow_id):
    terms, days = _terms(request.get_json(silent=True) or {})
    contract = contract_service.create_or_update(escrow_id, current_user_id(),
                                                 terms, days)
    return {"contract": contract.to_dict()}


@bp.post("/<int:escrow_id>/contract/sign")
@login_required
def sign_contract(escrow_id):
    contract = contract_service.sign(escrow_id, current_user_id())
    return {"contract": contract.to_dict()}
