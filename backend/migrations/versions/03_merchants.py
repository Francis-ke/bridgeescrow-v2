"""create table merchants

Revision ID: 03
Revises: 02
"""
from alembic import op

revision = "03"
down_revision = "02"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""CREATE TABLE merchants (
    	id INTEGER NOT NULL AUTO_INCREMENT, 
    	user_id INTEGER NOT NULL, 
    	business_name VARCHAR(140) NOT NULL, 
    	till_number VARCHAR(12) NOT NULL, 
    	paybill VARCHAR(12), 
    	status VARCHAR(16) NOT NULL, 
    	created_at DATETIME NOT NULL, 
    	updated_at DATETIME NOT NULL, 
    	CONSTRAINT pk_merchants PRIMARY KEY (id), 
    	CONSTRAINT uq_merchants_user_id UNIQUE (user_id), 
    	CONSTRAINT fk_merchants_user_id_users FOREIGN KEY(user_id) REFERENCES users (id), 
    	CONSTRAINT uq_merchants_till_number UNIQUE (till_number)
    )""")



def downgrade():
    op.execute("DROP TABLE IF EXISTS merchants")
