from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)  # 区域：hk, sg, jp, us 等
    country = Column(String(50), nullable=False)
    city = Column(String(50))
    ip_address = Column(String(45), nullable=False)
    port = Column(Integer, default=51820)
    protocol = Column(String(20), default="wireguard")
    public_key = Column(Text)  # WireGuard 公钥
    bandwidth_limit = Column(Integer)  # 节点带宽限制
    current_load = Column(Integer, default=0)  # 当前负载（用户数）
    max_load = Column(Integer, default=100)  # 最大负载
    status = Column(String(20), default="active")  # active, maintenance, offline
    is_premium = Column(Boolean, default=False)  # 高级节点
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
