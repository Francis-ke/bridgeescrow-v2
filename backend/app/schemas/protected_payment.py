from decimal import Decimal
from marshmallow import Schema, fields, validate
from app.services.protected.rules import CATEGORIES


def money():
    return fields.Decimal(required=True, allow_nan=False, validate=validate.Range(
        min=Decimal('10'), max=Decimal('5000000')))


class MilestoneSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=3, max=140))
    amount = money()
    deadline = fields.DateTime(required=True)


class ProtectedCreateSchema(Schema):
    password = fields.String(load_default=None, allow_none=True, load_only=True, validate=validate.Length(max=256))
    category = fields.String(required=True, validate=validate.OneOf(list(CATEGORIES)))
    provider_id = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    title = fields.String(required=True, validate=validate.Length(min=3, max=140))
    description = fields.String(required=True, validate=validate.Length(min=20, max=10000))
    amount = money()
    deadline = fields.DateTime(required=True)
    booking_start = fields.DateTime(allow_none=True, load_default=None)
    booking_end = fields.DateTime(allow_none=True, load_default=None)
    rules = fields.Dict(required=True)
    milestones = fields.List(fields.Nested(MilestoneSchema), load_default=list,
                             validate=validate.Length(max=12))
