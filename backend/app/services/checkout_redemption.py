from app.core.db import db
from app.models import Escrow
from app.services.protected.common import require, load
from .checkout_codes import valid
from .checkout_settlement import complete


def redeem(order, seller, payload):
    require(order.seller_id == seller.id, 'Order not found', 404)
    require(isinstance(payload, dict), 'Submit a JSON object', 422)
    if order.state == 'completed':
        return {'state': 'completed', 'escrow_id': order.escrow_id}
    require(order.state == 'paid', 'Only secured payments can be completed')
    escrow = db.session.get(Escrow, order.escrow_id)
    party = escrow.seller_id if order.developer_application_id else seller.id
    payment = load(order.escrow_id, party)
    require(payment.escrow.status == 'funded' and payment.state == 'funded', 'Payment is disputed or unavailable for release')
    valid(order, payload.get('code'))
    return complete(order, payment, seller.id)
