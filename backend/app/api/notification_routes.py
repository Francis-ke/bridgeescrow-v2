from flask import Blueprint
from app.core.db import db
from app.core.decorators import login_required
from app.core.errors import ApiError
from app.core.jwt import current_user_id
from app.models import Escrow
from app.models.mixins import utcnow
from app.models.notification import Notification
from app.services.notifications import add

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@bp.get("")
@login_required
def list_notifications():
    uid = current_user_id()
    expired = Escrow.query.filter(Escrow.seller_id == uid, Escrow.status == "funded",
                                 Escrow.receipt_hold_until <= utcnow()).all()
    for escrow in expired:
        add(uid, escrow, f"hold-ended-{escrow.id}-{escrow.receipt_hold_until.isoformat()}",
            f"The hold for {escrow.reference} has ended. Buyer confirmation is still required to receive payment.")
    db.session.commit()
    query = Notification.query.filter_by(user_id=uid)
    return {"notifications": [row.to_dict() for row in query.order_by(
        Notification.id.desc()).limit(50).all()],
        "unread_count": query.filter_by(read_at=None).count()}


@bp.put("/<int:notification_id>/read")
@login_required
def mark_read(notification_id):
    row = Notification.query.filter_by(id=notification_id, user_id=current_user_id()).first()
    if not row:
        raise ApiError("Notification not found", 404, "not_found")
    row.read_at = row.read_at or utcnow()
    db.session.commit()
    return {"notification": row.to_dict()}


@bp.put("/read-all")
@login_required
def read_all():
    Notification.query.filter_by(user_id=current_user_id(), read_at=None).update(
        {"read_at": utcnow()}, synchronize_session=False)
    db.session.commit()
    return {"unread_count": 0}
