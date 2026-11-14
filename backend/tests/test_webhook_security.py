import socket
import pytest
from app.core.errors import ApiError
from app.services.developer.webhook_urls import validate_url
from app.services.developer import webhook_transport as transport
from tests.webhook_helpers import public_dns


@pytest.mark.parametrize('url', ['http://public.example/hooks', 'https://u:p@public.example/hooks',
    'https://public.example/hooks#fragment', 'https://public.example/\nheader', 'file:///etc/passwd'])
def test_webhook_urls_reject_unsafe_schemes_and_credentials(monkeypatch, url):
    public_dns(monkeypatch)
    with pytest.raises(ApiError):
        validate_url(url)


@pytest.mark.parametrize('address', ['127.0.0.1', '10.0.0.1', '169.254.169.254', '::1', '::ffff:127.0.0.1'])
def test_all_dns_answers_must_be_public(monkeypatch, address):
    monkeypatch.setattr('socket.getaddrinfo', lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, '', (address, 443))])
    with pytest.raises(ApiError):
        validate_url('https://merchant.example/hooks')


def test_tls_uses_validated_ip_but_verifies_original_hostname(monkeypatch):
    connected, verified = [], []
    class FakeSocket:
        def settimeout(self, timeout):
            assert timeout > 0
        def connect(self, address):
            connected.append(address)
        def close(self):
            pass
    class FakeTLS:
        def wrap_socket(self, connection, server_hostname):
            verified.append(server_hostname)
            return connection
    monkeypatch.setattr(transport.socket, 'socket', lambda *a: FakeSocket())
    connection = transport.PinnedHTTPSConnection('merchant.example', 443,
        (socket.AF_INET, 1, 6, '', ('93.184.216.34', 443)))
    connection._context = FakeTLS()
    connection.connect()
    assert connected == [('93.184.216.34', 443)]
    assert verified == ['merchant.example']
    connection.close()
