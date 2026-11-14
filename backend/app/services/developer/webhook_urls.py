import ipaddress
import socket
from urllib.parse import urlsplit
from app.core.errors import ApiError


def validate_url(value):
    if not isinstance(value, str) or len(value) > 500 or any(ord(char) < 33 for char in value):
        raise ApiError('Enter a valid HTTPS webhook URL', 422, 'invalid_webhook_url')
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        if parsed.scheme != 'https' or not host or parsed.username or parsed.password or parsed.fragment:
            raise ValueError()
        host = host.encode('idna').decode('ascii')
        port = parsed.port or 443
        if not 1 <= port <= 65535 or '%' in host or '\\' in value:
            raise ValueError()
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        if not addresses:
            raise ValueError()
        for _, _, _, _, address in addresses:
            ip = ipaddress.ip_address(address[0])
            if not ip.is_global or ip.is_multicast or ip.is_reserved:
                raise ValueError()
            if ip.version == 6 and ip.ipv4_mapped and not ip.ipv4_mapped.is_global:
                raise ValueError()
    except (ValueError, UnicodeError, OSError):
        raise ApiError('Webhook URLs must resolve only to public HTTPS destinations',
                       422, 'invalid_webhook_url') from None
    return host, port, (parsed.path or '/') + ('?' + parsed.query if parsed.query else ''), addresses
