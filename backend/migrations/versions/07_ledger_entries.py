"""create table ledger_entries

Revision ID: 07
Revises: 06
"""
from alembic import op

revision = "07"
down_revision = "06"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE ledger_entries (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	wallet_id INTEGER NOT NULL, 
    	escrow_id INTEGER, 
    	entry_type VARCHAR(16) NOT NULL, 
    	direction VARCHAR(6) NOT NULL, 
    	amount_cents BIGINT NOT NULL, 
    	reference VARCHAR(40) NOT NULL, 
    	description VARCHAR(190) NOT NULL, 
    	idempotency_key VARCHAR(80), 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_ledger_entries PRIMARY KEY (id), 
    	CONSTRAINT fk_ledger_entries_wallet_id_wallets FOREIGN KEY(wallet_id) REFERENCES wallets (id), 
    	CONSTRAINT fk_ledger_entries_escrow_id_escrows FOREIGN KEY(escrow_id) REFERENCES escrows (id), 
    	CONSTRAINT uq_ledger_entries_idempotency_key UNIQUE (idempotency_key)
    )""")
    op.execute("CREATE UNIQUE INDEX ix_ledger_entries_reference ON ledger_entries (reference)")
    op.execute("CREATE INDEX ix_ledger_entries_escrow_id ON ledger_entries (escrow_id)")
    op.execute("CREATE INDEX ix_ledger_entries_wallet_id ON ledger_entries (wallet_id)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS ledger_entries")
