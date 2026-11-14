import re
from app.core.db import db
from app.models.mixins import MoneyMixin, utcnow
from app.services.protected.common import require
from app.services import payment_service
from .sandbox import parties


def ensure_active(order):
    from app.models.developer_application import DeveloperApplication
    application = db.session.get(DeveloperApplication, order.developer_application_id)
    require(application and application.active,
            'This sandbox application is unavailable', 403)
    from .environments import require_environment
    require_environment(application.environment)
    return application


def validate_method(data):
    if data['method'] == 'mpesa':
        phone = data.get('phone_number', '').lstrip('+')
        require(bool(re.fullmatch(r'(?:254|0)[17]\d{8}', phone)), 'Enter a valid Kenyan phone number', 422)


def record_payment(order, protected, data):
    intent = payment_service.start(protected.escrow.buyer_id, MoneyMixin.from_cents(order.amount_cents),
        data.get('phone_number', '') or 'sandbox-card',
        kind='stk_push' if data['method'] == 'mpesa' else 'card', commit=False)
    payment_service.confirm(intent.id, credit_wallet=False, commit=False)
    return intent


def failure(order, buyer, data):
    from .lifecycle import emit_order
    application = ensure_active(order)
    require(application.environment == 'sandbox', 'Simulation is disabled for live orders', 403)
    require(order.state == 'pending' and order.expires_at > utcnow(), 'Checkout is unavailable')
    require(isinstance(data, dict) and data.get('method') in ['card', 'mpesa'], 'Choose a payment method', 422)
    buyer_id, _ = parties(order, buyer)
    intent = payment_service.start(buyer_id, MoneyMixin.from_cents(order.amount_cents),
        'sandbox-failure', kind='stk_push' if data['method'] == 'mpesa' else 'card', commit=False)
    payment_service.fail(intent.id, commit=False)
    emit_order(order, 'payment.failed', suffix=str(intent.id))
    db.session.commit()
    return {'state': 'failed', 'retry_allowed': True, 'message': 'Sandbox payment failed. No funds moved.'}
