"""Seller API credentials, website orders, and scoped buyer checkout sessions."""
import sqlalchemy as sa
from alembic import op
revision = '19'
down_revision = '18'
branch_labels = None
depends_on = None


def times():
    return [sa.Column(name, sa.DateTime(), nullable=False) for name in ['created_at', 'updated_at']]


def upgrade():
    op.create_table('integration_profiles', sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('business_name', sa.String(140), nullable=False), sa.Column('website', sa.String(500), nullable=False),
        sa.Column('contact_email', sa.String(190), nullable=False), *times())
    op.create_table('merchant_api_keys', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(80), nullable=False), sa.Column('key_hash', sa.String(64), unique=True, nullable=False),
        sa.Column('key_prefix', sa.String(16), nullable=False), sa.Column('revoked_at', sa.DateTime()), *times())
    op.create_index('ix_merchant_api_keys_user_id', 'merchant_api_keys', ['user_id'])
    columns = [sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('seller_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('buyer_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('escrow_id', sa.Integer(), sa.ForeignKey('escrows.id'), unique=True)]
    for name, length in [('external_id', 100), ('public_token', 64), ('fingerprint', 64), ('currency', 3),
                         ('state', 16), ('return_url', 500)]:
        columns.append(sa.Column(name, sa.String(length), nullable=False, unique=name == 'public_token'))
    for name in ['items', 'seller_snapshot', 'buyer_snapshot']:
        columns.append(sa.Column(name, sa.JSON(), nullable=name == 'buyer_snapshot'))
    columns += [sa.Column('amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=False), sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('card_last4', sa.String(4)), sa.Column('delivery_hash', sa.String(64)),
        sa.Column('delivery_expires', sa.DateTime()), sa.Column('delivery_attempts', sa.Integer(), nullable=False),
        sa.Column('code_sent_at', sa.DateTime())]
    op.create_table('checkout_orders', *columns, *times(), sa.UniqueConstraint('seller_id', 'external_id'))
    op.create_index('ix_checkout_orders_seller_id', 'checkout_orders', ['seller_id'])
    columns = [sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('checkout_orders.id'), nullable=False),
        sa.Column('buyer_id', sa.Integer(), sa.ForeignKey('users.id'))]
    for name, length in [('challenge', 64), ('email', 190), ('full_name', 120), ('phone', 32),
                         ('address', 500), ('otp_hash', 64), ('session_hash', 64)]:
        columns.append(sa.Column(name, sa.String(length), nullable=name == 'session_hash',
                                 unique=name in ['challenge', 'session_hash']))
    columns += [sa.Column('expires_at', sa.DateTime(), nullable=False), sa.Column('attempts', sa.Integer(), nullable=False),
                sa.Column('sent_at', sa.DateTime(), nullable=False), sa.Column('session_expires', sa.DateTime())]
    op.create_table('checkout_auth', *columns, *times())
    op.create_index('ix_checkout_auth_order_id', 'checkout_auth', ['order_id'])


def downgrade():
    for table in ['checkout_auth', 'checkout_orders', 'merchant_api_keys', 'integration_profiles']:
        op.drop_table(table)
