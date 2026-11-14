from app.core.db import db
from app.models import User, Escrow
from app.models.mixins import utcnow
from app.models.protected_payment import ProtectedPayment, WorkMilestone
from app.schemas.protected_payment import ProtectedCreateSchema
from .rules import defaults, RuleSchema
from .common import require, utc, cents, event


def create(uid, payload, confirm_by_card=False):
    data = ProtectedCreateSchema().load(payload)
    require(len(data['title'].strip()) >= 3 and len(data['description'].strip()) >= 20,
            'Enter a meaningful title and description', 422)
    provider = db.session.get(User, data['provider_id'])
    require(provider and provider.id != uid and provider.is_active and provider.email_verified,
            'Choose another active verified provider', 422)
    category = data['category']
    if category == 'delivery' and not confirm_by_card:
        client = db.session.get(User, uid)
        require(bool(data['password']) and client.check_password(data['password']),
                'Enter your correct account password to confirm the delivery payment', 401)
    rules = RuleSchema().load(data['rules'])
    if category == 'booking':
        require('late_refund_percent' in rules, 'Set the booking late-cancellation refund percentage', 422)
    config = {**defaults(category), **rules}
    cutoff = utc(config['cancellation_deadline'])
    deadline = utc(data['deadline'])
    require(utcnow() < cutoff <= deadline, 'Cancellation deadline must be in the future and before the payment deadline', 422)
    config['cancellation_deadline'] = cutoff.isoformat() + 'Z'
    start = utc(data['booking_start']) if data['booking_start'] else None
    end = utc(data['booking_end']) if data['booking_end'] else None
    if category == 'booking':
        require(start and end and utcnow() < start < end and cutoff <= start,
                'Set future booking dates and a cancellation deadline before the booking starts', 422)
        require(deadline >= end, 'Booking deadline must include the complete service period', 422)
    else:
        require(not start and not end, 'Booking dates apply only to booking payments', 422)
    amount = cents(data['amount'])
    parts = data['milestones']
    require(not parts or category == 'freelancing', 'Milestones are available for freelancing only', 422)
    if parts:
        require(all(len(part['title'].strip()) >= 3 for part in parts), 'Enter meaningful milestone titles', 422)
        require(sum(cents(part['amount']) for part in parts) == amount, 'Milestone amounts must equal the total', 422)
        dates = [utc(part['deadline']) for part in parts]
        require(all(utcnow() < date <= deadline for date in dates), 'Milestone deadlines must fall within the job deadline', 422)
        require(dates == sorted(dates), 'Milestones must be in deadline order', 422)
    escrow = Escrow(reference=Escrow.new_reference(), buyer_id=uid, seller_id=provider.id,
                    amount_cents=amount, fee_cents=amount // 100, title=data['title'].strip(), status='hold')
    db.session.add(escrow)
    db.session.flush()
    payment = ProtectedPayment(escrow_id=escrow.id, category=category,
        description=data['description'].strip(), deadline_at=deadline,
        booking_start=start, booking_end=end, rules=config)
    db.session.add(payment)
    db.session.flush()
    for part in parts or [{'title': data['title'], 'amount': data['amount'], 'deadline': data['deadline']}]:
        db.session.add(WorkMilestone(payment_id=payment.id, title=part['title'].strip(),
                      amount_cents=cents(part['amount']), deadline_at=utc(part['deadline'])))
    event(payment, uid, 'created', 'Both parties must accept the terms before funding.')
    db.session.commit()
    return payment
