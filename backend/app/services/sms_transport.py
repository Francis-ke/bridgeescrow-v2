import json
from urllib.parse import urlencode
from urllib.request import Request
from .provider_http import open_request
from flask import current_app


def send(phone, message, environment=None):
    cfg = current_app.config
    if not cfg.get('AT_USERNAME') or not cfg.get('AT_API_KEY'):
        raise ValueError('SMS credentials are missing')
    environment = environment or cfg['AT_ENVIRONMENT']
    if environment not in ('sandbox', 'live'):
        raise ValueError('Invalid SMS environment')
    host = 'api.sandbox.africastalking.com' if environment == 'sandbox' else 'api.africastalking.com'
    payload = {'username': cfg['AT_USERNAME'], 'to': '+' + phone, 'message': message}
    if cfg['AT_SENDER_ID']:
        payload['from'] = cfg['AT_SENDER_ID']
    request = Request('https://' + host + '/version1/messaging', data=urlencode(payload).encode(),
                      headers={'apiKey': cfg['AT_API_KEY'], 'Accept': 'application/json'})
    with open_request(request, timeout=15) as response:
        data = json.load(response)
    recipients = data.get('SMSMessageData', {}).get('Recipients', [])
    if len(recipients) != 1 or recipients[0].get('statusCode') != 101:
        raise ValueError('SMS provider did not accept the message')
    return recipients[0]['messageId']
