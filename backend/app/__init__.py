from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from app.core.db import db
from app.core.errors import register_errors
from app.api import register_blueprints
from app.core.jwt_cache import reset_identity

migrate = Migrate(directory="migrations")


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    if app.config.get("SQLALCHEMY_ENGINE_OPTIONS") is None:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    app.before_request(reset_identity)
    from app.services.developer.usage import register_usage_hooks
    register_usage_hooks(app)
    from app.services.developer.webhook_worker import register_cli
    register_cli(app)
    from app.services.sms_worker import register_cli as register_sms_cli
    register_sms_cli(app)
    from app.services.live_ledger import register_guard
    register_guard(app)
    from app.channel_cli import register_cli as register_channel_cli
    register_channel_cli(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    register_errors(app)
    register_blueprints(app)

    @app.after_request
    def private_responses(response):
        from flask import request
        if request.headers.get('Authorization'):
            response.headers['Cache-Control'] = 'private, no-store'
            response.vary.add('Authorization')
        return response

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "bridgeescrow-v2"}

    return app
