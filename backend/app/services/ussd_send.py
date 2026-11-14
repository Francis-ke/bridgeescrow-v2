from app.services import ussd_helpers as h
from app.services.escrow_service import create
from app.services.escrow_funding import fund


def send(phone, steps):
    user = h.user_by_phone(phone)
    if not user:
        return h.NO_ACCOUNT
    if len(steps) == 1:
        return "CON Enter seller account number (BExxxxxxx)"
    if len(steps) == 2:
        return "CON Enter amount in KES"
    if len(steps) == 3:
        return "CON Enter what you are buying"
    from app.core.db import db
    try:
        with db.session.begin_nested():
            esc = create(user.id, steps[1], steps[2], " ".join(steps[3:]), commit=False)
            fund(esc.id, user.id, commit=False)
    except Exception as exc:
        return f"END {getattr(exc, 'message', 'Could not create escrow')}"
    return (f"END Funds protected.\nRef {esc.reference}\nKES {steps[2]} held "
            f"for {esc.seller.full_name}")
