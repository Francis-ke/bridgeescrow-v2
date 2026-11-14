"""Assign individual CVV display codes to local virtual cards."""
import secrets
import sqlalchemy as sa
from alembic import op

revision = "14"
down_revision = "13"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("card_cvv", sa.String(3), nullable=True))
    connection = op.get_bind()
    users = sa.table("users", sa.column("id", sa.Integer()), sa.column("card_cvv", sa.String(3)))
    codes = [f"{value:03d}" for value in range(1000) if value != 942]
    available = list(codes)
    for uid in connection.execute(sa.select(users.c.id)).scalars().all():
        code = secrets.choice(available or codes)
        if available:
            available.remove(code)
        connection.execute(users.update().where(users.c.id == uid).values(card_cvv=code))
    with op.batch_alter_table("users") as batch:
        batch.alter_column("card_cvv", existing_type=sa.String(3), nullable=False)


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("card_cvv")
