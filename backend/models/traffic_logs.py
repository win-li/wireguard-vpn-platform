from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    node_id = Column(Integer, ForeignKey("nodes.id"))
    bytes_sent = Column(BigInteger, default=0)
    bytes_received = Column(BigInteger, default=0)
    session_duration = Column(Integer)  # 会话时长（秒）
    client_ip = Column(String(45))
    logged_at = Column(DateTime, default=func.now())
