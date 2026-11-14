import hmac
from flask import Blueprint, current_app, request
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.core.errors import ApiError
from app.models.payout import Payout
from app.services.payouts import initiate
from app.services.payout_results import finish

bp = Blueprint('payouts', __name__, url_prefix='/api/payouts')


@bp.post('')
@login_required
def create():
    payout = initiate(current_user_id(), request.get_json(silent=True) or {})
    return {'payout': payout.to_dict()}, 202


@bp.get('')
@login_required
def listing():
    rows = Payout.query.filter_by(user_id=current_user_id()).order_by(Payout.id.desc()).limit(30).all()
    return {'payouts': [row.to_dict() for row in rows]}


@bp.post('/result/<reference>/<token>')
@bp.post('/timeout/<reference>/<token>')
def result(reference, token):
    cfg = current_app.config
    expected = cfg['MPESA_CALLBACK_TOKEN']
    if cfg['PAYMENT_MODE'] != 'daraja_live' or not expected or not hmac.compare_digest(token, expected):
        raise ApiError('Payout callback authentication required', 401, 'unauthorized')
    finish(reference, request.get_json(silent=True) or {}, timeout='/timeout/' in request.path)
    return {'ResultCode': 0, 'ResultDesc': 'Accepted'}
