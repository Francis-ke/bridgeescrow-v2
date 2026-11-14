"""Verified phones, SMS outbox, authenticated USSD and provider payment metadata."""
import sqlalchemy as sa
from alembic import op
revision = '21'
down_revision = '20'
branch_labels = None
depends_on = None


def timestamps():
    return [sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False)]


def upgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column('pin_locked_until', sa.DateTime(), nullable=True))
    with op.batch_alter_table('escrows') as batch:
        batch.add_column(sa.Column('release_expires_at', sa.DateTime(), nullable=True))
        batch.add_column(sa.Column('release_attempts', sa.Integer(), nullable=False, server_default='0'))
    with op.batch_alter_table('payments') as batch:
        batch.add_column(sa.Column('provider', sa.String(24), nullable=False, server_default='simulated'))
        batch.add_column(sa.Column('client_key', sa.String(100), nullable=True))
        batch.create_unique_constraint('uq_payment_wallet_key', ['wallet_id', 'client_key'])
    op.create_table('phone_challenges', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('phone', sa.String(20), nullable=False), sa.Column('token', sa.String(64), nullable=False, unique=True),
        sa.Column('code_hash', sa.String(64), nullable=False), sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False), sa.Column('consumed_at', sa.DateTime()), *timestamps())
    op.create_table('sms_messages', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('phone', sa.String(20), nullable=False), sa.Column('body', sa.Text(), nullable=False),
        sa.Column('event_key', sa.String(160), nullable=False, unique=True), sa.Column('mode', sa.String(16), nullable=False),
        sa.Column('status', sa.String(16), nullable=False), sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.String(100)), sa.Column('error', sa.String(160)),
        sa.Column('next_attempt_at', sa.DateTime()), *timestamps())
    op.create_table('ussd_sessions', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(100), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False), sa.Column('authenticated', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False), sa.Column('request_hash', sa.String(64)),
        sa.Column('reply', sa.Text()), sa.Column('closed', sa.Boolean(), nullable=False), *timestamps())
    op.create_table('channel_requests', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('scope', sa.String(24), nullable=False), *timestamps())
    op.create_index('ix_channel_request_rate', 'channel_requests', ['user_id', 'scope', 'created_at'])


def downgrade():
    for name in ['channel_requests', 'ussd_sessions', 'sms_messages', 'phone_challenges']:
        op.drop_table(name)
    with op.batch_alter_table('payments') as batch:
        batch.drop_constraint('uq_payment_wallet_key', type_='unique')
        batch.drop_column('client_key')
        batch.drop_column('provider')
    with op.batch_alter_table('escrows') as batch:
        batch.drop_column('release_attempts')
        batch.drop_column('release_expires_at')
    with op.batch_alter_table('users') as batch:
        batch.drop_column('phone_verified')
        batch.drop_column('pin_locked_until')
