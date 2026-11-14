from app.core.db import db
from app.models.merchant_api import CheckoutOrder
from app.services.checkout_state import state

STATES = {'pending': 'PENDING', 'paid': 'HELD', 'completed': 'RELEASED',
          'disputed': 'DISPUTED', 'refunded': 'REFUNDED', 'cancelled': 'CANCELLED'}


def emit_order(order, event_type, suffix=''):
    if not order.developer_application_id:
        return
    from .webhook_events import enqueue
    from app.models.developer_application import DeveloperApplication
    environment = db.session.get(DeveloperApplication, order.developer_application_id).environment
    payload = {'id': order.id, 'order_id': order.client_reference, 'environment': environment,
               'state': STATES[state(order)], 'amount_cents': order.amount_cents, 'currency': order.currency}
    if event_type.startswith('payment.'):
        payload['payment_state'] = 'FAILED' if event_type == 'payment.failed' else 'PENDING'
    enqueue(order.developer_application_id, event_type, payload,
            event_id=f'dev-{order.developer_application_id}-{order.id}-{event_type}-{suffix}')


def payment_event(payment, action, suffix=''):
    if not (payment.rules.get('sandbox_application_id') or payment.rules.get('developer_application_id')):
        return
    order = CheckoutOrder.query.filter_by(escrow_id=payment.escrow_id).first()
    if not order:
        return
    event_type = {'checkout_paid': 'escrow.held', 'delivery_confirmed': 'escrow.released',
                  'buyer_confirmed': 'escrow.released', 'dispute_opened': 'escrow.disputed'}.get(action)
    if action == 'dispute_resolved':
        event_type = {'released': 'escrow.released', 'refunded': 'escrow.refunded'}.get(payment.escrow.status)
    if event_type:
        emit_order(order, event_type, suffix)
