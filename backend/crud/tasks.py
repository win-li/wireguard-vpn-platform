from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.user_tasks import Task, UserTask, PointExchange, PointExchangeRule
from models.daily_checkins import UserPoints
from crud.checkin import add_points, get_or_create_user_points
from datetime import datetime, date
from typing import List, Optional

# 默认任务配置
DEFAULT_TASKS = [
    {
        "name": "每日签到",
        "description": "每天签到可获得积分奖励",
        "task_type": "daily",
        "task_code": "daily_checkin",
        "points": 10,
        "reward_days": 0,
        "max_completions": 1,
        "sort_order": 1
    },
    {
        "name": "首次登录",
        "description": "完成首次登录获得奖励",
        "task_type": "one_time",
        "task_code": "first_login",
        "points": 50,
        "reward_days": 1,
        "max_completions": 1,
        "sort_order": 2
    },
    {
        "name": "邀请好友",
        "description": "成功邀请一位好友注册",
        "task_type": "achievement",
        "task_code": "invite_friend",
        "points": 100,
        "reward_days": 3,
        "max_completions": 0,  # 无限制
        "sort_order": 3
    },
    {
        "name": "分享给好友",
        "description": "分享给好友获得奖励",
        "task_type": "daily",
        "task_code": "share",
        "points": 5,
        "reward_days": 0,
        "max_completions": 1,
        "sort_order": 4
    },
    {
        "name": "完善个人资料",
        "description": "完善个人资料信息",
        "task_type": "one_time",
        "task_code": "complete_profile",
        "points": 20,
        "reward_days": 0,
        "max_completions": 1,
        "sort_order": 5
    },
]

# 默认积分兑换规则
DEFAULT_EXCHANGE_RULES = [
    {
        "name": "兑换1天会员",
        "description": "使用100积分兑换1天会员时长",
        "points_required": 100,
        "reward_type": "days",
        "reward_value": 1,
        "sort_order": 1
    },
    {
        "name": "兑换7天会员",
        "description": "使用500积分兑换7天会员时长",
        "points_required": 500,
        "reward_type": "days",
        "reward_value": 7,
        "sort_order": 2
    },
    {
        "name": "兑换30天会员",
        "description": "使用1800积分兑换30天会员时长",
        "points_required": 1800,
        "reward_type": "days",
        "reward_value": 30,
        "sort_order": 3
    },
]

def init_default_tasks(db: Session):
    """初始化默认任务"""
    for task_data in DEFAULT_TASKS:
        existing = db.query(Task).filter(Task.task_code == task_data["task_code"]).first()
        if not existing:
            task = Task(**task_data)
            db.add(task)
    db.commit()

def init_default_exchange_rules(db: Session):
    """初始化默认兑换规则"""
    for rule_data in DEFAULT_EXCHANGE_RULES:
        existing = db.query(PointExchangeRule).filter(
            PointExchangeRule.name == rule_data["name"]
        ).first()
        if not existing:
            rule = PointExchangeRule(**rule_data)
            db.add(rule)
    db.commit()

def get_all_tasks(db: Session, is_active: bool = True) -> List[Task]:
    """获取所有任务"""
    query = db.query(Task)
    if is_active:
        query = query.filter(Task.is_active == True)
    return query.order_by(Task.sort_order).all()

def get_task_by_code(db: Session, task_code: str) -> Optional[Task]:
    """根据任务代码获取任务"""
    return db.query(Task).filter(Task.task_code == task_code).first()

def get_or_create_user_task(db: Session, user_id: int, task_id: int) -> UserTask:
    """获取或创建用户任务记录"""
    user_task = db.query(UserTask).filter(
        and_(
            UserTask.user_id == user_id,
            UserTask.task_id == task_id
        )
    ).first()
    
    if not user_task:
        user_task = UserTask(
            user_id=user_id,
            task_id=task_id,
            completion_count=0,
            status="available",
            points_earned=0
        )
        db.add(user_task)
        db.commit()
        db.refresh(user_task)
    
    return user_task

def get_user_tasks(db: Session, user_id: int) -> List[dict]:
    """获取用户任务列表"""
    tasks = get_all_tasks(db)
    result = []
    
    for task in tasks:
        user_task = get_or_create_user_task(db, user_id, task.id)
        
        # 判断是否可以完成
        can_complete = True
        if task.max_completions > 0 and user_task.completion_count >= task.max_completions:
            can_complete = False
        
        # 每日任务检查是否今天已完成
        if task.task_type == "daily" and user_task.last_completed_at:
            if user_task.last_completed_at.date() == date.today():
                can_complete = False
        
        result.append({
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "task_type": task.task_type,
            "task_code": task.task_code,
            "points": task.points,
            "reward_days": task.reward_days,
            "max_completions": task.max_completions,
            "completion_count": user_task.completion_count,
            "status": user_task.status,
            "can_complete": can_complete
        })
    
    return result

def complete_task(db: Session, user_id: int, task_code: str):
    """完成任务"""
    task = get_task_by_code(db, task_code)
    if not task:
        return {"success": False, "message": "任务不存在"}
    
    if not task.is_active:
        return {"success": False, "message": "任务已禁用"}
    
    user_task = get_or_create_user_task(db, user_id, task.id)
    
    # 检查完成次数限制
    if task.max_completions > 0 and user_task.completion_count >= task.max_completions:
        return {"success": False, "message": "任务已完成,无法重复完成"}
    
    # 每日任务检查
    if task.task_type == "daily" and user_task.last_completed_at:
        if user_task.last_completed_at.date() == date.today():
            return {"success": False, "message": "今日任务已完成,请明天再来"}
    
    # 更新任务状态
    user_task.completion_count += 1
    user_task.last_completed_at = datetime.now()
    user_task.status = "completed"
    user_task.points_earned += task.points
    
    # 添加积分
    add_points(db, user_id, task.points, "task", f"完成任务:{task.name}", task.id)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"任务完成!获得{task.points}积分",
        "points_earned": task.points,
        "task_name": task.name
    }

def get_exchange_rules(db: Session, is_active: bool = True) -> List[PointExchangeRule]:
    """获取积分兑换规则"""
    query = db.query(PointExchangeRule)
    if is_active:
        query = query.filter(PointExchangeRule.is_active == True)
    return query.order_by(PointExchangeRule.sort_order).all()

def exchange_points(db: Session, user_id: int, rule_id: int):
    """积分兑换"""
    rule = db.query(PointExchangeRule).filter(PointExchangeRule.id == rule_id).first()
    if not rule or not rule.is_active:
        return {"success": False, "message": "兑换规则不存在或已禁用"}
    
    user_points = get_or_create_user_points(db, user_id)
    if user_points.balance < rule.points_required:
        return {"success": False, "message": "积分不足"}
    
    # 扣除积分
    from crud.checkin import use_points
    transaction = use_points(db, user_id, rule.points_required, "exchange", 
                            f"兑换:{rule.name}", rule.id)
    if not transaction:
        return {"success": False, "message": "积分扣除失败"}
    
    # 创建兑换记录
    exchange = PointExchange(
        user_id=user_id,
        points_used=rule.points_required,
        reward_type=rule.reward_type,
        reward_value=rule.reward_value,
        reward_description=rule.name
    )
    db.add(exchange)
    db.commit()
    
    return {
        "success": True,
        "message": "兑换成功!",
        "points_used": rule.points_required,
        "reward_type": rule.reward_type,
        "reward_value": rule.reward_value,
        "reward_description": rule.name
    }
