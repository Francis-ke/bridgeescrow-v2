from flask import Blueprint, request
from app.core.db import db
from app.models.developer_application import DeveloperApplication, ApiCredential
from app.services.developer.applications import actor, owned_app, describe, create, edit
from app.services.developer import credentials

bp = Blueprint('developer_apps', __name__, url_prefix='/api/v1/developer')


@bp.get('/apps')
def list_apps():
    rows = DeveloperApplication.query.filter_by(user_id=actor()).order_by(DeveloperApplication.id.desc()).all()
    return {'applications': [describe(row) for row in rows]}


@bp.post('/apps')
def create_app():
    return {'application': describe(create(request.get_json(silent=True) or {}))}, 201


@bp.get('/apps/<identifier>')
def get_app(identifier):
    return {'application': describe(owned_app(identifier))}


@bp.patch('/apps/<identifier>')
def patch_app(identifier):
    return {'application': describe(edit(identifier, request.get_json(silent=True) or {}))}


@bp.get('/apps/<identifier>/keys')
def list_keys(identifier):
    app = owned_app(identifier)
    rows = ApiCredential.query.filter_by(app_id=app.id).order_by(ApiCredential.id.desc()).all()
    return {'credentials': [credentials.describe(row) for row in rows]}


@bp.post('/apps/<identifier>/keys')
def create_key(identifier):
    return credentials.create(identifier, request.get_json(silent=True) or {}), 201


@bp.delete('/keys/<int:kid>')
def delete_key(kid):
    return credentials.revoke(kid)


@bp.post('/keys/<int:kid>/rotate')
def rotate_key(kid):
    return credentials.rotate(kid), 201
