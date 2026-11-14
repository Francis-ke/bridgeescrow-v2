"""Add category-specific protected payments and balanced ledger buckets."""
import sqlalchemy as sa
from alembic import op
revision = '18'
down_revision = '17'
branch_labels = None
depends_on = None


def times():
    return [sa.Column(name, sa.DateTime(), nullable=False) for name in ['created_at', 'updated_at']]


def upgrade():
    op.add_column('ledger_entries', sa.Column('account_bucket', sa.String(16), nullable=False, server_default='available'))
    op.add_column('ledger_entries', sa.Column('batch_reference', sa.String(40), nullable=True))
    op.create_index('ix_ledger_entries_batch_reference', 'ledger_entries', ['batch_reference'])
    columns = [sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('escrow_id', sa.Integer(), sa.ForeignKey('escrows.id'), nullable=False, unique=True)]
    for name, length in [('category', 24), ('state', 32), ('pre_dispute_state', 32)]:
        columns.append(sa.Column(name, sa.String(length), nullable=name == 'pre_dispute_state'))
    columns += [sa.Column('description', sa.Text(), nullable=False), sa.Column('rules', sa.JSON(), nullable=False)]
    for name in ['client_accepted', 'provider_accepted']:
        columns.append(sa.Column(name, sa.Boolean(), nullable=False))
    for name in ['deadline_at', 'booking_start', 'booking_end', 'reservation_confirmed_at',
                 'provider_confirmed_at', 'client_confirmed_at']:
        columns.append(sa.Column(name, sa.DateTime(), nullable=name != 'deadline_at'))
    for name in ['released_cents', 'refunded_cents', 'earned_fee_cents']:
        columns.append(sa.Column(name, sa.BigInteger(), nullable=False))
    columns += [sa.Column(name, sa.JSON(), nullable=True) for name in ['extension', 'cancellation']]
    op.create_table('protected_payments', *columns, *times())
    op.create_index('ix_protected_payments_category', 'protected_payments', ['category'])
    columns = [sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('payment_id', sa.Integer(), sa.ForeignKey('protected_payments.id'), nullable=False),
        sa.Column('title', sa.String(140), nullable=False), sa.Column('amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('state', sa.String(24), nullable=False), sa.Column('revision_count', sa.Integer(), nullable=False)]
    for name in ['deadline_at', 'submitted_at', 'approved_at', 'revision_due_at']:
        columns.append(sa.Column(name, sa.DateTime(), nullable=name != 'deadline_at'))
    columns += [sa.Column(name, sa.Text(), nullable=True) for name in ['submission', 'revision_reason']]
    op.create_table('work_milestones', *columns, *times())
    op.create_index('ix_work_milestones_payment_id', 'work_milestones', ['payment_id'])
    op.create_table('protected_events', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('payment_id', sa.Integer(), sa.ForeignKey('protected_payments.id'), nullable=False),
        sa.Column('actor_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(40), nullable=False), sa.Column('detail', sa.Text(), nullable=False), *times())
    op.create_index('ix_protected_events_payment_id', 'protected_events', ['payment_id'])


def downgrade():
    for name in ['protected_events', 'work_milestones', 'protected_payments']:
        op.drop_table(name)
    op.drop_index('ix_ledger_entries_batch_reference', table_name='ledger_entries')
    op.drop_column('ledger_entries', 'batch_reference')
    op.drop_column('ledger_entries', 'account_bucket')
