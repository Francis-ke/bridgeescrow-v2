from app.api.integration_routes import bp as integration_bp
from app.api.developer_apps import bp as developer_apps_bp
from app.api.developer_webhook_routes import bp as developer_webhooks_bp
from app.api.developer_escrows import bp as developer_escrows_bp
from app.api.developer_checkout import bp as developer_checkout_bp
from app.api.developer_delivery import bp as developer_delivery_bp
from app.api.checkout_routes import bp as checkout_bp
from app.api import developer_buyer
from app.api.protected_routes import bp as protected_bp
from app.api.notification_routes import bp as notifications_bp
from app.api.auth_routes import bp as auth_bp
from app.api import auth_login, auth_pin  # noqa: F401 registers routes
from app.api import auth_otp  # noqa: F401 registers OTP routes
from app.api.wallet_routes import bp as wallet_bp
from app.api import wallet_money  # noqa: F401
from app.api.escrow_routes import bp as escrow_bp
from app.api import escrow_actions  # noqa: F401
from app.api import contract_routes, dispute_routes  # noqa: F401
from app.api.dashboard_routes import bp as dashboard_bp
from app.api.payment_routes import bp as payment_bp
from app.api.callback_routes import bp as callback_bp
from app.api.analytics_routes import bp as analytics_bp
from app.api.merchant_routes import bp as merchant_bp
from app.api.admin_routes import bp as admin_bp
from app.api import admin_analytics, admin_disputes, admin_workflows  # noqa: F401
from app.api.payout_routes import bp as payouts_bp
from app.api.sms_routes import bp as sms_bp
from app.api.phone_routes import bp as phone_bp
from app.api.ussd_routes import bp as ussd_bp


def register_blueprints(app):
    for bp in (developer_apps_bp, developer_webhooks_bp, developer_escrows_bp, developer_checkout_bp, developer_delivery_bp,
               integration_bp, checkout_bp, protected_bp, notifications_bp, auth_bp, wallet_bp, escrow_bp, dashboard_bp, merchant_bp,
               admin_bp, ussd_bp, phone_bp, sms_bp, payouts_bp, payment_bp, callback_bp, analytics_bp):
        app.register_blueprint(bp)
