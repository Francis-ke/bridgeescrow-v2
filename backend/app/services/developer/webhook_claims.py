from datetime import timedelta
from sqlalchemy import or_, and_, select, text
from app.core.db import db
from app.models.mixins import utcnow
from app.models.webhook import WebhookDelivery, WebhookEndpoint

MAX_ATTEMPTS = 5


def claim():
    from app.models.developer_application import DeveloperApplication
    if db.engine.dialect.name == 'sqlite':
        raw = db.session.connection().connection.driver_connection
        if not raw.in_transaction:
            db.session.execute(text('BEGIN IMMEDIATE'))
    now = utcnow()
    eligible = or_(and_(WebhookDelivery.status.in_(['pending', 'retry']),
                         WebhookDelivery.next_attempt_at <= now),
                   and_(WebhookDelivery.status == 'processing', WebhookDelivery.next_attempt_at <= now))
    row = db.session.execute(select(WebhookDelivery).where(eligible).order_by(WebhookDelivery.id)
        .with_for_update(skip_locked=True).limit(1).execution_options(populate_existing=True)).scalar_one_or_none()
    if not row:
        db.session.rollback()
        return None
    endpoint = db.session.get(WebhookEndpoint, row.endpoint_id)
    app = db.session.get(DeveloperApplication, endpoint.app_id) if endpoint else None
    if not endpoint or not endpoint.active or not app or not app.active:
        row.status, row.error, row.next_attempt_at = 'cancelled', 'Endpoint or application disabled', None
        db.session.commit()
        return {'skipped': True}
    if row.attempts >= MAX_ATTEMPTS:
        row.status, row.error, row.next_attempt_at = 'failed', 'Delivery attempt limit reached', None
        db.session.commit()
        return {'skipped': True}
    row.attempts += 1
    row.status, row.next_attempt_at = 'processing', now + timedelta(seconds=60)
    result = {'id': row.id, 'attempt': row.attempts, 'url': endpoint.url,
              'secret_ciphertext': endpoint.secret_ciphertext, 'payload': row.payload}
    db.session.commit()
    return result


def finish(delivery, status, error):
    row = db.session.execute(select(WebhookDelivery).where(WebhookDelivery.id == delivery['id'])
        .with_for_update().execution_options(populate_existing=True)).scalar_one()
    if row.status != 'processing' or row.attempts != delivery['attempt']:
        db.session.rollback()
        return
    row.http_status, row.error = status, error
    if error is None:
        row.status, row.next_attempt_at = 'delivered', None
    elif row.attempts >= MAX_ATTEMPTS:
        row.status, row.next_attempt_at = 'failed', None
    else:
        row.status = 'retry'
        delays = [60, 300, 900, 3600]
        row.next_attempt_at = utcnow() + timedelta(seconds=delays[row.attempts - 1])
    db.session.commit()
