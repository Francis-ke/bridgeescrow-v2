import secrets
from app.core.db import db
from app.core.errors import ApiError
from app.models import Payment
from app.models.mixins import MoneyMixin
from app.services import wallet_service

DEMO_MSISDN = "254708374149"


def _ref() -> str:
    return "PAY" + secrets.token_hex(5).upper()


def start(user_id: int, amount, msisdn: str, kind: str = "stk_push", commit=True) -> Payment:
    """Create a pending M-Pesa payment intent (STK Push in production)."""
    cents = MoneyMixin.to_cents(amount)
    if cents < 100:
        raise ApiError("Minimum payment is KES 1.00")
    wallet = wallet_service.wallet_for(user_id)
    pay = Payment(reference=_ref(), wallet_id=wallet.id, kind=kind,
                  msisdn=msisdn, amount_cents=cents,
                  checkout_request_id="ws_CO_" + secrets.token_hex(6).upper())
    db.session.add(pay)
    db.session.flush()
    if commit:
        db.session.commit()
    return pay


from app.services.payment_confirmation import confirm


def fail(payment_id: int, commit=True) -> Payment:
    pay = db.session.get(Payment, payment_id)
    if not pay:
        raise ApiError("Payment not found", 404, "not_found")
    if pay.status == 'confirmed':
        raise ApiError('A confirmed payment cannot be marked failed', 409, 'invalid_state')
    pay.status = "failed"
    if commit:
        db.session.commit()
    return pay


def mine(user_id: int, limit: int = 30) -> list[dict]:
    wallet = wallet_service.wallet_for(user_id)
    rows = Payment.query.filter_by(wallet_id=wallet.id).order_by(
        Payment.id.desc()).limit(limit).all()
    return [p.to_dict() for p in rows]
