from datetime import timedelta
from app.core.db import db
from app.core.errors import ApiError
from app.models.phone_channel import ChannelRequest
from app.models.mixins import utcnow


def consume(uid, scope, limit=5, seconds=600):
    cutoff = utcnow() - timedelta(seconds=seconds)
    query = ChannelRequest.query.filter_by(user_id=uid, scope=scope).filter(ChannelRequest.created_at >= cutoff)
    if query.count() >= limit:
        raise ApiError('Too many requests. Try again later.', 429, 'channel_rate_limit')
    db.session.add(ChannelRequest(user_id=uid, scope=scope))
    db.session.commit()
