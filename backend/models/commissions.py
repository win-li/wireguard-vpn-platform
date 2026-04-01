from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Boolean, Text
from sqlalchemy.sql import func
from config.database import Base

class Commission(Base):
    """佣金记录表"""
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    level = Column(Integer, default=1)
    order_id = Column(Integer, ForeignKey("payments.id"))
    order_amount = Column(DECIMAL(10, 2))
    commission_rate = Column(DECIMAL(5, 4))
    commission_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    settled_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CommissionWithdrawal(Base):
    """佣金提现记录表"""
    __tablename__ = "commission_withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    withdraw_method = Column(String(50), nullable=False)
    account_info = Column(Text)
    status = Column(String(20), default="pending")
    reject_reason = Column(String(255))
    processed_at = Column(DateTime)
    transaction_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserCommissionBalance(Base):
    """用户佣金余额表"""
    __tablename__ = "user_commission_balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    total_earned = Column(DECIMAL(10, 2), default=0)
    total_withdrawn = Column(DECIMAL(10, 2), default=0)
    balance = Column(DECIMAL(10, 2), default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
