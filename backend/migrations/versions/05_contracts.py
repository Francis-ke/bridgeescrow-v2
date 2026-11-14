"""create table contracts

Revision ID: 05
Revises: 04
"""
from alembic import op

revision = "05"
down_revision = "04"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE contracts (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	escrow_id INTEGER NOT NULL, 
    	terms TEXT NOT NULL, 
    	delivery_days INTEGER NOT NULL, 
    	buyer_signed_at DATETIME, 
    	seller_signed_at DATETIME, 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_contracts PRIMARY KEY (id), 
    	CONSTRAINT uq_contracts_escrow_id UNIQUE (escrow_id), 
    	CONSTRAINT fk_contracts_escrow_id_escrows FOREIGN KEY(escrow_id) REFERENCES escrows (id)
    )""")



def downgrade():
    op.execute("DROP TABLE IF EXISTS contracts")
