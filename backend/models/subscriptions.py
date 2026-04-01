from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    status = Column(String(20), default="active")  # active, expired, cancelled, pending
    start_at = Column(DateTime, nullable=False)
    expire_at = Column(DateTime, nullable=False)
    bandwidth_used = Column(Integer, default=0)  # 已用流量（字节）
    bandwidth_limit = Column(Integer)  # 流量限制
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
