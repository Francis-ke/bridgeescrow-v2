import os


class ChannelConfig:
    DEVELOPER_LIVE_ENABLED = os.getenv('DEVELOPER_LIVE_ENABLED', '0') == '1'
    PAYMENT_MODE = os.getenv('PAYMENT_MODE', 'simulated')
    SMS_MODE = os.getenv('SMS_MODE', 'simulated')
    AT_USERNAME = os.getenv('AT_USERNAME', '')
    AT_API_KEY = os.getenv('AT_API_KEY', '')
    AT_SENDER_ID = os.getenv('AT_SENDER_ID', '')
    AT_ENVIRONMENT = os.getenv('AT_ENVIRONMENT', 'sandbox')
    USSD_ENVIRONMENT = os.getenv('USSD_ENVIRONMENT', 'sandbox')
    USSD_CALLBACK_TOKEN = os.getenv('USSD_CALLBACK_TOKEN', '')
    USSD_SERVICE_CODE = os.getenv('USSD_SERVICE_CODE', '')
    USSD_TTL_SECONDS = 180
    MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
    MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
    MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '')
    MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')
    MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', '')
    MPESA_CALLBACK_TOKEN = os.getenv('MPESA_CALLBACK_TOKEN', '')
    MPESA_B2C_ENABLED = os.getenv('MPESA_B2C_ENABLED', '0') == '1'
    MPESA_B2C_INITIATOR = os.getenv('MPESA_B2C_INITIATOR', '')
    MPESA_B2C_SECURITY_CREDENTIAL = os.getenv('MPESA_B2C_SECURITY_CREDENTIAL', '')
    MPESA_B2C_RESULT_URL = os.getenv('MPESA_B2C_RESULT_URL', '')
    MPESA_B2C_TIMEOUT_URL = os.getenv('MPESA_B2C_TIMEOUT_URL', '')
