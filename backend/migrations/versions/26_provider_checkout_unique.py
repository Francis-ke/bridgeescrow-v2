"""Prevent a provider checkout reference from crediting multiple payments."""
from alembic import op
revision = '26'
down_revision = '25'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('payments') as batch:
        batch.create_unique_constraint('uq_payment_provider_checkout', ['provider', 'checkout_request_id'])


def downgrade():
    with op.batch_alter_table('payments') as batch:
        batch.drop_constraint('uq_payment_provider_checkout', type_='unique')
