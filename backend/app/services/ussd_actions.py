from app.models import User
from app.services.wallet_service import wallet_for
from app.services.ussd_send import send
from app.services.ussd_release import release
from app.services import ussd_helpers as h


def balance(phone, steps):
    user = h.user_by_phone(phone)
    if not user:
        return h.NO_ACCOUNT
    from app.api.wallet_routes import snapshot
    w = snapshot(user.id)
    return (f"END {user.account_number}\nAvailable: KES {w['available']}\n"
            f"In escrow: KES {float(w['escrow']) + float(w['incoming_escrow']):.2f}")


def list_escrows(phone, steps):
    user = h.user_by_phone(phone)
    if not user:
        return h.NO_ACCOUNT
    return h.short_escrows(user)


def register(phone, steps):
    if h.user_by_phone(phone):
        return "END You already have an account."
    return "END Register on the BridgeEscrow web portal, then dial again."
