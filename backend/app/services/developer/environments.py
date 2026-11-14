from flask import current_app
from app.core.errors import ApiError


def live_enabled():
    cfg = current_app.config
    return cfg.get('DEVELOPER_LIVE_ENABLED') and cfg['PAYMENT_MODE'] == 'daraja_live'


def require_environment(environment, user=None):
    if environment == 'sandbox':
        return
    if environment != 'production' or not live_enabled():
        raise ApiError('Production applications are disabled until live M-PESA is configured', 422, 'environment_disabled')
    if user:
        from app.services.phone_numbers import require_verified
        require_verified(user, live=True)
    from app.services.live_ledger import verify_clean
    verify_clean()
