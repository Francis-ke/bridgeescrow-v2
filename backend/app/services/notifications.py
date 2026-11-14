from app.core.db import db
from app.models.notification import Notification


def add(user_id, escrow, event_key, message):
    if not Notification.query.filter_by(event_key=event_key).first():
        db.session.add(Notification(user_id=user_id, escrow_id=escrow.id if escrow else None,
                                    event_key=event_key, message=message))
        from app.models import User
        from app.services.sms import queue
        user = db.session.get(User, user_id)
        if user and user.phone_verified:
            queue(user, 'BridgeEscrow: ' + message, 'notification-' + event_key)
