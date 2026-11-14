from app.services import ussd_helpers as h
from app.services.escrow_release import confirm_release, open_release


def release(phone, steps):
    user = h.user_by_phone(phone)
    if not user:
        return h.NO_ACCOUNT
    if len(steps) == 1:
        return "CON Enter escrow reference (ESC...)"
    if len(steps) == 2:
        try:
            code = open_release_by_ref(user, steps[1])
        except Exception as exc:
            return f"END {getattr(exc, 'message', 'Escrow not found')}"
        return f"CON Release code sent by SMS. Enter it now"
    try:
        confirm_release_by_ref(user, steps[1], steps[-1])
    except Exception as exc:
        return f"END {getattr(exc, 'message', 'Release failed')}"
    return "END Payment released to seller. Asante!"


def _escrow(ref: str):
    from app.models import Escrow
    esc = Escrow.query.filter_by(reference=ref.strip().upper()).first()
    if not esc:
        raise LookupError("Escrow reference not found")
    return esc


def open_release_by_ref(user, ref):
    return open_release(_escrow(ref).id, user.id, commit=False)


def confirm_release_by_ref(user, ref, code):
    return confirm_release(_escrow(ref).id, user.id, code, commit=False)
