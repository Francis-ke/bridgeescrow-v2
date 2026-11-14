from datetime import timedelta
import time
import click
from sqlalchemy import or_, update
from app.core.db import db
from app.models.phone_channel import SmsMessage
from app.models.mixins import utcnow
from . import sms_transport


def deliver(limit=20):
    rows = SmsMessage.query.filter(SmsMessage.mode == 'africastalking',
        SmsMessage.status.in_(['queued', 'retry']),
        or_(SmsMessage.next_attempt_at.is_(None), SmsMessage.next_attempt_at <= utcnow())).limit(limit).all()
    sent = 0
    for row in rows:
        claimed = db.session.execute(update(SmsMessage).where(SmsMessage.id == row.id,
            SmsMessage.status == row.status).values(status='sending', attempts=SmsMessage.attempts + 1))
        db.session.commit()
        if claimed.rowcount != 1:
            continue
        try:
            row.provider_id = sms_transport.send(row.phone, row.body, row.environment)
            row.status, row.error = 'accepted', None
            sent += 1
        except Exception as error:
            row.status = 'failed' if row.attempts >= 5 else 'retry'
            row.error = type(error).__name__
            row.next_attempt_at = utcnow() + timedelta(seconds=30 * 2 ** row.attempts)
        db.session.commit()
    return sent


def register_cli(app):
    @app.cli.command('deliver-sms')
    @click.option('--watch', is_flag=True)
    @click.option('--limit', type=click.IntRange(1, 100), default=20)
    def run(watch, limit):
        """Deliver queued provider SMS. Accepted does not mean handset delivery."""
        while True:
            click.echo(f'Accepted: {deliver(limit)}')
            if not watch:
                return
            time.sleep(5)
