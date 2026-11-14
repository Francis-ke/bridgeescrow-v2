"""Keep simulated phone verification separate from live phone ownership."""
import sqlalchemy as sa
from alembic import op
revision = '22'
down_revision = '21'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('phone_verification_source', sa.String(24), nullable=True))
    with op.batch_alter_table('phone_challenges') as batch:
        batch.add_column(sa.Column('source', sa.String(24), nullable=False, server_default='simulated'))


def downgrade():
    with op.batch_alter_table('phone_challenges') as batch:
        batch.drop_column('source')
    with op.batch_alter_table('users') as batch:
        batch.drop_column('phone_verification_source')
