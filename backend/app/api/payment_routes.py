from flask import Blueprint, request, current_app
from app.core.decorators import login_required
from app.core.errors import ApiError
from app.core.jwt import current_user_id
from app.services import payment_service

bp = Blueprint("payments", __name__, url_prefix="/api/payments")


@bp.get("")
@login_required
def my_payments():
    return {"payments": payment_service.mine(current_user_id())}


@bp.post("/stk-push")
@login_required
def stk_push():
    body = request.get_json(silent=True) or {}
    if current_app.config['PAYMENT_MODE'] != 'simulated':
        from app.services.mpesa_collection import initiate
        pay = initiate(current_user_id(), body.get('amount'), request.headers.get('Idempotency-Key', ''))
        return {'payment': pay.to_dict(), 'message': 'Request recorded. Confirm the M-PESA prompt if received; wallet credit waits for verified provider confirmation.'}, 202
    msisdn = str(body.get("msisdn", "")).strip()
    if not msisdn:
        raise ApiError("A phone number is required for the STK push")
    pay = payment_service.start(current_user_id(), body.get("amount", "0"),
                                msisdn, "stk_push")
    return {"payment": pay.to_dict(),
            "message": "Check your phone and enter the M-Pesa PIN"}, 201


@bp.post("/<int:payment_id>/simulate")
@login_required
def simulate_callback(payment_id):
    """Sandbox stand-in for the Safaricom Daraja callback endpoint."""
    from app.core.db import db
    from app.models import Payment
    from app.services.wallet_service import wallet_for
    pay = db.session.get(Payment, payment_id)
    if not pay or pay.wallet_id != wallet_for(current_user_id()).id:
        raise ApiError('Payment not found', 404, 'not_found')
    if current_app.config['PAYMENT_MODE'] != 'simulated' or pay.provider != 'simulated':
        raise ApiError('Payment simulation is disabled', 403, 'simulation_disabled')
    pay = payment_service.confirm(payment_id)
    return {"payment": pay.to_dict()}


@bp.post("/demo-checkout")
@login_required
def demo_checkout():
    from app.services.demo_checkout import checkout
    from app.api.wallet_routes import snapshot
    receipt = checkout(current_user_id(), request.get_json(silent=True) or {})
    return {"receipt": receipt.to_dict(), "wallet": snapshot(current_user_id())}
