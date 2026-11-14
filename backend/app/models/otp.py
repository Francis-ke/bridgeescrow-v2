from app.core.db import db
from app.models.mixins import TimestampMixin


class OtpChallenge(TimestampMixin, db.Model):
    __tablename__ = "otp_challenges"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    purpose = db.Column(db.String(24), nullable=False, index=True)
    challenge_token = db.Column(db.String(64), unique=True, nullable=False)
    code_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    consumed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship("User", back_populates="otp_challenges")
