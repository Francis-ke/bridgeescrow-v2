from decimal import Decimal
from sqlalchemy import select, text
from app.core.db import db
from app.core.errors import ApiError
from app.models import Wallet
from app.models.payout import Payout
from .ledger import credit
from .notifications import add


def finish(reference, body, timeout=False):
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    payout = db.session.execute(select(Payout).where(Payout.reference == reference)
        .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
    if not payout:
        raise ApiError('Payout not found', 404, 'not_found')
    if payout.status in ('succeeded', 'failed'):
        return payout
    data = body.get('Result', {})
    if timeout:
        payout.status = 'unknown'
        db.session.commit()
        return payout
    if payout.conversation_id and data.get('ConversationID') != payout.conversation_id:
        raise ApiError('Payout callback reference mismatch', 422, 'payout_mismatch')
    code = str(data.get('ResultCode', ''))
    if not code:
        raise ApiError('Missing provider result', 422, 'payout_mismatch')
    if code == '0':
        values = {item.get('Key'): item.get('Value') for item in data.get('ResultParameters', {}).get('ResultParameter', [])}
        if Decimal(str(values.get('TransactionAmount', '-1'))) * 100 != payout.amount_cents:
            raise ApiError('Payout amount mismatch', 422, 'payout_mismatch')
        receipt = data.get('TransactionID')
        if not receipt:
            raise ApiError('Missing payout receipt', 422, 'payout_mismatch')
        payout.status, payout.receipt = 'succeeded', receipt
    else:
        wallet = db.session.execute(select(Wallet).where(Wallet.user_id == payout.user_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one()
        credit(wallet, payout.amount_cents, 'refund', 'Failed M-PESA payout ' + payout.reference,
               key='payout-refund-' + payout.reference)
        payout.status = 'failed'
    add(payout.user_id, None, 'payout-result-' + payout.reference,
        f'M-PESA withdrawal {payout.reference}: {payout.status}. Check your wallet for details.')
    db.session.commit()
    return payout
