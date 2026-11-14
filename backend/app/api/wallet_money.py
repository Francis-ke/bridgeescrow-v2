from flask import request, current_app
from app.core.errors import ApiError
from app.core.jwt import current_user_id
from app.core.db import db
from app.core.decorators import login_required
from app.services.transaction_pin import verify
from app.models import User
from app.services import wallet_service
from app.schemas.money import AmountSchema
from app.api.wallet_routes import bp, snapshot


@bp.post("/deposit")
@login_required
def deposit():
    if current_app.config['PAYMENT_MODE'] != 'simulated':
        raise ApiError('Use a verified provider payment to deposit money', 403, 'simulation_disabled')
    data = AmountSchema().load(request.get_json(silent=True) or {})
    wallet = wallet_service.deposit(current_user_id(), data["amount"],
                                   data["idempotency_key"])
    return {"wallet": snapshot(current_user_id(), wallet)}, 201


@bp.post("/withdraw")
@login_required
def withdraw():
    if current_app.config['PAYMENT_MODE'] != 'simulated':
        from app.services.payouts import initiate
        payout = initiate(current_user_id(), request.get_json(silent=True) or {})
        return {'payout': payout.to_dict(), 'wallet': snapshot(current_user_id())}, 202
    body = request.get_json(silent=True) or {}
    data = AmountSchema().load(body)
    user = db.session.get(User, current_user_id())
    verify(user, str(body.get("pin", "")))
    wallet = wallet_service.withdraw(current_user_id(), data["amount"], True,
                                     data["idempotency_key"])
    return {"wallet": snapshot(current_user_id(), wallet)}
