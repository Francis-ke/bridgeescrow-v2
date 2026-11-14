import secrets
from datetime import timedelta
from app.core.db import db
from app.models import Escrow
from app.models.protected_payment import ProtectedPayment, WorkMilestone
from app.models.mixins import utcnow
from app.services.wallet_service import wallet_for
from app.services.protected import ledger
from app.services.protected.rules import defaults
from app.services.developer.sandbox import parties


def create(order, buyer, provider_payment=None):
    buyer_id, seller_id = parties(order, buyer)
    deadline = utcnow() + timedelta(hours=order.duration_hours)
    escrow = Escrow(reference=Escrow.new_reference(), buyer_id=buyer_id, seller_id=seller_id,
        amount_cents=order.amount_cents, fee_cents=order.amount_cents // 100,
        title=('Order ' + (order.client_reference or order.external_id))[:140], status='funded')
    db.session.add(escrow)
    db.session.flush()
    rules = {**defaults('delivery'), 'release': 'delivery_code', 'late_refund_percent': 100,
             'cancellation_deadline': deadline.isoformat() + 'Z'}
    if order.developer_application_id:
        key = 'developer_application_id' if provider_payment else 'sandbox_application_id'
        rules[key] = order.developer_application_id
    payment = ProtectedPayment(escrow_id=escrow.id, category='delivery', state='funded',
        description='Website purchase: ' + ', '.join(item['description'] for item in order.items),
        client_accepted=True, provider_accepted=True, deadline_at=deadline, rules=rules)
    db.session.add(payment)
    db.session.flush()
    db.session.add(WorkMilestone(payment_id=payment.id, title='Package delivery',
                                amount_cents=order.amount_cents, deadline_at=deadline))
    wallet = wallet_for(buyer_id)
    ledger.lock_wallets(wallet)
    wallet.available_cents += order.amount_cents
    batch = 'CK-' + secrets.token_hex(10)
    ledger.line(wallet, payment, 'debit', order.amount_cents, 'external', 'deposit', batch)
    entry = ledger.line(wallet, payment, 'credit', order.amount_cents, 'available', 'deposit', batch)
    if provider_payment:
        entry.idempotency_key = 'pay-' + provider_payment.reference
    ledger.fund(payment)
    return payment
