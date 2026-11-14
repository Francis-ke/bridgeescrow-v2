import sqlalchemy as sa
from alembic import op


def timestamps():
    return [sa.Column(name, sa.DateTime(), nullable=False) for name in ['created_at', 'updated_at']]


def create_webhook_tables():
    op.create_table('webhook_endpoints', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('app_id', sa.Integer(), sa.ForeignKey('developer_applications.id'), nullable=False),
        sa.Column('url', sa.String(500), nullable=False), sa.Column('secret_ciphertext', sa.Text(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('events', sa.JSON(), nullable=False), *timestamps())
    op.create_index('ix_webhook_endpoints_app_id', 'webhook_endpoints', ['app_id'])
    op.create_table('webhook_deliveries', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('endpoint_id', sa.Integer(), sa.ForeignKey('webhook_endpoints.id'), nullable=False),
        sa.Column('event_id', sa.String(64), nullable=False), sa.Column('event_type', sa.String(40), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('http_status', sa.Integer(), nullable=True), sa.Column('error', sa.String(500), nullable=True),
        sa.UniqueConstraint('endpoint_id', 'event_id'), *timestamps())
    op.create_index('ix_webhook_deliveries_endpoint_id', 'webhook_deliveries', ['endpoint_id'])
