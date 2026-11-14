"""Freeze each SMS message's provider environment at enqueue time."""
import sqlalchemy as sa
from alembic import op
revision = '25'
down_revision = '24'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sms_messages') as batch:
        batch.add_column(sa.Column('environment', sa.String(16), nullable=False, server_default='local'))


def downgrade():
    with op.batch_alter_table('sms_messages') as batch:
        batch.drop_column('environment')
