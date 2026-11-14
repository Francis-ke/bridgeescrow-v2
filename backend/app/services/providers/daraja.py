import base64
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request
from app.services.provider_http import open_request
from urllib.error import HTTPError, URLError
from flask import current_app
from app.core.errors import ApiError


def required(*names):
    cfg = current_app.config
    if any(not cfg.get(name) for name in names):
        raise ApiError('Configure the M-PESA provider fields in backend/.env', 503, 'mpesa_unavailable')
    return cfg


def base_url():
    mode = current_app.config['PAYMENT_MODE']
    if mode not in ('daraja_sandbox', 'daraja_live'):
        raise ApiError('Daraja payments are not enabled', 503, 'mpesa_unavailable')
    return 'https://api.safaricom.co.ke' if mode == 'daraja_live' else 'https://sandbox.safaricom.co.ke'


def request_json(path, payload=None, headers=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(base_url() + path, data=body, headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with open_request(request, timeout=20) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        raise ApiError('M-PESA provider request could not be confirmed. Do not submit a new payment.',
                       502, 'provider_unavailable') from None


def token():
    cfg = required('MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET')
    raw = (cfg['MPESA_CONSUMER_KEY'] + ':' + cfg['MPESA_CONSUMER_SECRET']).encode()
    response = request_json('/oauth/v1/generate?grant_type=client_credentials',
                            headers={'Authorization': 'Basic ' + base64.b64encode(raw).decode()})
    if not response.get('access_token'):
        raise ApiError('M-PESA authentication failed', 503, 'mpesa_unavailable')
    return response['access_token']


def credentials():
    cfg = required('MPESA_SHORTCODE', 'MPESA_PASSKEY')
    timestamp = datetime.now(ZoneInfo('Africa/Nairobi')).strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((cfg['MPESA_SHORTCODE'] + cfg['MPESA_PASSKEY'] + timestamp).encode()).decode()
    return {'BusinessShortCode': cfg['MPESA_SHORTCODE'], 'Password': password, 'Timestamp': timestamp}


def stk(pay):
    cfg = required('MPESA_CALLBACK_URL', 'MPESA_CALLBACK_TOKEN')
    if not cfg['MPESA_CALLBACK_URL'].startswith('https://'):
        raise ApiError('M-PESA requires a public HTTPS callback URL', 503, 'mpesa_unavailable')
    payload = {**credentials(), 'TransactionType': 'CustomerPayBillOnline', 'Amount': pay.amount_cents // 100,
        'PartyA': pay.msisdn, 'PartyB': cfg['MPESA_SHORTCODE'], 'PhoneNumber': pay.msisdn,
        'CallBackURL': cfg['MPESA_CALLBACK_URL'].rstrip('/') + '/' + pay.reference + '/' + cfg['MPESA_CALLBACK_TOKEN'],
        'AccountReference': pay.reference, 'TransactionDesc': 'BridgeEscrow wallet deposit'}
    return request_json('/mpesa/stkpush/v1/processrequest', payload, {'Authorization': 'Bearer ' + token()})


def query(checkout_id):
    return request_json('/mpesa/stkpushquery/v1/query', {**credentials(), 'CheckoutRequestID': checkout_id},
                        {'Authorization': 'Bearer ' + token()})
