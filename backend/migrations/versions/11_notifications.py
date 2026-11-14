"""Add private transaction notifications."""
import sqlalchemy as sa
from alembic import op

revision = "11"
down_revision = "10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("escrow_id", sa.Integer(), sa.ForeignKey("escrows.id"), nullable=False),
        sa.Column("event_key", sa.String(160), nullable=False, unique=True),
        sa.Column("message", sa.String(400), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade():
    op.drop_table("notifications")
