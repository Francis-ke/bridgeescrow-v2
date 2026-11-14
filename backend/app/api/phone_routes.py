from flask import Blueprint, current_app, request
from marshmallow import Schema, fields, validate
from app.core.db import db
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.models import User
from app.models.phone_channel import SmsMessage
from app.services import phone_verification, sms
from app.services.channel_limits import consume

bp = Blueprint('phone', __name__, url_prefix='/api/phone')


class PhoneSchema(Schema):
    phone = fields.String(required=True, validate=validate.Length(max=24))


class VerifySchema(Schema):
    challenge_id = fields.String(required=True, validate=validate.Length(max=64))
    otp = fields.String(required=True, validate=validate.Regexp(r'^\d{6}$'))


@bp.post('/verification')
@login_required
def start():
    data = PhoneSchema().load(request.get_json(silent=True) or {})
    return phone_verification.start(db.session.get(User, current_user_id()), data['phone']), 202


@bp.post('/verify')
@login_required
def verify():
    data = VerifySchema().load(request.get_json(silent=True) or {})
    user = phone_verification.verify(db.session.get(User, current_user_id()), data['challenge_id'], data['otp'])
    return {'user': user.to_dict()}


@bp.get('/messages')
@login_required
def messages():
    rows = SmsMessage.query.filter_by(user_id=current_user_id()).order_by(SmsMessage.id.desc()).limit(30).all()
    return {'messages': [sms.describe(row) for row in rows], 'sms_mode': current_app.config['SMS_MODE']}


@bp.post('/sms-test')
@login_required
def sms_test():
    from app.services.phone_numbers import require_verified
    user = db.session.get(User, current_user_id())
    require_verified(user)
    consume(user.id, 'sms_test', limit=3)
    import secrets
    row = sms.queue(user, 'BridgeEscrow test SMS. Your verified phone is connected to your account.',
                    'test-' + secrets.token_hex(16))
    db.session.commit()
    return {'message': sms.describe(row)}, 202


@bp.get('/status')
@login_required
def status():
    cfg = current_app.config
    return {'developer_live_enabled': bool(cfg.get('DEVELOPER_LIVE_ENABLED') and cfg['PAYMENT_MODE'] == 'daraja_live'), 'sms_mode': cfg['SMS_MODE'], 'payment_mode': cfg['PAYMENT_MODE'],
            'ussd_service_code': cfg['USSD_SERVICE_CODE'],
            'sms_configured': all(cfg.get(k) for k in ('AT_USERNAME', 'AT_API_KEY')),
            'ussd_callback_configured': bool(cfg['USSD_CALLBACK_TOKEN']),
            'mpesa_configured': all(cfg.get(k) for k in ('MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET',
                'MPESA_SHORTCODE', 'MPESA_PASSKEY', 'MPESA_CALLBACK_URL', 'MPESA_CALLBACK_TOKEN'))}
