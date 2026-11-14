import hmac
from flask import Blueprint, request, current_app
from app.core.errors import ApiError
from app.services.mpesa_collection import callback

bp = Blueprint('callbacks', __name__, url_prefix='/api/callbacks')


@bp.post('/mpesa')
@bp.post('/mpesa/<token>')
@bp.post('/mpesa/<reference>/<token>')
def mpesa_callback(token='', reference=None):
    cfg = current_app.config
    expected = cfg['MPESA_CALLBACK_TOKEN']
    given = token or request.headers.get('X-Callback-Secret', '')
    if not expected or not hmac.compare_digest(expected, given):
        raise ApiError('Callback authentication required', 401, 'unauthorized')
    if cfg['PAYMENT_MODE'] not in ('daraja_sandbox', 'daraja_live'):
        raise ApiError('Provider callbacks are disabled in simulation mode', 403, 'provider_disabled')
    pay = callback(request.get_json(silent=True) or {}, reference=reference)
    return {'ResultCode': 0, 'ResultDesc': 'Accepted', 'payment': pay.to_dict()}
