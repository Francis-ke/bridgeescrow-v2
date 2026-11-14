"""Add sender decisions for recipient hold requests."""
import sqlalchemy as sa
from alembic import op

revision = "12"
down_revision = "11"
branch_labels = None
depends_on = None


def upgrade():
    for name, datatype in [
        ("hold_request_hours", sa.Integer()), ("hold_request_reason", sa.String(400)),
        ("hold_request_status", sa.String(16)), ("hold_requested_at", sa.DateTime()),
        ("hold_decided_at", sa.DateTime())]:
        op.add_column("escrows", sa.Column(name, datatype, nullable=True))


def downgrade():
    for name in ["hold_decided_at", "hold_requested_at", "hold_request_status",
                 "hold_request_reason", "hold_request_hours"]:
        op.drop_column("escrows", name)
