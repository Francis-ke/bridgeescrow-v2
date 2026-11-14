"""create table payments

Revision ID: 08
Revises: 07
"""
from alembic import op

revision = "08"
down_revision = "07"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE payments (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	reference VARCHAR(32) NOT NULL, 
    	wallet_id INTEGER NOT NULL, 
    	kind VARCHAR(16) NOT NULL, 
    	msisdn VARCHAR(20) NOT NULL, 
    	amount_cents BIGINT NOT NULL, 
    	status VARCHAR(16) NOT NULL, 
    	checkout_request_id VARCHAR(64), 
    	receipt VARCHAR(32), 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_payments PRIMARY KEY (id), 
    	CONSTRAINT fk_payments_wallet_id_wallets FOREIGN KEY(wallet_id) REFERENCES wallets (id)
    )""")
    op.execute("CREATE INDEX ix_payments_checkout_request_id ON payments (checkout_request_id)")
    op.execute("CREATE INDEX ix_payments_wallet_id ON payments (wallet_id)")
    op.execute("CREATE UNIQUE INDEX ix_payments_reference ON payments (reference)")
    op.execute("CREATE INDEX ix_payments_status ON payments (status)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS payments")
