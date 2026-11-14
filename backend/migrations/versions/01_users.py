"""create table users

Revision ID: 01
Revises: None
"""
from alembic import op

revision = "01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE users (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	account_number VARCHAR(16) NOT NULL, 
    	full_name VARCHAR(120) NOT NULL, 
    	email VARCHAR(190) NOT NULL, 
    	phone VARCHAR(20) NOT NULL, 
    	password_hash VARCHAR(255) NOT NULL, 
    	pin_salt VARCHAR(64), 
    	pin_hash VARCHAR(128), 
    	pin_attempts INTEGER NOT NULL, 
    	`role` VARCHAR(16) NOT NULL, 
    	is_active BOOL NOT NULL, 
    	last_login_at DATETIME, 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_users PRIMARY KEY (id)
    )""")
    op.execute("CREATE UNIQUE INDEX ix_users_phone ON users (phone)")
    op.execute("CREATE UNIQUE INDEX ix_users_account_number ON users (account_number)")
    op.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS users")
