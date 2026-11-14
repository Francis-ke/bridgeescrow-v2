import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def database_uri() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    user = os.getenv("DB_USER", "bridge")
    pwd = os.getenv("DB_PASSWORD", "bridge")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "bridgeescrow_v2")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"


from channel_config import ChannelConfig


class Config(ChannelConfig):
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me-32-bytes-long!!")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-at-least-32-bytes-long!")
    JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))
    SQLALCHEMY_DATABASE_URI = database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5180,http://127.0.0.1:5180").split(",")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    if MAIL_SERVER == "smtp.gmail.com" and MAIL_PASSWORD:
        MAIL_PASSWORD = MAIL_PASSWORD.replace(" ", "")
    MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "600"))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    DEFAULT_CURRENCY = "KES"
    PUBLIC_FRONTEND_URL = os.getenv("PUBLIC_FRONTEND_URL", "http://127.0.0.1:5180")
    PIN_MAX_ATTEMPTS = int(os.getenv("PIN_MAX_ATTEMPTS", "5"))
    USSD_MAX_LEN = int(os.getenv("USSD_MAX_LEN", "182"))
