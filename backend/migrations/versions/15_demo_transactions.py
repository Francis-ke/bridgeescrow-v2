"""Persist account-affecting demo checkouts with duplicate protection."""
import sqlalchemy as sa
from alembic import op
revision = '15'
down_revision = '14'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('demo_transactions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('escrow_id', sa.Integer(), sa.ForeignKey('escrows.id'), nullable=True),
        sa.Column('idempotency_key', sa.String(64), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('reference', sa.String(32), nullable=False, unique=True),
        sa.Column('kind', sa.String(16), nullable=False), sa.Column('method', sa.String(8), nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('destination', sa.String(190), nullable=False), sa.Column('last4', sa.String(4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', 'idempotency_key'))
    op.create_index('ix_demo_transactions_user_id', 'demo_transactions', ['user_id'])


def downgrade():
    op.drop_table('demo_transactions')
