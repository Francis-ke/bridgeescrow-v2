from flask import Blueprint, request
from marshmallow import Schema, fields, validate
from app.services.protected.common import require
from app.services.developer.authentication import authenticate
from app.services.developer.applications import owned_app
from app.services.developer.orders import scoped, describe
from app.services.developer.checkout import validate_method
from app.services.developer.sandbox import overview
from app.models.merchant_api import CheckoutOrder
from app.models.mixins import utcnow

bp = Blueprint('developer_checkout', __name__, url_prefix='/api/v1')


class SessionSchema(Schema):
    escrow_id = fields.Integer(required=True, strict=True)
    method = fields.String(load_default='card', validate=validate.OneOf(['card', 'mpesa']))
    phone_number = fields.String(load_default='', validate=validate.Length(max=20))


@bp.post('/checkout/sessions')
def create_session():
    application, _ = authenticate('checkout:write')
    data = SessionSchema().load(request.get_json(silent=True) or {})
    order = scoped(application, data['escrow_id'])
    require(order.expires_at > utcnow() or order.state != 'pending', 'Checkout has expired', 410)
    from app.services.developer.checkout import ensure_active
    application = ensure_active(order)
    require(application.environment != 'production' or data['method'] == 'mpesa', 'Live card charging is not configured', 422)
    if data['phone_number']:
        validate_method(data)
    return {'checkout_session': {'url': describe(order)['checkout_url'] + '?method=' + data['method'],
        'escrow_id': order.id, 'method': data['method'], 'environment': application.environment}} , 201


@bp.get('/developer/apps/<identifier>/sandbox')
def sandbox_overview(identifier):
    application = owned_app(identifier)
    require(application.environment == 'sandbox', 'Use your account wallet for production balances', 422)
    rows = CheckoutOrder.query.filter_by(developer_application_id=application.id).order_by(CheckoutOrder.id.desc()).limit(30).all()
    return {**overview(application.id), 'transactions': [describe(row) for row in rows]}
