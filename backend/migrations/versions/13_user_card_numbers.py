"""Give each user a distinct persistent virtual card identifier."""
import secrets
import sqlalchemy as sa
from alembic import op

revision = "13"
down_revision = "12"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("card_number", sa.String(16), nullable=True))
    connection = op.get_bind()
    users = sa.table("users", sa.column("id", sa.Integer()), sa.column("card_number", sa.String(16)))
    used = set()
    for uid in connection.execute(sa.select(users.c.id)).scalars().all():
        number = f"9900{secrets.randbelow(10**12):012d}"
        while number in used:
            number = f"9900{secrets.randbelow(10**12):012d}"
        used.add(number)
        connection.execute(users.update().where(users.c.id == uid).values(card_number=number))
    with op.batch_alter_table("users") as batch:
        batch.alter_column("card_number", existing_type=sa.String(16), nullable=False)
        batch.create_index("ix_users_card_number", ["card_number"], unique=True)


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_index("ix_users_card_number")
        batch.drop_column("card_number")
