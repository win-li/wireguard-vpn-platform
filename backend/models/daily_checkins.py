from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Boolean, Text
from sqlalchemy.sql import func
from config.database import Base

class DailyCheckin(Base):
    """每日签到记录表"""
    __tablename__ = "daily_checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    checkin_date = Column(DateTime, nullable=False, index=True)
    consecutive_days = Column(Integer, default=1)
    points_earned = Column(Integer, default=0)
    bonus_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class CheckinStreak(Base):
    """用户连续签到记录表"""
    __tablename__ = "checkin_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_checkin_date = Column(DateTime)
    total_checkins = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserPoints(Base):
    """用户积分表"""
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    total_points = Column(Integer, default=0)
    used_points = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PointTransaction(Base):
    """积分交易记录表"""
    __tablename__ = "point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(String(255))
    related_id = Column(Integer)
    created_at = Column(DateTime, default=func.now())
