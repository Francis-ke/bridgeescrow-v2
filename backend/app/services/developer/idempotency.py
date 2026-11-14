from app.models.merchant_api import CheckoutOrder
from app.services.integration_bill import prepare
from app.services.protected.common import require


def lookup(application, payload, key):
    require(isinstance(key, str) and len(key) <= 128, 'Idempotency-Key must be at most 128 characters', 422)
    if not key:
        return None
    existing = CheckoutOrder.query.filter_by(developer_application_id=application.id, idempotency_key=key).first()
    if existing:
        require(existing.fingerprint == prepare(payload)[3], 'Idempotency-Key already used for another request', 409)
    return existing


def attach(order, key):
    if key:
        require(not order.idempotency_key or order.idempotency_key == key,
                'Order already associated with another Idempotency-Key', 409)
        order.idempotency_key = key
