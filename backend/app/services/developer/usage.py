import uuid
from flask import g, request
from app.core.db import db
from app.models.developer_usage import ApiUsageLog
from app.models.mixins import utcnow


def register_usage_hooks(app):
    if app.extensions.get('developer_usage_hooks'):
        return
    app.extensions['developer_usage_hooks'] = True

    @app.before_request
    def start_developer_audit():
        g.developer_request_id = None
        g.developer_app_id = None
        g.developer_credential_id = None
        if request.path == '/api/v1' or request.path.startswith('/api/v1/'):
            g.developer_request_id = str(uuid.uuid4())
            g.developer_app_id = None
            g.developer_credential_id = None

    @app.after_request
    def finish_developer_audit(response):
        request_id = getattr(g, 'developer_request_id', None)
        if not (request.path == '/api/v1' or request.path.startswith('/api/v1/')) or not request_id:
            return response
        # Never let audit logging commit an unsuccessful or unfinished financial operation.
        db.session.rollback()
        now = utcnow()
        values = {'app_id': getattr(g, 'developer_app_id', None),
            'credential_id': getattr(g, 'developer_credential_id', None),
            'request_id': request_id, 'path': request.path[:500], 'method': request.method[:10],
            'status': response.status_code, 'idempotency_key': request.headers.get('Idempotency-Key', '')[:128] or None,
            'created_at': now, 'updated_at': now}
        with db.engine.begin() as connection:
            connection.execute(ApiUsageLog.__table__.insert().values(**values))
        response.headers['X-Request-ID'] = request_id
        if response.status_code == 429:
            response.headers['Retry-After'] = str(60 - now.second)
        return response
