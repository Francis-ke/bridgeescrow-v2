from app.core.db import db
from app.core.errors import ApiError
from app.models import Contract, Escrow
from app.models.mixins import utcnow


def _escrow(escrow_id: int) -> Escrow:
    esc = db.session.get(Escrow, escrow_id)
    if not esc:
        raise ApiError("Escrow not found", 404, "not_found")
    return esc


def for_escrow(escrow_id: int, uid: int) -> Contract | None:
    esc = _escrow(escrow_id)
    if uid not in (esc.buyer_id, esc.seller_id):
        raise ApiError("Escrow not found", 404, "not_found")
    return Contract.query.filter_by(escrow_id=escrow_id).first()


def create_or_update(escrow_id: int, uid: int, terms: str,
                     delivery_days: int) -> Contract:
    esc = _escrow(escrow_id)
    from app.services.protected.common import legacy_guard
    legacy_guard(esc)
    if esc.buyer_id != uid:
        raise ApiError("Only the buyer can draft the contract", 403, "forbidden")
    if esc.status != "hold":
        raise ApiError("Contract is locked once funds are held", 409, "invalid_state")
    contract = Contract.query.filter_by(escrow_id=escrow_id).first()
    if contract is None:
        contract = Contract(escrow_id=escrow_id, terms=terms,
                            delivery_days=delivery_days)
        db.session.add(contract)
    else:
        contract.terms, contract.delivery_days = terms, delivery_days
    db.session.commit()
    return contract


def sign(escrow_id: int, uid: int) -> Contract:
    esc = _escrow(escrow_id)
    contract = Contract.query.filter_by(escrow_id=escrow_id).first()
    if contract is None:
        raise ApiError("No contract on this escrow", 404, "not_found")
    if uid == esc.buyer_id and not contract.buyer_signed_at:
        contract.buyer_signed_at = utcnow()
    elif uid == esc.seller_id and not contract.seller_signed_at:
        contract.seller_signed_at = utcnow()
    else:
        raise ApiError("You already signed this contract", 409, "already_signed")
    db.session.commit()
    return contract
