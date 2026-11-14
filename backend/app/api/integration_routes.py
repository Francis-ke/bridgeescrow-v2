from flask import Blueprint, request
from app.core.db import db
from app.models.merchant_api import MerchantApiKey, CheckoutOrder, IntegrationProfile
from app.services.integration_common import seller, require, lock_order
from app.services.integration_keys import create_key, describe, revoke
from app.services.integration_orders import create, public
from app.services.checkout_redemption import redeem

bp = Blueprint('integration', __name__, url_prefix='/api')


@bp.get('/seller/api')
def settings():
    user = seller()
    profile = db.session.get(IntegrationProfile, user.id)
    return {'profile': {'business_name': profile.business_name, 'website': profile.website,
        'contact_email': profile.contact_email} if profile else None,
        'keys': [describe(row) for row in MerchantApiKey.query.filter_by(user_id=user.id).order_by(MerchantApiKey.id.desc())]}


@bp.post('/seller/api/keys')
def new_key():
    return create_key(seller(), request.get_json(silent=True) or {}), 201


@bp.delete('/seller/api/keys/<int:kid>')
def delete_key(kid):
    return revoke(seller(), kid)


@bp.route('/integrations/orders', methods=['POST'])
@bp.route('/seller/orders', methods=['POST'])
def new_order():
    user = seller(api=request.path.startswith('/api/integrations/'))
    return {'order': public(create(user, request.get_json(silent=True) or {}))}, 201


@bp.get('/seller/orders')
def orders():
    user = seller()
    rows = CheckoutOrder.query.filter_by(seller_id=user.id, developer_application_id=None).order_by(CheckoutOrder.id.desc()).limit(50).all()
    return {'orders': [{**public(row), 'buyer': row.buyer_snapshot, 'escrow_id': row.escrow_id} for row in rows]}


@bp.get('/integrations/orders/<int:oid>')
def integration_status(oid):
    user = seller(api=True)
    row = CheckoutOrder.query.filter_by(id=oid, seller_id=user.id, developer_application_id=None).first()
    require(row is not None, 'Order not found', 404)
    return {'order': {**public(row), 'buyer': row.buyer_snapshot, 'escrow_id': row.escrow_id}}


@bp.post('/integrations/orders/<int:oid>/redeem')
@bp.post('/seller/orders/<int:oid>/redeem')
def redeem_delivery(oid):
    user = seller(api=request.path.startswith('/api/integrations/'))
    order = lock_order(oid=oid)
    require(order.developer_application_id is None, 'Order not found', 404)
    return redeem(order, user, request.get_json(silent=True) or {})
