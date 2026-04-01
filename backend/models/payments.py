from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, ForeignKey, Boolean
from sqlalchemy.sql import func
from config.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="CNY")
    payment_method = Column(String(50))  # alipay, wechat, stripe, usdt_trc20, usdt_erc20
    transaction_id = Column(String(255))  # 第三方交易 ID
    
    # USDT 支付专用字段
    wallet_address = Column(String(255))  # 收款钱包地址
    network_type = Column(String(20))  # TRC20 或 ERC20
    tx_hash = Column(String(255))  # 链上交易哈希
    usdt_amount = Column(DECIMAL(20, 6))  # USDT金额（精确到6位小数）
    expires_at = Column(DateTime)  # 支付过期时间
    
    status = Column(String(20), default="pending")  # pending, success, failed, refunded, expired
    # 使用name参数映射数据库中的metadata字段到payment_metadata属性
    payment_metadata = Column("metadata", Text)  # 额外信息（JSON 格式）
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class USDTWallet(Base):
    """USDT收款钱包池"""
    __tablename__ = "usdt_wallets"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), unique=True, nullable=False)
    network = Column(String(20), nullable=False)  # TRC20 或 ERC20
    private_key_encrypted = Column(Text)  # 加密的私钥（可选，用于热钱包）
    is_active = Column(Boolean, default=True)
    current_payment_id = Column(Integer, ForeignKey("payments.id"))  # 当前绑定的支付订单
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
