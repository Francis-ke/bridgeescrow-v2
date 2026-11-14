from sqlalchemy import select, text
from app.core.db import db
from app.models import User, Escrow
from app.models.developer_application import DeveloperApplication
from app.models.merchant_api import CheckoutOrder
from app.services.integration_common import lock_order, require
from app.services.integration_orders import create, public
from .lifecycle import emit_order, STATES
from app.services.checkout_state import state


def lock_app(application):
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    row = db.session.execute(select(DeveloperApplication).where(DeveloperApplication.id == application.id)
        .with_for_update().execution_options(populate_existing=True)).scalar_one()
    require(row.active, 'Application is unavailable', 403)
    from .environments import require_environment
    require_environment(row.environment)
    return row


def scoped(application, oid, locked=False):
    order = lock_order(oid=oid) if locked else db.session.get(CheckoutOrder, oid)
    require(order and order.developer_application_id == application.id, 'Escrow not found', 404)
    return order


def describe(order):
    bill = public(order)
    application = db.session.get(DeveloperApplication, order.developer_application_id)
    return {'id': order.id, 'order_id': order.client_reference, 'environment': application.environment,
        'state': STATES[state(order)], 'amount': bill['amount'], 'currency': bill['currency'],
        'checkout_url': bill['checkout_url'], 'ledger_escrow_id': order.escrow_id,
        'buyer': order.buyer_snapshot, 'duration_hours': order.duration_hours}


def new(application, payload, idempotency_key=''):
    application = lock_app(application)
    from .idempotency import lookup, attach
    previous = lookup(application, payload, idempotency_key)
    if previous:
        db.session.commit()
        return previous
    user = db.session.get(User, application.user_id)
    order = create(user, payload, application=application, commit=False)
    require(application.environment != 'production' or order.amount_cents % 100 == 0, 'Live M-PESA orders require whole KES totals', 422)
    attach(order, idempotency_key)
    if order.state == 'pending':
        emit_order(order, 'payment.pending')
    db.session.commit()
    return order


def protected(order):
    from app.services.protected.common import load
    require(order.escrow_id is not None, 'Payment has not been funded')
    escrow = db.session.get(Escrow, order.escrow_id)
    return load(escrow.id, escrow.seller_id)
