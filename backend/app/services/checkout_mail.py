import ssl
import smtplib
from email.message import EmailMessage
from flask import current_app
from app.core.errors import ApiError


def send(email, subject, body):
    config = current_app.config
    if not config.get('MAIL_PASSWORD'):
        raise ApiError('Email delivery is not configured', 503, 'email_unavailable')
    message = EmailMessage()
    message['From'], message['To'], message['Subject'] = config['MAIL_FROM'], email, subject
    message.set_content(body)
    try:
        with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT'], timeout=10) as smtp:
            if config['MAIL_USE_TLS']:
                smtp.starttls(context=ssl.create_default_context())
            smtp.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        raise ApiError('Unable to send email. Please try again.', 503, 'email_unavailable') from None
