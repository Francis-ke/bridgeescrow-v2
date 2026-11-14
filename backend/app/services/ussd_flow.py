from app.services import ussd_actions as act
from app.services import ussd_protected as protected
from app.services.ussd_deposit import deposit

MENU = ("Karibu BridgeEscrow\n1. Check balance\n2. Send protected money\n"
        "3. Release escrow\n4. My escrows\n5. Register\n"
        "6. Protected orders\n7. Manage protected order\n8. M-PESA deposit")


def run_session(phone: str, text: str):
    steps = [s.strip() for s in text.split("*") if s.strip() != ""]
    handlers = {"1": act.balance, "2": act.send, "3": act.release,
                "4": act.list_escrows, "5": act.register, "6": protected.listing,
                "7": protected.manage, "8": deposit}
    if not steps:
        return "CON " + MENU
    handler = handlers.get(steps[0])
    if handler is None:
        return "END Invalid option. Dial again."
    try:
        return handler(phone, steps)
    except Exception:
        from app.core.db import db
        db.session.rollback()
        return "END Sorry, the service is busy. Try again later."
