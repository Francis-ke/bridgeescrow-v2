import hmac
from flask import Blueprint, current_app, request, Response
from marshmallow import Schema, fields, validate
from app.core.decorators import login_required
from app.core.errors import ApiError
from app.core.jwt import current_user_id
from app.core.db import db
from app.models import User
from app.services.phone_numbers import require_verified
from app.services.ussd_gateway import run

bp = Blueprint('ussd', __name__, url_prefix='/api/ussd')


class SimulationSchema(Schema):
    session_id = fields.String(required=True, validate=validate.Length(min=8, max=80))
    text = fields.String(load_default='', validate=validate.Length(max=500))


@bp.post('')
@bp.post('/gateway/<token>')
def ussd(token=''):
    expected = current_app.config['USSD_CALLBACK_TOKEN']
    given = token or request.headers.get('X-USSD-Token', '')
    if not expected or not hmac.compare_digest(expected, given):
        raise ApiError('USSD gateway authentication required', 401, 'unauthorized')
    data = request.form or request.get_json(silent=True) or {}
    service = current_app.config['USSD_SERVICE_CODE']
    if service and data.get('serviceCode') != service:
        raise ApiError('Unknown USSD service code', 403, 'invalid_service_code')
    from app.services.phone_numbers import find
    user = find(str(data.get('phoneNumber', '')))
    if user:
        require_verified(user, live=current_app.config['USSD_ENVIRONMENT'] == 'live' or current_app.config['PAYMENT_MODE'] == 'daraja_live')
    try:
        reply = run(str(data.get('phoneNumber', '')), str(data.get('text', '')),
                    'gateway-' + str(data.get('sessionId', '')) if data.get('sessionId') else '')
    except ApiError as error:
        reply = 'END ' + error.message
    return Response(reply, mimetype='text/plain')


@bp.post('/simulate')
@login_required
def simulate():
    data = SimulationSchema().load(request.get_json(silent=True) or {})
    user = db.session.get(User, current_user_id())
    phone = require_verified(user, live=current_app.config['PAYMENT_MODE'] == 'daraja_live')
    from app.services.channel_limits import consume
    consume(user.id, 'ussd_simulation', limit=60, seconds=60)
    reply = run(phone, data['text'], 'web-' + str(user.id) + '-' + data['session_id'])
    return {'reply': reply, 'phone': phone, 'simulated_transport': True}
