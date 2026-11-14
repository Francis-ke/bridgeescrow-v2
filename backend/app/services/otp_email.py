from email.message import EmailMessage
import smtplib
import ssl
from flask import current_app
from app.core.errors import ApiError


def _send_email(user, code, purpose):
    server = current_app.config.get("MAIL_SERVER")
    if not server or not current_app.config.get("MAIL_PASSWORD") or not current_app.config.get("MAIL_FROM"):
        raise ApiError("Email delivery is not configured. Please contact support.",
                       503, "email_unavailable")
    msg = EmailMessage()
    msg["Subject"] = ("Reset your BridgeEscrow password" if purpose == "password_reset"
                      else "Verify your BridgeEscrow email")
    msg["From"] = current_app.config["MAIL_FROM"]
    msg["To"] = user.email
    minutes = current_app.config["OTP_TTL_SECONDS"] // 60
    msg.set_content(f"Your BridgeEscrow code is {code}. It expires in {minutes} minutes. "
                    "If you did not request this code, ignore this email.")
    try:
        with smtplib.SMTP(server, current_app.config["MAIL_PORT"], timeout=10) as smtp:
            if current_app.config["MAIL_USE_TLS"]:
                smtp.starttls(context=ssl.create_default_context())
            if current_app.config.get("MAIL_USERNAME"):
                smtp.login(current_app.config["MAIL_USERNAME"],
                           current_app.config["MAIL_PASSWORD"])
            smtp.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        current_app.logger.warning("OTP email authentication rejected")
        raise ApiError("Email service authentication failed. Please contact support.",
                       503, "email_unavailable") from None
    except (OSError, smtplib.SMTPException) as error:
        current_app.logger.warning("OTP email delivery failed (%s)", type(error).__name__)
        raise ApiError("Email service is unavailable. Please try again later.",
                       503, "email_unavailable") from None

