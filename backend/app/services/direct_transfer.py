from sqlalchemy import update
from app.core.db import db
from app.models import Wallet
from app.services.notifications import add
from app.services.wallet_service import wallet_for


def receive(sender, recipient, cents, receipt):
    """Credit the recipient within the sender's existing database transaction."""
    wallet = wallet_for(recipient.id)
    db.session.execute(update(Wallet).where(Wallet.id == wallet.id).values(
        available_cents=Wallet.available_cents + cents))
    from app.models import LedgerEntry
    db.session.add(LedgerEntry(wallet_id=wallet.id, entry_type='transfer',
        direction='credit', amount_cents=cents, reference='IN-' + receipt.reference,
        description=f'Received from {sender.full_name}: {receipt.reference}',
        idempotency_key=f'received-{receipt.id}'))
    add(recipient.id, None, f'transfer-{receipt.id}',
        f'{sender.full_name} sent KES {cents // 100}.{cents % 100:02d} to your wallet.')
