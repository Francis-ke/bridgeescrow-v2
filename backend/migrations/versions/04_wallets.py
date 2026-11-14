"""create table wallets

Revision ID: 04
Revises: 03
"""
from alembic import op

revision = "04"
down_revision = "03"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE wallets (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	user_id INTEGER NOT NULL, 
    	currency VARCHAR(3) NOT NULL, 
    	available_cents BIGINT NOT NULL, 
    	escrow_cents BIGINT NOT NULL, 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_wallets PRIMARY KEY (id), 
    	CONSTRAINT uq_wallets_user_id UNIQUE (user_id), 
    	CONSTRAINT fk_wallets_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
    )""")



def downgrade():
    op.execute("DROP TABLE IF EXISTS wallets")
