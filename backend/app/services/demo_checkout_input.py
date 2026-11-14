from decimal import Decimal
from marshmallow import Schema, fields, validate
from sqlalchemy import func, or_
from app.models import User
from app.core.errors import ApiError


class CheckoutSchema(Schema):
    kind = fields.String(required=True, validate=validate.OneOf(['buy', 'send', 'deposit', 'withdraw']))
    method = fields.String(required=True, validate=validate.OneOf(['card', 'mpesa']))
    amount = fields.Decimal(required=True, allow_nan=False, validate=validate.Range(min=Decimal('0.01'), max=Decimal('5000000')))
    destination = fields.String(load_default='', validate=validate.Length(max=190))
    recipient_card = fields.String(load_default='', validate=validate.Regexp(r'^\d{16}$|^$'))
    last4 = fields.String(load_default='', validate=validate.Regexp(r'^\d{4}$|^$'))
    idempotency_key = fields.String(required=True, validate=validate.Length(min=16, max=64))


def recipient_for(uid, data, cents):
    recipient = None
    target = data['destination'].strip()
    if data['kind'] == 'send':
        recipient = User.query.filter_by(card_number=data['recipient_card']).first()
    elif data['kind'] == 'buy':
        if not target:
            raise ApiError('Enter the seller account or phone number', 422, 'recipient_required')
        normalized = target.replace(' ', '').lstrip('+')
        if normalized.startswith('0'):
            normalized = '254' + normalized[1:]
        phones = [target, normalized, '+' + normalized]
        if normalized.startswith('254'):
            phones.append('0' + normalized[3:])
        recipient = User.query.filter(or_(func.lower(User.email) == target.lower(),
            User.account_number == target.upper(), User.card_number == target,
            User.phone.in_(phones))).first()
    if (data['kind'] == 'send' or data['kind'] == 'buy' and data['method'] == 'card') and not recipient:
        raise ApiError('Recipient account not found; enter their registered virtual card, email or account number', 404, 'recipient_not_found')
    if recipient and (recipient.id == uid or not recipient.is_active or not recipient.email_verified):
        raise ApiError('Choose another active, verified recipient', 422, 'invalid_recipient')
    if recipient and cents < 1000:
        raise ApiError('Minimum protected payment is KES 10.00', 422, 'invalid_amount')
    if data['method'] == 'mpesa' and not target:
        raise ApiError('Enter an M-PESA phone number', 422, 'phone_required')
    return recipient, target
