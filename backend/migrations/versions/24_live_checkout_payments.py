"""Bind provider confirmations to an immutable merchant checkout."""
import sqlalchemy as sa
from alembic import op
revision = '24'
down_revision = '23'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('payments') as batch:
        batch.add_column(sa.Column('checkout_order_id', sa.Integer(), nullable=True))
        batch.create_foreign_key('fk_payment_checkout_order', 'checkout_orders', ['checkout_order_id'], ['id'])
        batch.create_index('ix_payments_checkout_order_id', ['checkout_order_id'])


def downgrade():
    with op.batch_alter_table('payments') as batch:
        batch.drop_index('ix_payments_checkout_order_id')
        batch.drop_constraint('fk_payment_checkout_order', type_='foreignkey')
        batch.drop_column('checkout_order_id')
