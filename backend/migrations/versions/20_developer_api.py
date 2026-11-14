"""Add sandbox developer applications, credentials, usage, and webhooks."""
import sqlalchemy as sa
from alembic import op
from migrations.helpers.developer_webhooks import create_webhook_tables, timestamps
revision = '20'
down_revision = '19'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('developer_applications', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('public_id', sa.String(64), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False), sa.Column('description', sa.String(2000), nullable=False),
        sa.Column('website', sa.String(500), nullable=False), sa.Column('type', sa.String(16), nullable=False),
        sa.Column('environment', sa.String(16), nullable=False), sa.Column('active', sa.Boolean(), nullable=False), *timestamps())
    op.create_index('ix_developer_applications_user_id', 'developer_applications', ['user_id'])
    op.create_table('api_credentials', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('app_id', sa.Integer(), sa.ForeignKey('developer_applications.id'), nullable=False),
        sa.Column('name', sa.String(80), nullable=False), sa.Column('public_key', sa.String(100), nullable=False, unique=True),
        sa.Column('secret_hash', sa.String(64), nullable=False, unique=True), sa.Column('prefix', sa.String(32), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False), sa.Column('revoked_at', sa.DateTime(), nullable=True), *timestamps())
    op.create_index('ix_api_credentials_app_id', 'api_credentials', ['app_id'])
    op.create_table('api_rate_windows',
        sa.Column('credential_id', sa.Integer(), sa.ForeignKey('api_credentials.id'), primary_key=True),
        sa.Column('window_start', sa.DateTime(), primary_key=True), sa.Column('count', sa.Integer(), nullable=False))
    op.create_table('api_usage_logs', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('app_id', sa.Integer(), sa.ForeignKey('developer_applications.id'), nullable=True),
        sa.Column('credential_id', sa.Integer(), sa.ForeignKey('api_credentials.id'), nullable=True),
        sa.Column('request_id', sa.String(64), unique=True, nullable=False),
        sa.Column('path', sa.String(500), nullable=False), sa.Column('method', sa.String(10), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False), sa.Column('idempotency_key', sa.String(128), nullable=True), *timestamps())
    op.create_index('ix_api_usage_logs_app_id', 'api_usage_logs', ['app_id'])
    op.create_index('ix_api_usage_logs_credential_id', 'api_usage_logs', ['credential_id'])
    create_webhook_tables()
    with op.batch_alter_table('checkout_orders') as batch:
        batch.add_column(sa.Column('developer_application_id', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('client_reference', sa.String(100), nullable=True))
        batch.add_column(sa.Column('idempotency_key', sa.String(128), nullable=True))
        batch.create_index('ix_checkout_orders_developer_application_id', ['developer_application_id'])
        batch.create_unique_constraint('uq_checkout_app_idempotency', ['developer_application_id', 'idempotency_key'])
        batch.create_foreign_key('fk_checkout_order_developer_app',
                                 'developer_applications', ['developer_application_id'], ['id'])


def downgrade():
    with op.batch_alter_table('checkout_orders') as batch:
        batch.drop_constraint('uq_checkout_app_idempotency', type_='unique')
        batch.drop_index('ix_checkout_orders_developer_application_id')
        batch.drop_constraint('fk_checkout_order_developer_app', type_='foreignkey')
        batch.drop_column('idempotency_key')
        batch.drop_column('client_reference')
        batch.drop_column('developer_application_id')
    for table in ['webhook_deliveries', 'webhook_endpoints', 'api_usage_logs', 'api_rate_windows',
                  'api_credentials', 'developer_applications']:
        op.drop_table(table)
