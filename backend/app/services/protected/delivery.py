from datetime import timedelta
from marshmallow import Schema, fields, validate
from app.models import User
from app.models.mixins import utcnow
from app.schemas.protected_payment import money
from .create import create
from .common import require
from .rules import defaults


class DeliverySchema(Schema):
    provider_id = fields.Integer(load_default=None, allow_none=True, strict=True, validate=validate.Range(min=1))
    recipient_card = fields.String(load_default=None, allow_none=True, validate=validate.Regexp(r'^\d{16}$'))
    account_holder = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    duration_hours = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=2160))
    amount = money()
    password = fields.String(load_default=None, allow_none=True, load_only=True, validate=validate.Length(max=256))


def create_delivery(uid, payload):
    data = DeliverySchema().load(payload)
    by_card = bool(data['recipient_card'])
    provider_id = data['provider_id']
    if by_card:
        provider = User.query.filter_by(card_number=data['recipient_card']).first()
        require(provider is not None, 'Receiving account card number was not found', 404)
        require(provider_id is None or provider_id == provider.id, 'Receiving account does not match the card', 422)
        if data['account_holder'] is not None:
            normalize = lambda value: ' '.join(value.casefold().split())
            require(normalize(data['account_holder']) == normalize(provider.full_name),
                    'Account holder name does not match the receiving account', 422)
        provider_id = provider.id
    require(provider_id is not None, 'Enter the receiving account card number', 422)
    deadline = (utcnow() + timedelta(hours=data['duration_hours'])).isoformat() + 'Z'
    return create(uid, {'category': 'delivery', 'provider_id': provider_id,
        'amount': data['amount'], 'password': data['password'], 'deadline': deadline,
        'title': 'Delivery payment',
        'description': 'Protected delivery payment. The provider submits delivery confirmation and the client approves release.',
        'rules': {**defaults('delivery'), 'cancellation_deadline': deadline}}, confirm_by_card=by_card)
