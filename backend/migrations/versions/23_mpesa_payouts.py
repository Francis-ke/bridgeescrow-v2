"""Audited M-PESA payout reservations and provider results."""
import sqlalchemy as sa
from alembic import op
revision = '23'
down_revision = '22'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('payouts', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('reference', sa.String(40), nullable=False, unique=True),
        sa.Column('client_key', sa.String(100), nullable=False), sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=False), sa.Column('status', sa.String(24), nullable=False),
        sa.Column('conversation_id', sa.String(100), unique=True), sa.Column('originator_id', sa.String(100)),
        sa.Column('receipt', sa.String(40), unique=True), sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', 'client_key', name='uq_payout_user_key'))


def downgrade():
    op.drop_table('payouts')
