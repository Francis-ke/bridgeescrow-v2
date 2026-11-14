"""Use neutral transaction labels in stored interface content."""
import sqlalchemy as sa
from alembic import op
revision = '17'
down_revision = '16'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for table, columns in {
        'demo_transactions': ['reference'], 'ledger_entries': ['description'],
        'notifications': ['message'], 'escrows': ['title'],
    }.items():
        for column in columns:
            connection.execute(sa.text(f'''UPDATE {table} SET {column} =
                replace(replace(replace({column}, 'DEMO-', 'TXN-'), 'Demo ', ''), 'demo ', '')
                WHERE {column} LIKE '%Demo %' OR {column} LIKE '%DEMO-%' '''))


def downgrade():
    # Presentation-only wording does not alter account data or transactions.
    pass
