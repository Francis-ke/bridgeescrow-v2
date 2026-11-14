from app.core.db import db
from app.models.mixins import TimestampMixin


class Contract(TimestampMixin, db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrows.id"), unique=True,
                          nullable=False)
    terms = db.Column(db.Text, nullable=False)
    delivery_days = db.Column(db.Integer, default=7, nullable=False)
    buyer_signed_at = db.Column(db.DateTime, nullable=True)
    seller_signed_at = db.Column(db.DateTime, nullable=True)
    escrow = db.relationship("Escrow")

    @property
    def fully_signed(self) -> bool:
        return bool(self.buyer_signed_at and self.seller_signed_at)

    def to_dict(self) -> dict:
        return {"id": self.id, "escrow_id": self.escrow_id, "terms": self.terms,
                "delivery_days": self.delivery_days,
                "buyer_signed": self.buyer_signed_at is not None,
                "seller_signed": self.seller_signed_at is not None,
                "fully_signed": self.fully_signed}
