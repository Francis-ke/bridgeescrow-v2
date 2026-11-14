import hashlib
import secrets
from sqlalchemy import func
from app.core.db import db
from app.models import User, Wallet, Escrow
from app.models.merchant_api import CheckoutOrder
from app.models.protected_payment import ProtectedPayment
from app.models.mixins import MoneyMixin
from app.services.wallet_service import wallet_for


def account(application_id, kind, order_id=0):
    seed = f'{application_id}:{kind}:{order_id}'
    number = 'SB' + hashlib.sha256(seed.encode()).hexdigest()[:14]
    user = User.query.filter_by(account_number=number).first()
    if not user:
        user = User(account_number=number, full_name=f'Sandbox {kind}',
            email=number.lower() + '@bridgeescrow.invalid', phone=number,
            role='system', is_active=False, email_verified=False)
        user.set_password(secrets.token_urlsafe(48))
        db.session.add(user)
        db.session.flush()
    return user


def parties(order, buyer):
    if not order.developer_application_id:
        return buyer.id, order.seller_id
    from app.models.developer_application import DeveloperApplication
    appid = order.developer_application_id
    if db.session.get(DeveloperApplication, appid).environment == 'production':
        return buyer.id, order.seller_id
    return account(appid, 'buyer', order.id).id, account(appid, 'seller').id


def fees(application_id):
    return wallet_for(account(application_id, 'fees').id)


def overview(application_id):
    number = 'SB' + hashlib.sha256(f'{application_id}:seller:0'.encode()).hexdigest()[:14]
    seller = User.query.filter_by(account_number=number).first()
    wallet = Wallet.query.filter_by(user_id=seller.id).first() if seller else None
    held = db.session.query(func.coalesce(func.sum(Wallet.escrow_cents), 0)).join(User).filter(
        User.id.in_(db.session.query(Escrow.buyer_id).join(CheckoutOrder,
            CheckoutOrder.escrow_id == Escrow.id).filter(CheckoutOrder.developer_application_id == application_id))).scalar()
    refunded = db.session.query(func.coalesce(func.sum(ProtectedPayment.refunded_cents), 0)).join(
        CheckoutOrder, CheckoutOrder.escrow_id == ProtectedPayment.escrow_id).filter(
        CheckoutOrder.developer_application_id == application_id).scalar()
    return {'environment': 'sandbox', 'available': MoneyMixin.from_cents(wallet.available_cents if wallet else 0),
        'held': MoneyMixin.from_cents(int(held)), 'refunded': MoneyMixin.from_cents(int(refunded)),
        'production_enabled': False, 'methods': ['card', 'mpesa']}
