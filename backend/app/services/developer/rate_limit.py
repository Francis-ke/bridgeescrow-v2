from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.mysql import insert as mysql_insert
from app.core.db import db
from app.core.errors import ApiError
from app.models.developer_usage import ApiRateWindow
from app.models.mixins import utcnow


def consume(credential_id):
    table = ApiRateWindow.__table__
    window = utcnow().replace(second=0, microsecond=0)
    values = {'credential_id': credential_id, 'window_start': window, 'count': 1}
    with db.engine.begin() as connection:
        if connection.dialect.name == 'sqlite':
            statement = sqlite_insert(table).values(**values).on_conflict_do_update(
                index_elements=['credential_id', 'window_start'], set_={'count': table.c.count + 1})
        else:
            statement = mysql_insert(table).values(**values).on_duplicate_key_update(count=table.c.count + 1)
        connection.execute(statement)
        count = connection.execute(select(table.c.count).where(
            table.c.credential_id == credential_id, table.c.window_start == window)).scalar_one()
    if count > 60:
        raise ApiError('API rate limit exceeded; retry after the current minute', 429, 'rate_limited')
