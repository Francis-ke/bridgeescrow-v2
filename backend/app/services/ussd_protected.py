from app.core.db import db
from app.models import Escrow
from app.models.protected_payment import ProtectedPayment
from app.services import ussd_helpers as h
from app.services.protected.common import load, require
from app.services.protected.dispatch import ACTIONS


def listing(phone, steps):
    user = h.user_by_phone(phone)
    rows = ProtectedPayment.query.join(Escrow).filter(
        (Escrow.buyer_id == user.id) | (Escrow.seller_id == user.id)).order_by(ProtectedPayment.id.desc()).limit(4).all()
    if not rows:
        return 'END No protected orders yet. Create one on the website.'
    return 'END ' + '\n'.join(f'{row.escrow.reference} {row.category} {row.state}' for row in rows)


def manage(phone, steps):
    if len(steps) == 1:
        return 'CON Enter protected escrow reference (ESC...)'
    if len(steps) == 2:
        return 'CON 1. Accept terms\n2. Fund from wallet\n3. Confirm service\n4. Open dispute'
    action = {'1': 'accept', '2': 'fund', '3': 'confirm', '4': 'dispute'}.get(steps[2])
    require(action, 'Invalid action', 422)
    if action == 'dispute' and len(steps) == 3:
        return 'CON Explain the issue (at least 10 characters)'
    user = h.user_by_phone(phone)
    escrow = Escrow.query.filter_by(reference=steps[1].upper()).first()
    require(escrow, 'Escrow not found', 404)
    with db.session.begin_nested():
        payment = load(escrow.id, user.id)
        require(payment.rules['release'] != 'delivery_code' or action == 'dispute',
                'Website orders require the buyer delivery code on the website')
        data = {'reason': steps[3]} if action == 'dispute' else {}
        ACTIONS[action](payment, user.id, data)
    return f'END {escrow.reference}: {payment.state}. View full details on the website.'
