from app.services.protected.common import legacy_guard
import hashlib, hmac, secrets
from datetime import timedelta
from app.models.mixins import utcnow
from app.core.db import db
from app.core.errors import ApiError
from app.models.escrow import Escrow
from app.services.escrow_funding import load
from app.services.settle import pay_seller, refund_buyer
from app.services.receipt_hold import ensure_releasable


def open_release(escrow_id: int, buyer_id: int, commit=True) -> str:
    """Buyer triggers release; returns a one-time 6-digit code to SMS.
    Only the hash is stored, never the plain code."""
    esc = load(escrow_id)
    legacy_guard(esc)
    if esc.buyer_id != buyer_id or esc.status != "funded":
        raise ApiError("Escrow is not ready for release", 409, "invalid_state")
    ensure_releasable(esc)
    code = str(secrets.randbelow(900000) + 100000)
    esc.release_code_hash = hashlib.sha256(code.encode()).hexdigest()
    esc.release_expires_at = utcnow() + timedelta(minutes=10)
    esc.release_attempts = 0
    from .sms import queue
    from app.models import User
    user = db.session.get(User, buyer_id)
    from flask import current_app
    if current_app.config['PAYMENT_MODE'] != 'simulated':
        from .phone_numbers import require_verified
        require_verified(user)
    if user.phone_verified:
        queue(user, f'BridgeEscrow release code {code} for {esc.reference}. Enter only after receiving your order. Expires in 10 minutes.',
              f'release-{esc.id}-{secrets.token_hex(8)}')
    db.session.commit() if commit else db.session.flush()
    return code


def confirm_release(escrow_id: int, buyer_id: int, code: str, commit=True) -> Escrow:
    esc = load(escrow_id)
    legacy_guard(esc)
    if current_user_not_buyer(esc, buyer_id) or esc.status != "funded":
        raise ApiError("Escrow is not payable", 409, "invalid_state")
    ensure_releasable(esc)
    given = hashlib.sha256(code.strip().encode()).hexdigest()
    if not esc.release_expires_at or esc.release_expires_at < utcnow() or esc.release_attempts >= 5:
        raise ApiError('Release code expired or locked; request a new one', 403, 'bad_release_code')
    if not esc.release_code_hash or not hmac.compare_digest(given, esc.release_code_hash):
        esc.release_attempts += 1
        db.session.commit()
        raise ApiError("Wrong release code", 403, "bad_release_code")
    pay_seller(esc)
    db.session.commit() if commit else db.session.flush()
    return esc


def current_user_not_buyer(esc: Escrow, buyer_id: int) -> bool:
    return esc.buyer_id != buyer_id


def refund(escrow_id: int, actor_id: int, is_admin: bool) -> Escrow:
    esc = load(escrow_id)
    legacy_guard(esc)
    allowed = is_admin or actor_id in (esc.buyer_id, esc.seller_id)
    if not allowed or esc.status not in ("funded", "disputed"):
        raise ApiError("Refund not allowed in this state", 409, "invalid_state")
    refund_buyer(esc)
    db.session.commit()
    return esc
