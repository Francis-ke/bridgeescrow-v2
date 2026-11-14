from flask import g
from app.core.db import db
from app.core.errors import ApiError
from app.core.jwt import current_user_id
from app.models import User
from app.models.developer_application import DeveloperApplication
from .schemas import ApplicationSchema


def actor(uid=None):
    user = db.session.get(User, uid if uid is not None else current_user_id())
    if not user or not user.is_active or not user.email_verified:
        raise ApiError('An active verified account is required', 403, 'account_unavailable')
    return user.id


def owned_app(identifier, user_id=None):
    uid = actor(user_id)
    query = DeveloperApplication.query.filter_by(user_id=uid)
    app = query.filter_by(id=int(identifier)).first() if str(identifier).isdigit() else query.filter_by(public_id=identifier).first()
    if not app:
        raise ApiError('Application not found', 404, 'not_found')
    g.developer_app_id = app.id
    return app


def describe(app):
    from app.services.escrow_details import iso
    owner = db.session.get(User, app.user_id)
    return {'owner': {'name': owner.full_name, 'account_number': owner.account_number},
            'id': app.id, 'app_id': app.public_id, 'name': app.name, 'description': app.description,
            'website': app.website, 'type': app.type, 'environment': app.environment,
            'active': app.active, 'created_at': iso(app.created_at)}


def create(payload):
    data = ApplicationSchema().load(payload)
    for key in ['name', 'description']:
        data[key] = data[key].strip()
    if len(data['name']) < 3 or len(data['description']) < 10:
        raise ApiError('Enter a meaningful application name and description', 422, 'validation_error')
    uid = actor()
    from .environments import require_environment
    require_environment(data['environment'], db.session.get(User, uid))
    app = DeveloperApplication(user_id=uid, **data)
    db.session.add(app)
    db.session.commit()
    g.developer_app_id = app.id
    return app


def edit(identifier, payload):
    app = owned_app(identifier)
    data = ApplicationSchema().load(payload, partial=True)
    if 'environment' in data and data['environment'] != app.environment:
        raise ApiError('Application environment cannot change; create a separate application', 422, 'environment_immutable')
    for key, value in data.items():
        if key in ['name', 'description']:
            value = value.strip()
            if len(value) < (3 if key == 'name' else 10):
                raise ApiError('Enter meaningful settings', 422, 'validation_error')
        setattr(app, key, value)
    db.session.commit()
    return app
