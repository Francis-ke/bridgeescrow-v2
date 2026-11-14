from app.core.db import db
from app.core.errors import ApiError
from app.models import Dispute, Escrow


def _escrow(escrow_id: int) -> Escrow:
    esc = db.session.get(Escrow, escrow_id)
    if not esc:
        raise ApiError("Escrow not found", 404, "not_found")
    return esc


def raise_dispute(escrow_id: int, uid: int, reason: str) -> Dispute:
    esc = _escrow(escrow_id)
    if uid not in (esc.buyer_id, esc.seller_id):
        raise ApiError("Escrow not found", 404, "not_found")
    if esc.protection:
        from app.services.protected.disputes import open_dispute
        row = open_dispute(esc.protection, uid, {'reason': reason})
        db.session.commit()
        return row
    if esc.status not in ("funded", "disputed"):
        raise ApiError("Only a funded escrow can be disputed", 409, "invalid_state")
    if not reason or len(reason.strip()) < 10:
        raise ApiError("Describe the problem in at least 10 characters", 422)
    open_row = Dispute.query.filter_by(escrow_id=escrow_id, status="open").first()
    if open_row:
        raise ApiError("A dispute is already open", 409, "already_open")
    dispute = Dispute(escrow_id=escrow_id, raised_by=uid, reason=reason.strip())
    esc.status = "disputed"
    db.session.add(dispute)
    db.session.commit()
    return dispute


def list_for(escrow_id: int) -> list[dict]:
    rows = Dispute.query.filter_by(escrow_id=escrow_id).order_by(
        Dispute.id.desc()).all()
    return [d.to_dict() for d in rows]


def resolve(dispute_id: int, resolution: str) -> Dispute:
    dispute = db.session.get(Dispute, dispute_id)
    if not dispute:
        raise ApiError("Dispute not found", 404, "not_found")
    dispute.status = "resolved"
    dispute.resolution = (resolution or "Resolved by admin")[:400]
    db.session.commit()
    return dispute
