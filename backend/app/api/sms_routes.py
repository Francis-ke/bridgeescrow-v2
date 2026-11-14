from flask import Blueprint, current_app
from app.core.errors import ApiError
from app.core.decorators import login_required
from app.api.phone_routes import messages, sms_test

bp = Blueprint('sms', __name__, url_prefix='/api/sms')
bp.add_url_rule('/messages', view_func=messages, methods=['GET'])
bp.add_url_rule('/test', view_func=sms_test, methods=['POST'])


@bp.post('/simulate')
@login_required
def simulate():
    if current_app.config['SMS_MODE'] != 'simulated':
        raise ApiError('SMS simulation is disabled in provider mode; use /api/sms/test to request a real test message', 403, 'simulation_disabled')
    return sms_test()
