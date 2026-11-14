"""add web identity and email OTP challenges

Revision ID: 09
Revises: 08
"""
import sqlalchemy as sa
from alembic import op

revision = "09"
down_revision = "08"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("national_id", sa.String(32), nullable=True))
    op.create_index("ix_users_national_id", "users", ["national_id"], unique=True)
    op.add_column("users", sa.Column("email_verified", sa.Boolean(),
                                      nullable=False, server_default=sa.true()))
    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(24), nullable=False),
        sa.Column("challenge_token", sa.String(64), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],
                                name="fk_otp_challenges_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_otp_challenges"),
        sa.UniqueConstraint("challenge_token", name="uq_otp_challenges_challenge_token"),
    )
    op.create_index("ix_otp_challenges_user_id", "otp_challenges", ["user_id"])
    op.create_index("ix_otp_challenges_purpose", "otp_challenges", ["purpose"])


def downgrade():
    op.drop_index("ix_otp_challenges_purpose", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_user_id", table_name="otp_challenges")
    op.drop_table("otp_challenges")
    op.drop_column("users", "email_verified")
    op.drop_index("ix_users_national_id", table_name="users")
    op.drop_column("users", "national_id")
