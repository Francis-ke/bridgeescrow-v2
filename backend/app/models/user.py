from app.core.db import db
from app.core.security import hash_password, verify_password
from app.models.mixins import TimestampMixin, utcnow
from app.services.card_numbers import new_card_number, new_card_cvv

ROLES = ("customer", "merchant", "admin")


class User(TimestampMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), unique=True, nullable=False, index=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False,
                            index=True, default=new_card_number)
    card_cvv = db.Column(db.String(3), nullable=False, default=new_card_cvv)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    national_id = db.Column(db.String(32), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    phone_verification_source = db.Column(db.String(24), nullable=True)
    phone_verified = db.Column(db.Boolean, default=False, nullable=False)
    pin_locked_until = db.Column(db.DateTime, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    pin_salt = db.Column(db.String(64), nullable=True)
    pin_hash = db.Column(db.String(128), nullable=True)
    pin_attempts = db.Column(db.Integer, default=0, nullable=False)
    role = db.Column(db.String(16), default="customer", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    wallet = db.relationship("Wallet", back_populates="user", uselist=False)
    otp_challenges = db.relationship("OtpChallenge", back_populates="user")

    def set_password(self, raw: str) -> None:
        self.password_hash = hash_password(raw)

    def check_password(self, raw: str) -> bool:
        return verify_password(raw, self.password_hash)

    def touch_login(self) -> None:
        self.last_login_at = utcnow()

    def to_dict(self, include_card_security=False) -> dict:
        result = {"id": self.id, "account_number": self.account_number,
                "card_number": self.card_number,
                "full_name": self.full_name, "email": self.email,
                "national_id": self.national_id, "phone": self.phone, "phone_verified": self.phone_verified, "phone_verification_source": self.phone_verification_source,
                "role": self.role, "is_active": self.is_active,
                "email_verified": self.email_verified}
        if include_card_security:
            result["card_cvv"] = self.card_cvv
        return result
