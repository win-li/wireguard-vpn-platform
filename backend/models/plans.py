from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)  # 订阅天数
    bandwidth_limit = Column(Integer)  # 流量限制（字节），NULL 表示不限
    device_limit = Column(Integer, default=3)  # 设备数量限制
    node_access = Column(String)  # 可访问的节点 ID 列表（JSON 格式）
    features = Column(String)  # 其他特性（JSON 格式）
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
