import base64
import hashlib
import hmac
import json
import secrets
import time
from cryptography.fernet import Fernet
from flask import current_app


def cipher():
    material = ('bridgeescrow:webhooks:v1:' + current_app.config['SECRET_KEY']).encode()
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(material).digest()))


def issue():
    secret = 'be_whsec_' + secrets.token_urlsafe(32)
    return secret, cipher().encrypt(secret.encode()).decode()


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def signed_headers(endpoint, payload, timestamp=None):
    timestamp = str(int(time.time()) if timestamp is None else timestamp)
    secret = cipher().decrypt(endpoint.secret_ciphertext.encode())
    signature = hmac.new(secret, timestamp.encode() + b'.' + payload, hashlib.sha256).hexdigest()
    return {'Content-Type': 'application/json', 'User-Agent': 'BridgeEscrow-Webhooks/1',
            'BridgeEscrow-Signature': f't={timestamp},v1={signature}'}
