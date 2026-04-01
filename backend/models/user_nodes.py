from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class UserNode(Base):
    __tablename__ = "user_nodes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"))
    private_key = Column(Text, nullable=False)  # 用户 WireGuard 私钥
    allowed_ips = Column(String(255))  # 允许的 IP 范围
    connected_at = Column(DateTime)
    disconnected_at = Column(DateTime)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
