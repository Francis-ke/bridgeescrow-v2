from app.core.db import db
from app.models.mixins import TimestampMixin


class Merchant(TimestampMixin, db.Model):
    """A merchant profile linked to a user account with role 'merchant'."""
    __tablename__ = "merchants"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True,
                        nullable=False)
    business_name = db.Column(db.String(140), nullable=False)
    till_number = db.Column(db.String(12), unique=True, nullable=False)
    paybill = db.Column(db.String(12), nullable=True)
    status = db.Column(db.String(16), default="pending", nullable=False)
    user = db.relationship("User")

    def to_dict(self) -> dict:
        return {"id": self.id, "business_name": self.business_name,
                "till_number": self.till_number, "paybill": self.paybill,
                "status": self.status, "owner": self.user.full_name}
