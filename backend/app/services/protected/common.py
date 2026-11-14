from datetime import timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.db import db
from app.core.errors import ApiError
from app.models import User, Escrow
from app.models.mixins import utcnow
from app.models.protected_payment import ProtectedPayment, ProtectedEvent
from app.services.notifications import add


def require(condition, message, status=409):
    if not condition:
        raise ApiError(message, status, 'protected_rule')


def utc(value):
    require(value.tzinfo is not None, 'Include a timezone in all dates', 422)
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def cents(value):
    result = int(value * 100)
    require(value == Decimal(result) / 100,
            'Use at most two decimal places', 422)
    return result


def load(eid, uid, admin=False, readonly=False):
    from .transactions import load_locked
    return load_locked(eid, uid, admin, readonly)


def event(payment, uid, action, detail=''):
    record = ProtectedEvent(payment_id=payment.id, actor_id=uid, action=action, detail=detail)
    db.session.add(record)
    db.session.flush()
    from app.services.developer.lifecycle import payment_event
    payment_event(payment, action, str(record.id))
    for recipient in (payment.escrow.buyer_id, payment.escrow.seller_id):
        if recipient != uid:
            add(recipient, payment.escrow, f'protected-{record.id}-{recipient}',
                f'{payment.escrow.title}: {action.replace("_", " ")}. {detail[:160]}')


def legacy_guard(escrow):
    require(not escrow.protection, 'Use the protected-payment workflow for this transaction')


def booking_available(payment):
    if payment.category != 'booking':
        return
    provider = payment.escrow.seller_id
    db.session.execute(select(User).where(User.id == provider).with_for_update()).scalar_one()
    conflict = ProtectedPayment.query.join(Escrow).filter(Escrow.seller_id == provider,
        ProtectedPayment.id != payment.id, ProtectedPayment.category == 'booking',
        ProtectedPayment.provider_accepted.is_(True),
        ProtectedPayment.state.notin_(['cancelled', 'completed']),
        ProtectedPayment.booking_start < payment.booking_end,
        ProtectedPayment.booking_end > payment.booking_start).with_for_update().first()
    require(not conflict, 'Provider is already reserved for these dates')
