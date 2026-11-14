"""Allow wallet notifications and backfill completed demo deposits."""
import sqlalchemy as sa
from alembic import op

revision = '16'
down_revision = '15'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('notifications') as batch:
        batch.alter_column('escrow_id', existing_type=sa.Integer(), nullable=True)
    connection = op.get_bind()
    rows = connection.execute(sa.text(
        "SELECT id,user_id,reference,amount_cents,created_at FROM demo_transactions WHERE kind='deposit'"
    )).mappings().all()
    for row in rows:
        key = f"demo-deposit-{row['id']}"
        exists = connection.execute(sa.text('SELECT id FROM notifications WHERE event_key=:key'), {'key': key}).first()
        if not exists:
            cents = row['amount_cents']
            connection.execute(sa.text('''INSERT INTO notifications
                (user_id,escrow_id,event_key,message,read_at,created_at,updated_at)
                VALUES (:uid,NULL,:key,:message,NULL,:time,:time)'''), {
                    'uid': row['user_id'], 'key': key, 'time': row['created_at'],
                    'message': f"Demo deposit of KES {cents // 100}.{cents % 100:02d} added to your wallet. Reference: {row['reference']}"})


def downgrade():
    op.execute('DELETE FROM notifications WHERE escrow_id IS NULL')
    with op.batch_alter_table('notifications') as batch:
        batch.alter_column('escrow_id', existing_type=sa.Integer(), nullable=False)
