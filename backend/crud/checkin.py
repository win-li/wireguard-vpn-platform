from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models.daily_checkins import DailyCheckin, CheckinStreak, UserPoints, PointTransaction
from models.user_tasks import Task, UserTask, PointExchange, PointExchangeRule
from datetime import datetime, date, timedelta
from typing import List, Optional

# 签到奖励配置
BASE_CHECKIN_POINTS = 10  # 基础签到积分
CONSECUTIVE_BONUS = {
    7: 50,    # 连续7天额外奖励
    14: 100,  # 连续14天额外奖励
    30: 300,  # 连续30天额外奖励
}

def get_or_create_user_points(db: Session, user_id: int) -> UserPoints:
    """获取或创建用户积分"""
    points = db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
    if not points:
        points = UserPoints(
            user_id=user_id,
            total_points=0,
            used_points=0,
            balance=0
        )
        db.add(points)
        db.commit()
        db.refresh(points)
    return points

def get_or_create_streak(db: Session, user_id: int) -> CheckinStreak:
    """获取或创建连续签到记录"""
    streak = db.query(CheckinStreak).filter(CheckinStreak.user_id == user_id).first()
    if not streak:
        streak = CheckinStreak(
            user_id=user_id,
            current_streak=0,
            max_streak=0,
            last_checkin_date=None,
            total_checkins=0
        )
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak

def add_points(db: Session, user_id: int, amount: int, type: str, 
               description: str = None, related_id: int = None) -> PointTransaction:
    """添加积分"""
    user_points = get_or_create_user_points(db, user_id)
    user_points.total_points += amount
    user_points.balance += amount
    
    transaction = PointTransaction(
        user_id=user_id,
        amount=amount,
        balance_after=user_points.balance,
        type=type,
        description=description,
        related_id=related_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def use_points(db: Session, user_id: int, amount: int, type: str,
               description: str = None, related_id: int = None) -> PointTransaction:
    """使用积分"""
    user_points = get_or_create_user_points(db, user_id)
    if user_points.balance < amount:
        return None
    
    user_points.used_points += amount
    user_points.balance -= amount
    
    transaction = PointTransaction(
        user_id=user_id,
        amount=-amount,
        balance_after=user_points.balance,
        type=type,
        description=description,
        related_id=related_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def do_daily_checkin(db: Session, user_id: int):
    """执行每日签到"""
    today = date.today()
    today_datetime = datetime.combine(today, datetime.min.time())
    
    # 检查今天是否已签到
    existing = db.query(DailyCheckin).filter(
        and_(
            DailyCheckin.user_id == user_id,
            func.date(DailyCheckin.checkin_date) == today
        )
    ).first()
    
    if existing:
        return {"success": False, "message": "今天已经签到了", "points_earned": 0}
    
    # 获取或创建连续签到记录
    streak = get_or_create_streak(db, user_id)
    
    # 计算连续签到天数
    yesterday = today - timedelta(days=1)
    if streak.last_checkin_date and streak.last_checkin_date.date() == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    
    streak.last_checkin_date = today_datetime
    streak.total_checkins += 1
    if streak.current_streak > streak.max_streak:
        streak.max_streak = streak.current_streak
    
    # 计算奖励积分
    points_earned = BASE_CHECKIN_POINTS
    bonus_points = 0
    
    # 连续签到奖励
    for days, bonus in sorted(CONSECUTIVE_BONUS.items(), reverse=True):
        if streak.current_streak >= days and streak.current_streak % days == 0:
            bonus_points += bonus
            break
    
    total_points = points_earned + bonus_points
    
    # 创建签到记录
    checkin = DailyCheckin(
        user_id=user_id,
        checkin_date=today_datetime,
        consecutive_days=streak.current_streak,
        points_earned=points_earned,
        bonus_points=bonus_points
    )
    db.add(checkin)
    
    # 添加积分
    add_points(db, user_id, total_points, "checkin", 
               f"签到奖励(连续{streak.current_streak}天)")
    
    db.commit()
    
    user_points = get_or_create_user_points(db, user_id)
    
    return {
        "success": True,
        "message": f"签到成功!连续签到{streak.current_streak}天",
        "points_earned": points_earned,
        "bonus_points": bonus_points,
        "consecutive_days": streak.current_streak,
        "total_points": user_points.balance
    }

def get_checkin_status(db: Session, user_id: int):
    """获取签到状态"""
    today = date.today()
    
    # 检查今天是否已签到
    today_checkin = db.query(DailyCheckin).filter(
        and_(
            DailyCheckin.user_id == user_id,
            func.date(DailyCheckin.checkin_date) == today
        )
    ).first()
    
    streak = get_or_create_streak(db, user_id)
    user_points = get_or_create_user_points(db, user_id)
    
    return {
        "today_checked_in": today_checkin is not None,
        "current_streak": streak.current_streak,
        "max_streak": streak.max_streak,
        "total_checkins": streak.total_checkins,
        "last_checkin_date": streak.last_checkin_date,
        "points_balance": user_points.balance
    }

def get_point_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取积分交易记录"""
    return db.query(PointTransaction).filter(
        PointTransaction.user_id == user_id
    ).order_by(PointTransaction.created_at.desc()).offset(skip).limit(limit).all()
