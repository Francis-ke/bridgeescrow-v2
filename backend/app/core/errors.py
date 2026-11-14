from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400, code: str = "bad_request"):
        super().__init__(message)
        self.message, self.status, self.code = message, status, code


def _body(message, code, status):
    return jsonify({"error": {"code": code, "message": message}}), status


def register_errors(app):
    @app.errorhandler(ApiError)
    def api_error(err):
        return _body(err.message, err.code, err.status)

    @app.errorhandler(ValidationError)
    def validation_error(err):
        field, messages = next(iter(err.messages.items()))
        labels = {"full_name": "Full name", "national_id": "ID number",
                  "email": "Email", "password": "Password",
                  "password_confirm": "Confirm password", "otp": "Email OTP"}
        detail = messages[0] if isinstance(messages, list) else str(messages)
        label = labels.get(field, field.replace("_", " ").capitalize())
        msg = f"{label}: {detail}" if field != "_schema" else detail
        return _body(msg, "validation_error", 422)

    @app.errorhandler(HTTPException)
    def http_error(err):
        return _body(err.description, err.name.lower().replace(" ", "_"), err.code)

    @app.errorhandler(Exception)
    def unhandled(err):
        app.logger.exception("unhandled error")
        return _body("Internal server error", "internal_error", 500)
