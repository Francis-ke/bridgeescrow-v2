from app.core.db import db
from app.models.mixins import utcnow
from app.services.protected import ledger
from app.services.protected.common import event
from app.services.notifications import add


def complete(order, payment, actor_id):
    ledger.distribute(payment, ledger.remaining(payment))
    payment.state, payment.escrow.status = 'completed', 'released'
    payment.milestones[0].state, payment.milestones[0].approved_at = 'approved', utcnow()
    order.state, order.delivery_hash = 'completed', None
    sandbox = bool(payment.rules.get('sandbox_application_id'))
    target = None if sandbox else payment.escrow
    text = 'sandbox balance' if sandbox else 'wallet'
    add(order.seller_id, target, f'checkout-received-{order.id}',
        f'Payment for order {order.client_reference or order.external_id} released to your {text}.')
    if sandbox:
        add(order.buyer_id, None, f'dev-buyer-released-{order.id}', 'Sandbox delivery confirmed; payment released.')
    event(payment, actor_id, 'delivery_confirmed', 'The buyer authorized release of this protected payment.')
    db.session.commit()
    return {'state': 'completed', 'escrow_id': order.escrow_id}
