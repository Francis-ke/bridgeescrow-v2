from app.core.db import db
from app.models.mixins import TimestampMixin


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrows.id"), nullable=True)
    event_key = db.Column(db.String(160), unique=True, nullable=False)
    message = db.Column(db.String(400), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        from app.services.escrow_details import iso
        kind, title = "activity", "Account update"
        categories = [
            (("protected-",), "activity", "Protected payment updated"),
            (("demo-deposit-", "deposit-"), "deposit", "Deposit received"),
            (("hold-request-",), "hold", "Hold-time request"),
            (("hold-decision-",), "hold", "Hold request updated"),
            (("hold-ended-",), "hold", "Hold period ended"),
            (("funded-",), "incoming", "Incoming payment"),
            (("received-",), "received", "Payment received"),
            (("refunded-",), "refund", "Payment refunded"),
        ]
        for prefixes, event_kind, event_title in categories:
            if self.event_key.startswith(prefixes):
                kind, title = event_kind, event_title
                break
        return {"kind": kind, "title": title, "id": self.id, "message": self.message, "escrow_id": self.escrow_id,
                "url": f"/escrows/{self.escrow_id}" if self.escrow_id else "/?statements=1",
                "read": self.read_at is not None, "created_at": iso(self.created_at)}
