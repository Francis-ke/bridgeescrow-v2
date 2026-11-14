from marshmallow import Schema, fields, validate

CATEGORIES = {
    'delivery': 'Delivery', 'services': 'Services', 'events': 'Events',
    'deposits': 'Deposits', 'contracts': 'Contracts',
    'freelancing': 'Freelancing Payment', 'booking': 'Booking Payment',
    'other': 'Other Protected Payments',
}


class RuleSchema(Schema):
    release = fields.String(validate=validate.OneOf(
        ['client_approval', 'mutual_confirmation']))
    max_extension_hours = fields.Integer(load_default=168, strict=True, validate=validate.Range(min=1, max=2160))
    max_revisions = fields.Integer(load_default=3, strict=True, validate=validate.Range(min=0, max=20))
    revision_hours = fields.Integer(load_default=48, strict=True, validate=validate.Range(min=1, max=720))
    early_refund_percent = fields.Integer(load_default=100, strict=True, validate=validate.Range(min=0, max=100))
    late_refund_percent = fields.Integer(strict=True, validate=validate.Range(min=0, max=100))
    cancellation_deadline = fields.DateTime(required=True)


def defaults(category):
    return {'release': 'mutual_confirmation' if category == 'booking' else 'client_approval',
            'max_extension_hours': 168, 'max_revisions': 3, 'revision_hours': 48,
            'early_refund_percent': 100, 'late_refund_percent': 0 if category == 'booking' else 80}
