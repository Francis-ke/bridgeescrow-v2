from app.core.errors import ApiError
from .daraja import required, request_json, token


def send(payout):
    cfg = required('MPESA_B2C_INITIATOR', 'MPESA_B2C_SECURITY_CREDENTIAL', 'MPESA_SHORTCODE',
                   'MPESA_B2C_RESULT_URL', 'MPESA_B2C_TIMEOUT_URL', 'MPESA_CALLBACK_TOKEN')
    for name in ('MPESA_B2C_RESULT_URL', 'MPESA_B2C_TIMEOUT_URL'):
        if not cfg[name].startswith('https://'):
            raise ApiError('Payout callback URLs must use public HTTPS', 503, 'payout_unavailable')
    suffix = '/' + payout.reference + '/' + cfg['MPESA_CALLBACK_TOKEN']
    payload = {'InitiatorName': cfg['MPESA_B2C_INITIATOR'],
        'SecurityCredential': cfg['MPESA_B2C_SECURITY_CREDENTIAL'], 'CommandID': 'BusinessPayment',
        'Amount': payout.amount_cents // 100, 'PartyA': cfg['MPESA_SHORTCODE'], 'PartyB': payout.phone,
        'Remarks': payout.reference, 'Occasion': 'BridgeEscrow withdrawal',
        'ResultURL': cfg['MPESA_B2C_RESULT_URL'].rstrip('/') + suffix,
        'QueueTimeOutURL': cfg['MPESA_B2C_TIMEOUT_URL'].rstrip('/') + suffix}
    return request_json('/mpesa/b2c/v1/paymentrequest', payload, {'Authorization': 'Bearer ' + token()})
