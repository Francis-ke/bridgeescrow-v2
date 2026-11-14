import http.client
import socket
import ssl
import time
from .webhook_urls import validate_url
from .webhook_socket import DeadlineSocket


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, port, resolved, timeout=10):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self.resolved = resolved

    def connect(self):
        deadline = time.monotonic() + self.timeout
        family, _, _, _, address = self.resolved
        connection = socket.socket(family, socket.SOCK_STREAM)
        try:
            connection.settimeout(self.timeout)
            connection.connect(address)
            connection.settimeout(max(0.01, deadline - time.monotonic()))
            wrapped = self._context.wrap_socket(connection, server_hostname=self.host)
            self.sock = DeadlineSocket(wrapped, deadline)
        except Exception:
            connection.close()
            raise


def send(url, body, headers):
    host, port, path, addresses = validate_url(url)
    connection = PinnedHTTPSConnection(host, port, addresses[0])
    try:
        connection.request('POST', path, body=body, headers=headers)
        response = connection.getresponse()
        response.read(1024)
        return response.status
    finally:
        connection.close()
