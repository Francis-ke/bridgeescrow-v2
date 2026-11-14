from app.api.admin_routes import bp
from app.core.decorators import role_required
from app.core.jwt import current_user_id
from app.services.protected.common import load
from app.services.protected.serialization import serialize


@bp.get('/protected/<int:eid>')
@role_required('admin')
def inspect_protected(eid):
    uid = current_user_id()
    return {'payment': serialize(load(eid, uid, admin=True, readonly=True), uid)}
