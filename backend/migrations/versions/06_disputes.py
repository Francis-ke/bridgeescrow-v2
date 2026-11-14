"""create table disputes

Revision ID: 06
Revises: 05
"""
from alembic import op

revision = "06"
down_revision = "05"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE disputes (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	escrow_id INTEGER NOT NULL, 
    	raised_by INTEGER NOT NULL, 
    	reason VARCHAR(400) NOT NULL, 
    	status VARCHAR(16) NOT NULL, 
    	resolution VARCHAR(400), 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_disputes PRIMARY KEY (id), 
    	CONSTRAINT fk_disputes_escrow_id_escrows FOREIGN KEY(escrow_id) REFERENCES escrows (id), 
    	CONSTRAINT fk_disputes_raised_by_users FOREIGN KEY(raised_by) REFERENCES users (id)
    )""")
    op.execute("CREATE INDEX ix_disputes_escrow_id ON disputes (escrow_id)")
    op.execute("CREATE INDEX ix_disputes_status ON disputes (status)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS disputes")
