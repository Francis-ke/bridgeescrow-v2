import hashlib
from flask import g
from datetime import timedelta
from sqlalchemy import select, text as sql_text
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.models.phone_channel import UssdSession
from app.models.mixins import utcnow
from .phone_numbers import find, require_verified
from .transaction_pin import verify
from .ussd_flow import run_session, MENU


def run(phone, text, session_id):
    if not session_id or len(session_id) > 100 or len(text) > 500:
        raise ApiError('Invalid USSD session', 422, 'invalid_session')
    g.ussd_session_id = session_id
    user = find(phone)
    if not user or not user.phone_verified:
        return 'END No account with a verified number. Link your phone on the website.'
    phone = require_verified(user)
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(sql_text('BEGIN IMMEDIATE'))
    row = db.session.execute(select(UssdSession).where(UssdSession.session_id == session_id)
        .with_for_update()).scalar_one_or_none()
    if row and (row.user_id != user.id or row.phone != phone):
        raise ApiError('Session phone mismatch', 403, 'session_mismatch')
    digest = hashlib.sha256(text.encode()).hexdigest()
    if row and row.expires_at < utcnow():
        return 'END Session expired. Dial again.'
    if row and row.request_hash == digest:
        return row.reply
    if row and row.closed:
        return 'END This session has ended. Dial again.'
    if not row:
        row = UssdSession(session_id=session_id, user_id=user.id, phone=phone,
                          expires_at=utcnow() + timedelta(seconds=180))
        db.session.add(row)
    if not text:
        reply = 'CON Enter your BridgeEscrow transaction PIN'
    else:
        pin, _, selection = text.partition('*')
        verify(user, pin)
        row.authenticated = True
        reply = run_session(phone, selection) if selection else 'CON ' + MENU
    row.request_hash, row.reply, row.closed = digest, reply, reply.startswith('END')
    db.session.commit()
    return reply
