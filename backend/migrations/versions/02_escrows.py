"""create table escrows

Revision ID: 02
Revises: 01
"""
from alembic import op

revision = "02"
down_revision = "01"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE escrows (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	reference VARCHAR(24) NOT NULL, 
    	buyer_id INTEGER NOT NULL, 
    	seller_id INTEGER NOT NULL, 
    	amount_cents BIGINT NOT NULL, 
    	fee_cents BIGINT NOT NULL, 
    	currency VARCHAR(3) NOT NULL, 
    	title VARCHAR(140) NOT NULL, 
    	status VARCHAR(16) NOT NULL, 
    	release_code_hash VARCHAR(128), 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_escrows PRIMARY KEY (id), 
    	CONSTRAINT fk_escrows_buyer_id_users FOREIGN KEY(buyer_id) REFERENCES users (id), 
    	CONSTRAINT fk_escrows_seller_id_users FOREIGN KEY(seller_id) REFERENCES users (id)
    )""")
    op.execute("CREATE UNIQUE INDEX ix_escrows_reference ON escrows (reference)")
    op.execute("CREATE INDEX ix_escrows_status ON escrows (status)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS escrows")
