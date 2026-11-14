import secrets
from datetime import timedelta
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app.core.db import db
from app.models.merchant_api import CheckoutOrder, IntegrationProfile
from app.models.mixins import utcnow, MoneyMixin
from .integration_common import require
from .integration_bill import prepare, ItemSchema, OrderSchema


def public(order):
    from .checkout_state import state
    from app.models.developer_application import DeveloperApplication
    app = db.session.get(DeveloperApplication, order.developer_application_id) if order.developer_application_id else None
    return {'mode': 'test', 'id': order.id, 'order_id': order.client_reference or order.external_id,
        'environment': app.environment if app else 'legacy', 'items': order.items,
        'amount': MoneyMixin.from_cents(order.amount_cents), 'currency': order.currency,
        'seller': order.seller_snapshot, 'state': state(order), 'duration_hours': order.duration_hours,
        'checkout_url': current_app.config['PUBLIC_FRONTEND_URL'].rstrip('/') + '/checkout/' + order.public_token,
        'return_url': order.return_url}


def create(user, payload, application=None, commit=True):
    data, items, total, fingerprint = prepare(payload)
    profile = db.session.get(IntegrationProfile, user.id)
    require(application is not None or profile is not None, 'Create a seller API profile first', 409)
    reference = data['order_id']
    if application:
        require(len(reference) <= 80, 'Order reference must be at most 80 characters', 422)
        reference = f'{application.id}:{reference}'
    appid = application.id if application else None
    existing = CheckoutOrder.query.filter_by(seller_id=user.id, external_id=reference, developer_application_id=appid).first()
    if existing:
        require(existing.fingerprint == fingerprint, 'Order ID already used for a different bill', 409)
        return existing
    snapshot = {'name': application.name, 'email': user.email, 'website': application.website} if application else {
        'name': profile.business_name, 'email': profile.contact_email, 'website': profile.website}
    order = CheckoutOrder(seller_id=user.id, external_id=reference, public_token=secrets.token_urlsafe(32),
        fingerprint=fingerprint, items=items, amount_cents=total, duration_hours=data['duration_hours'],
        expires_at=utcnow() + timedelta(hours=24), return_url=data['return_url'], seller_snapshot=snapshot,
        developer_application_id=application.id if application else None,
        client_reference=data['order_id'] if application else None)
    db.session.add(order)
    try:
        db.session.flush()
        if commit:
            db.session.commit()
    except IntegrityError:
        db.session.rollback()
        order = CheckoutOrder.query.filter_by(seller_id=user.id, external_id=reference, developer_application_id=appid).first()
        require(order and order.fingerprint == fingerprint, 'Conflicting order request', 409)
    return order
