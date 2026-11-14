"""Add recipient receipt hold duration and reason."""
import sqlalchemy as sa
from alembic import op

revision = "10"
down_revision = "09"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("escrows", sa.Column("receipt_hold_until", sa.DateTime(), nullable=True))
    op.add_column("escrows", sa.Column("receipt_hold_reason", sa.String(400), nullable=True))


def downgrade():
    op.drop_column("escrows", "receipt_hold_reason")
    op.drop_column("escrows", "receipt_hold_until")
