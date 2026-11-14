import os, sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app          # noqa: E402
from app.core.db import db          # noqa: E402
from app import models              # noqa: F401,E402  (registers tables)

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
app = create_app()
with app.app_context():
    config.set_main_option("sqlalchemy.url",
                           app.config["SQLALCHEMY_DATABASE_URI"].replace("%", "%%"))
target_metadata = db.metadata


def run():
    url = config.get_main_option("sqlalchemy.url")
    if context.is_offline_mode():
        context.configure(url=url, target_metadata=target_metadata,
                          literal_binds=True, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
        return
    connectable = engine_from_config(config.get_section(config.config_ini_section),
                                     prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run()
