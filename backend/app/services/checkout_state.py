from app.core.db import db
from app.models import Escrow


def state(order):
    escrow = db.session.get(Escrow, order.escrow_id) if order.escrow_id else None
    if escrow:
        return {'released': 'completed', 'refunded': 'refunded', 'cancelled': 'cancelled',
                'disputed': 'disputed'}.get(escrow.status, order.state)
    return order.state
