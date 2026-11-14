from app.core.db import db
from app.models import User, Payment
from app.models.merchant_api import CheckoutOrder
from app.models.mixins import MoneyMixin
from app.services.protected.common import require, event
from app.services.phone_numbers import require_verified
from app.services.mpesa_collection import initiate


def start(order, session, buyer, data):
    require(data['method'] == 'mpesa', 'Live card charging is not configured. Choose M-PESA.', 422)
    require_verified(buyer, live=True)
    require(not order.buyer_id or order.buyer_id == buyer.id, 'This checkout is reserved for another buyer', 403)
    order.buyer_id = buyer.id
    order.buyer_snapshot = {'name': buyer.full_name, 'email': buyer.email,
        'shipping_name': session.full_name, 'phone': buyer.phone, 'address': session.address}
    failed = Payment.query.filter_by(checkout_order_id=order.id, status='failed').count()
    key = f'checkout-{order.id}-attempt-{failed:08d}'
    intent = initiate(buyer.id, MoneyMixin.from_cents(order.amount_cents), key, checkout_order=order)
    return {'state': 'pending', 'payment': intent.to_dict(),
            'message': 'Confirm the M-PESA prompt. Funds are held only after verified provider confirmation.'}


def fund(intent):
    from app.services.integration_common import lock_order
    from app.services.checkout_funding import create
    from app.services.checkout_codes import prepare
    order = lock_order(oid=intent.checkout_order_id)
    require(order and order.buyer_id, 'Payment has no checkout buyer', 409)
    if order.escrow_id:
        return order
    buyer = db.session.get(User, order.buyer_id)
    payment = create(order, buyer, provider_payment=intent)
    order.escrow_id, order.state = payment.escrow_id, 'paid'
    # The verified buyer requests their delivery code after returning to checkout.
    prepare(order)
    event(payment, buyer.id, 'checkout_paid', 'Provider payment verified; funds secured until buyer confirmation.')
    return order
