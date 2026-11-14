from sqlalchemy import select, text
from sqlalchemy.orm.attributes import set_committed_value
from app.core.db import db
from app.models import Escrow, User
from app.models.protected_payment import ProtectedPayment, WorkMilestone
from .common import require


def load_locked(eid, uid, admin=False, readonly=False):
    if db.engine.dialect.name == 'sqlite' and not readonly:
        connection = db.session.connection().connection.driver_connection
        if not connection.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    parties = db.session.execute(select(Escrow.buyer_id, Escrow.seller_id)
                                 .where(Escrow.id == eid)).first()
    require(parties is not None and (admin or uid in parties), 'Payment not found', 404)
    if not readonly:
        db.session.execute(select(User.id).where(User.id == parties.seller_id).with_for_update()).scalar_one()
    query = select(Escrow).where(Escrow.id == eid).execution_options(populate_existing=True)
    db.session.execute(query if readonly else query.with_for_update()).scalar_one()
    query = select(ProtectedPayment).where(ProtectedPayment.escrow_id == eid)
    query = query.execution_options(populate_existing=True)
    payment = db.session.execute(query if readonly else query.with_for_update()).scalar_one_or_none()
    require(payment is not None, 'Protected payment not found', 404)
    if not readonly:
        items = db.session.execute(select(WorkMilestone).where(WorkMilestone.payment_id == payment.id)
            .order_by(WorkMilestone.id).with_for_update().execution_options(populate_existing=True)).scalars().all()
        set_committed_value(payment, 'milestones', items)
    return payment
