from decimal import Decimal
from marshmallow import Schema, fields, validate
from .integration_common import digest, require, safe_url
import json


class ItemSchema(Schema):
    description = fields.String(required=True, validate=validate.Length(min=1, max=140))
    quantity = fields.Integer(required=True, strict=True, validate=validate.Range(min=1, max=1000))
    unit_amount = fields.Decimal(required=True, allow_nan=False,
        validate=validate.Range(min=Decimal('.01'), max=Decimal('5000000')))


class OrderSchema(Schema):
    order_id = fields.String(required=True, validate=validate.Length(min=1, max=100))
    items = fields.List(fields.Nested(ItemSchema), required=True, validate=validate.Length(min=1, max=50))
    currency = fields.String(load_default='KES', validate=validate.OneOf(['KES']))
    duration_hours = fields.Integer(load_default=72, strict=True, validate=validate.Range(min=1, max=2160))
    return_url = fields.String(load_default='', validate=validate.Length(max=500))


def prepare(payload):
    data = OrderSchema().load(payload)
    require(bool(data['order_id'].strip()), 'Enter an order reference', 422)
    require(not data['return_url'] or safe_url(data['return_url']), 'Invalid return URL', 422)
    items = []
    for item in data['items']:
        require(bool(item['description'].strip()), 'Enter item descriptions', 422)
        value = item['unit_amount'] * 100
        require(value == int(value), 'Use at most two decimal places', 422)
        items.append({'description': item['description'], 'quantity': item['quantity'],
                      'unit_amount': str(item['unit_amount']), 'line_cents': int(value) * item['quantity']})
    total = sum(item['line_cents'] for item in items)
    require(1000 <= total <= 500000000, 'Order total must be KES 10–5,000,000', 422)
    fingerprint = digest(json.dumps({**data, 'items': items}, sort_keys=True))
    return data, items, total, fingerprint
