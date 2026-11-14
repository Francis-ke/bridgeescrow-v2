from flask import Blueprint, request
from marshmallow import Schema, fields, validate
from app.core.db import db
from app.models import User
from app.services.developer.applications import owned_app
from app.services.developer.authentication import authenticate
from app.services.developer.orders import scoped, describe
from app.services.checkout_redemption import redeem

bp = Blueprint('developer_delivery', __name__, url_prefix='/api/v1')


class CodeSchema(Schema):
    code = fields.String(required=True, validate=validate.Regexp(r'^[0-9]{8}$'))


def confirm(application, oid):
    order = scoped(application, oid, locked=True)
    code = CodeSchema().load(request.get_json(silent=True) or {})
    redeem(order, db.session.get(User, application.user_id), code)
    return {'escrow': describe(order)}


@bp.post('/escrows/<int:oid>/delivery-confirmations')
def delivery(oid):
    application, _ = authenticate('release:request')
    return confirm(application, oid)


@bp.post('/developer/apps/<identifier>/escrows/<int:oid>/delivery-confirmations')
def dashboard_delivery(identifier, oid):
    return confirm(owned_app(identifier), oid)
