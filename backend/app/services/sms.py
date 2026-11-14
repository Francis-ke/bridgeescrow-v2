from flask import current_app
from app.core.db import db
from app.core.errors import ApiError
from app.models.phone_channel import SmsMessage
from .phone_numbers import normalize


def queue(user, message, event_key, phone=None):
    mode = current_app.config['SMS_MODE']
    if mode not in ('simulated', 'africastalking'):
        raise ApiError('SMS provider is not configured', 503, 'sms_unavailable')
    existing = SmsMessage.query.filter_by(event_key=event_key).first()
    if existing:
        return existing
    row = SmsMessage(user_id=user.id, phone=normalize(phone or user.phone), body=message,
                     event_key=event_key, mode=mode, environment=current_app.config['AT_ENVIRONMENT'] if mode == 'africastalking' else 'local', status='simulated' if mode == 'simulated' else 'queued')
    db.session.add(row)
    return row


def describe(row):
    return {'id': row.id, 'phone': row.phone, 'body': row.body if row.mode == 'simulated' else None,
            'mode': row.mode, 'status': row.status, 'attempts': row.attempts,
            'created_at': row.created_at.isoformat()}
