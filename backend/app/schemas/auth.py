import re
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError

PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


class RegisterSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    national_id = fields.Str(required=True, validate=validate.Length(min=4, max=32))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    password_confirm = fields.Str(required=True, load_only=True)

    @validates("password")
    def check_password(self, value, **kwargs):
        if not PASSWORD_RE.match(value):
            raise ValidationError("Password needs 8+ chars with letters and numbers")


class LoginSchema(Schema):
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=24))

    @validates_schema
    def identity(self, data, **kwargs):
        if bool(data.get('email')) == bool(data.get('phone')):
            raise ValidationError('Enter either email or verified phone number')
    password = fields.Str(required=True, load_only=True)


class OtpSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True, validate=validate.Regexp(r"^\d{6}$"))
    challenge_id = fields.Str(load_default=None, allow_none=True)


class EmailSchema(Schema):
    email = fields.Email(required=True)


class PasswordResetSchema(OtpSchema):
    @validates("password")
    def check_password(self, value, **kwargs):
        if not PASSWORD_RE.match(value):
            raise ValidationError("Password needs 8+ chars with letters and numbers")

    password = fields.Str(required=True, load_only=True)
    password_confirm = fields.Str(required=True, load_only=True)


class PinSchema(Schema):
    pin = fields.Str(required=True, validate=validate.Regexp(r"^\d{4}$"))


class ProfileSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=3, max=120))

    @validates("full_name")
    def check_name(self, value, **kwargs):
        if len(value.strip()) < 3:
            raise ValidationError("Enter a name with at least 3 characters")
