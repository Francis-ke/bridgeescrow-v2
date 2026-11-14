from marshmallow import Schema, fields, validate, EXCLUDE


class AmountSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # extra fields (e.g. pin) are handled separately
    amount = fields.Decimal(required=True, places=2, as_string=True)
    idempotency_key = fields.Str(load_default=None)


class EscrowCreateSchema(Schema):
    seller_account = fields.Str(required=True, validate=validate.Length(equal=9))
    amount = fields.Decimal(required=True, places=2, as_string=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=140))
