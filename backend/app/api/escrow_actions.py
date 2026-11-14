from flask import request, current_app
from app.core.db import db
from app.core.errors import ApiError
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.services import escrow_release
from app.api.escrow_routes import bp, visible_escrow


@bp.post("/<int:escrow_id>/release")
@login_required
def request_release(escrow_id):
    code = escrow_release.open_release(escrow_id, current_user_id())
    if current_app.config['PAYMENT_MODE'] == 'simulated':
        return {'status': 'code_sent', 'demo_code': code}
    return {'status': 'code_sent'}


@bp.post("/<int:escrow_id>/confirm")
@login_required
def confirm(escrow_id):
    code = (request.get_json(silent=True) or {}).get("code", "")
    esc = escrow_release.confirm_release(escrow_id, current_user_id(), code)
    return {"escrow": esc.to_dict()}


@bp.post("/<int:escrow_id>/refund")
@login_required
def refund(escrow_id):
    esc = escrow_release.refund(escrow_id, current_user_id(), False)
    return {"escrow": esc.to_dict()}


@bp.post("/<int:escrow_id>/cancel")
@login_required
def cancel(escrow_id):
    esc = visible_escrow(escrow_id)
    from app.services.protected.common import legacy_guard
    legacy_guard(esc)
    if esc.status != "hold" or esc.buyer_id != current_user_id():
        raise ApiError("Only an unfunded escrow by its buyer can be cancelled",
                       409, "invalid_state")
    esc.status = "cancelled"
    db.session.commit()
    return {"escrow": esc.to_dict()}


@bp.put("/<int:escrow_id>/receipt-hold")
@login_required
def receipt_hold(escrow_id):
    from app.services.receipt_hold import save
    esc = save(visible_escrow(escrow_id), current_user_id(),
               request.get_json(silent=True) or {})
    return {"escrow": esc.to_dict()}


@bp.post("/<int:escrow_id>/receipt-hold/decision")
@login_required
def decide_receipt_hold(escrow_id):
    from app.services.receipt_hold import decide
    escrow = visible_escrow(escrow_id)
    data = request.get_json(silent=True) or {}
    escrow = decide(escrow, current_user_id(), data.get("decision"))
    return {"escrow": escrow.to_dict()}
