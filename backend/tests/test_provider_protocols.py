from io import BytesIO
import json
from types import SimpleNamespace
from urllib.parse import parse_qs
from tests.conftest import auth
from tests.test_mpesa_provider import configured, callback


def test_stk_protocol_has_payer_amount_secret_callback_and_bearer_token(app, monkeypatch):
    app.config.update(PAYMENT_MODE='daraja_sandbox', MPESA_SHORTCODE='174379', MPESA_PASSKEY='pass',
        MPESA_CONSUMER_KEY='key', MPESA_CONSUMER_SECRET='secret',
        MPESA_CALLBACK_URL='https://example.com/api/callbacks/mpesa', MPESA_CALLBACK_TOKEN='callback-token')
    from app.services.providers import daraja
    calls = []
    def fake(path, payload=None, headers=None):
        calls.append((path, payload, headers))
        return {'access_token': 'access'} if path.startswith('/oauth') else {'ResponseCode': '0'}
    monkeypatch.setattr(daraja, 'request_json', fake)
    daraja.stk(SimpleNamespace(reference='PAYTEST', amount_cents=10000, msisdn='254711111111'))
    path, payload, headers = calls[-1]
    assert path == '/mpesa/stkpush/v1/processrequest'
    assert payload['Amount'] == 100 and payload['PhoneNumber'] == '254711111111'
    assert payload['CallBackURL'].endswith('/PAYTEST/callback-token')
    assert headers['Authorization'] == 'Bearer access'


def test_sms_protocol_preserves_enqueued_environment_and_checks_provider_acceptance(app, monkeypatch):
    from app.services import sms_transport
    app.config.update(AT_USERNAME='sandbox', AT_API_KEY='key', AT_ENVIRONMENT='live')
    seen = []
    def fake(request, timeout):
        seen.append(request)
        return BytesIO(json.dumps({'SMSMessageData': {'Recipients': [{'statusCode': 101, 'messageId': 'sms-1'}]}}).encode())
    monkeypatch.setattr(sms_transport, 'open_request', fake)
    assert sms_transport.send('254711111111', 'BridgeEscrow test', 'sandbox') == 'sms-1'
    assert seen[0].full_url == 'https://api.sandbox.africastalking.com/version1/messaging'
    assert parse_qs(seen[0].data.decode())['to'] == ['+254711111111']


def test_callback_can_confirm_before_stk_response_is_saved(app, client, buyer, monkeypatch):
    headers = configured(app, client, buyer, monkeypatch)
    from app.services.mpesa_results import callback as receive
    def early(pay):
        result = receive(callback(), reference=pay.reference)
        assert result.status == 'confirmed'
        return {'ResponseCode': '0', 'CheckoutRequestID': 'ws_provider_1'}
    monkeypatch.setattr('app.services.providers.daraja.stk', early)
    response = client.post('/api/payments/stk-push', headers=headers, json={'amount': '100'})
    assert response.status_code == 202 and response.json['payment']['status'] == 'confirmed'
    assert client.get('/api/wallet', headers=auth(buyer)).json['wallet']['available'] == '100.00'
