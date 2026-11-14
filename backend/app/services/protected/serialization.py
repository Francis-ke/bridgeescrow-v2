from app.models.protected_payment import ProtectedEvent
from app.models.mixins import MoneyMixin, utcnow
from app.services.escrow_details import iso
from .rules import CATEGORIES
from . import ledger


def summary(payment):
    return {'category': payment.category, 'label': CATEGORIES[payment.category],
        'state': payment.state, 'deadline': iso(payment.deadline_at),
        'released': MoneyMixin.from_cents(payment.released_cents),
        'refunded': MoneyMixin.from_cents(payment.refunded_cents)}


def serialize(payment, uid):
    from .availability import actions
    result = {**summary(payment), 'escrow': payment.escrow.to_dict(),
        'description': payment.description, 'rules': payment.rules,
        'client_accepted': payment.client_accepted, 'provider_accepted': payment.provider_accepted,
        'booking_start': iso(payment.booking_start), 'booking_end': iso(payment.booking_end),
        'reservation_confirmed_at': iso(payment.reservation_confirmed_at),
        'provider_confirmed_at': iso(payment.provider_confirmed_at),
        'client_confirmed_at': iso(payment.client_confirmed_at),
        'earned_fees': MoneyMixin.from_cents(payment.earned_fee_cents),
        'remaining': MoneyMixin.from_cents(ledger.remaining(payment)),
        'extension': payment.extension, 'cancellation': payment.cancellation,
        'overdue': utcnow() > payment.deadline_at and payment.state not in ['completed', 'cancelled'],
        'actions': actions(payment, uid)}
    result['milestones'] = [{'id': item.id, 'title': item.title,
        'amount': MoneyMixin.from_cents(item.amount_cents), 'state': item.state,
        'deadline': iso(item.deadline_at), 'submission': item.submission,
        'revision_reason': item.revision_reason, 'revision_count': item.revision_count,
        'revision_due': iso(item.revision_due_at), 'submitted_at': iso(item.submitted_at),
        'approved_at': iso(item.approved_at)} for item in payment.milestones]
    result['events'] = [{'action': row.action, 'detail': row.detail, 'actor_id': row.actor_id,
                        'at': iso(row.created_at)} for row in ProtectedEvent.query.filter_by(
                            payment_id=payment.id).order_by(ProtectedEvent.id).all()]
    return result
