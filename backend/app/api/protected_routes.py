from flask import Blueprint, request
from app.core.decorators import login_required
from app.core.jwt import current_user_id
from app.models import User
from app.services.protected.common import load, require
from app.services.protected.create import create
from app.services.protected.dispatch import perform
from app.services.protected.serialization import serialize
from app.services.protected.rules import CATEGORIES, defaults

bp = Blueprint('protected', __name__, url_prefix='/api/protected')


def actor():
    from app.core.db import db
    user = db.session.get(User, current_user_id())
    require(user and user.is_active and user.email_verified, 'An active verified account is required', 403)
    return user.id


@bp.get('/categories')
@login_required
def categories():
    return {'categories': [{'id': key, 'label': label, 'defaults': defaults(key)}
                           for key, label in CATEGORIES.items()]}


@bp.get('/providers')
@login_required
def providers():
    uid = actor()
    return {'providers': [{'id': user.id, 'name': user.full_name, 'email': user.email}
        for user in User.query.filter(User.id != uid, User.is_active.is_(True),
                                     User.email_verified.is_(True)).order_by(User.full_name).limit(500)]}


@bp.post('')
@login_required
def new_payment():
    uid = actor()
    payment = create(uid, request.get_json(silent=True) or {})
    return {'payment': serialize(payment, uid)}, 201


@bp.get('/<int:eid>')
@login_required
def detail(eid):
    uid = actor()
    return {'payment': serialize(load(eid, uid, readonly=True), uid)}


@bp.post('/<int:eid>/<action>')
@login_required
def action(eid, action):
    uid = actor()
    payment = perform(eid, uid, action, request.get_json(silent=True) or {})
    return {'payment': serialize(payment, uid)}


@bp.post('/delivery')
@login_required
def simple_delivery():
    from app.services.protected.delivery import create_delivery
    uid = actor()
    payment = create_delivery(uid, request.get_json(silent=True) or {})
    return {'payment': serialize(payment, uid)}, 201
