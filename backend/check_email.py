"""Check sender configuration and SMTP authentication without sending email."""
import smtplib
import ssl
import sys

from config import Config


def main():
    password = Config.MAIL_PASSWORD or ""
    if not all([Config.MAIL_SERVER, Config.MAIL_USERNAME, Config.MAIL_FROM, password]):
        print("Set MAIL_SERVER, MAIL_USERNAME, MAIL_FROM and MAIL_PASSWORD in backend/.env.")
        return 1
    if Config.MAIL_SERVER == "smtp.gmail.com":
        password = password.replace(" ", "")
        if len(password) != 16:
            print("Change MAIL_PASSWORD in backend/.env to the sender's 16-character Google app password.")
            print("Your current value does not match that format. No connection or email was attempted.")
            return 1
    try:
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT, timeout=10) as smtp:
            if Config.MAIL_USE_TLS:
                smtp.starttls(context=ssl.create_default_context())
            smtp.login(Config.MAIL_USERNAME, password)
    except smtplib.SMTPAuthenticationError:
        print("Gmail rejected authentication. Check the sender account and its app password.")
        return 1
    except (OSError, smtplib.SMTPException) as error:
        print(f"SMTP connection failed ({type(error).__name__}). Check network access and SMTP settings.")
        return 1
    print("SMTP authentication passed. No email sent; inbox delivery has not been tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
