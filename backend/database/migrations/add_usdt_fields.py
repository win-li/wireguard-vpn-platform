"""
数据库迁移：添加USDT支付相关字段
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # 添加USDT支付字段到payments表
    op.add_column('payments', sa.Column('wallet_address', sa.String(255), nullable=True))
    op.add_column('payments', sa.Column('network_type', sa.String(20), nullable=True))
    op.add_column('payments', sa.Column('tx_hash', sa.String(255), nullable=True))
    op.add_column('payments', sa.Column('usdt_amount', sa.DECIMAL(20, 6), nullable=True))
    op.add_column('payments', sa.Column('expires_at', sa.DateTime, nullable=True))
    
    # 创建USDT钱包表
    op.create_table(
        'usdt_wallets',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('address', sa.String(255), unique=True, nullable=False),
        sa.Column('network', sa.String(20), nullable=False),
        sa.Column('private_key_encrypted', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('current_payment_id', sa.Integer, sa.ForeignKey('payments.id'), nullable=True),
        sa.Column('last_used_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.now)
    )

def downgrade():
    # 删除USDT钱包表
    op.drop_table('usdt_wallets')
    
    # 删除payments表的USDT字段
    op.drop_column('payments', 'wallet_address')
    op.drop_column('payments', 'network_type')
    op.drop_column('payments', 'tx_hash')
    op.drop_column('payments', 'usdt_amount')
    op.drop_column('payments', 'expires_at')
