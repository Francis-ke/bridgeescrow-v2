from app.core.db import db
from app.models.mixins import TimestampMixin

OPEN, RESOLVED = "open", "resolved"


class Dispute(TimestampMixin, db.Model):
    __tablename__ = "disputes"
    id = db.Column(db.Integer, primary_key=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrows.id"), nullable=False,
                          index=True)
    raised_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(400), nullable=False)
    status = db.Column(db.String(16), default=OPEN, nullable=False, index=True)
    resolution = db.Column(db.String(400), nullable=True)

    def to_dict(self) -> dict:
        from app.models import Escrow
        escrow = db.session.get(Escrow, self.escrow_id)
        category = escrow.protection.category if escrow and escrow.protection else 'other'
        return {"category": category, "protected": bool(escrow and escrow.protection), "id": self.id, "escrow_id": self.escrow_id,
                "reason": self.reason, "status": self.status,
                "resolution": self.resolution,
                "created_at": self.created_at.isoformat()}
