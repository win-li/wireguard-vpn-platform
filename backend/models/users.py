from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    role = Column(String(20), default="user")  # user, admin, agent
    status = Column(String(20), default="active")  # active, suspended, deleted
    balance = Column(Integer, default=0)  # 余额（分）
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))
