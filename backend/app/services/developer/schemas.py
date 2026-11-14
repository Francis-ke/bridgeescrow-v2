from urllib.parse import urlsplit
from marshmallow import Schema, fields, validate, validates, ValidationError

PERMISSIONS = ['escrow:read', 'escrow:write', 'checkout:write', 'dispute:write', 'release:request']


class StrictBoolean(fields.Boolean):
    def _deserialize(self, value, attr, data, **kwargs):
        if type(value) is not bool:
            raise ValidationError('Use true or false')
        return value


class ApplicationSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    description = fields.String(required=True, validate=validate.Length(min=10, max=2000))
    website = fields.String(load_default='', validate=validate.Length(max=500))
    type = fields.String(required=True, validate=validate.OneOf(['website', 'mobile', 'backend']))
    environment = fields.String(load_default='sandbox', validate=validate.OneOf(['sandbox', 'production']))
    active = StrictBoolean(load_default=True)

    @validates('website')
    def website_url(self, value, **kwargs):
        if not value:
            return
        try:
            parsed = urlsplit(value)
        except ValueError:
            raise ValidationError('Enter a valid website URL') from None
        if parsed.scheme not in ['http', 'https'] or not parsed.hostname or parsed.username or parsed.password:
            raise ValidationError('Enter an HTTP or HTTPS website URL')


class CredentialSchema(Schema):
    name = fields.String(load_default='Default key', validate=validate.Length(min=1, max=80))
    permissions = fields.List(fields.String(validate=validate.OneOf(PERMISSIONS)),
                              load_default=lambda: list(PERMISSIONS), validate=validate.Length(min=1, max=5))
