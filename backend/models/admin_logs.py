from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func
from config.database import Base

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    target_type = Column(String(50))  # user, node, plan 等
    target_id = Column(Integer)
    log_details = Column(Text)  # 详情（JSON 格式）
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())
