from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Boolean, Text
from sqlalchemy.sql import func
from config.database import Base

class Task(Base):
    """任务定义表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    task_type = Column(String(50), nullable=False)
    task_code = Column(String(50), unique=True, nullable=False)
    points = Column(Integer, default=0)
    reward_days = Column(Integer, default=0)
    max_completions = Column(Integer, default=1)
    requirements = Column(Text)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserTask(Base):
    """用户任务完成记录表"""
    __tablename__ = "user_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    completion_count = Column(Integer, default=0)
    last_completed_at = Column(DateTime)
    status = Column(String(20), default="available")
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PointExchange(Base):
    """积分兑换记录表"""
    __tablename__ = "point_exchanges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    points_used = Column(Integer, nullable=False)
    reward_type = Column(String(50), nullable=False)
    reward_value = Column(Integer, nullable=False)
    reward_description = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class PointExchangeRule(Base):
    """积分兑换规则表"""
    __tablename__ = "point_exchange_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    points_required = Column(Integer, nullable=False)
    reward_type = Column(String(50), nullable=False)
    reward_value = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
