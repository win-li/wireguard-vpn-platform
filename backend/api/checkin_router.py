from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from api.deps import get_current_user
from models.users import User
from schemas.checkin import (
    CheckinResponse,
    CheckinStatus,
    TaskListResponse,
    TaskCompleteRequest,
    TaskCompleteResponse,
    PointExchangeRequest,
    PointExchangeResponse,
    PointBalanceResponse,
    PointTransactionResponse,
    ExchangeRuleResponse
)
from crud.checkin import (
    do_daily_checkin,
    get_checkin_status,
    get_point_transactions,
    get_or_create_user_points
)
from crud.tasks import (
    get_user_tasks,
    complete_task,
    get_exchange_rules,
    exchange_points,
    init_default_tasks,
    init_default_exchange_rules
)

router = APIRouter()

# ============ 签到相关 ============

@router.post("/daily", response_model=CheckinResponse)
def daily_checkin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """每日签到"""
    result = do_daily_checkin(db, current_user.id)
    return CheckinResponse(**result)

@router.get("/status", response_model=CheckinStatus)
def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取签到状态"""
    status = get_checkin_status(db, current_user.id)
    return CheckinStatus(**status)

@router.get("/points", response_model=PointBalanceResponse)
def get_points(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取积分余额"""
    user_points = get_or_create_user_points(db, current_user.id)
    return PointBalanceResponse.from_orm(user_points)

@router.get("/points/transactions", response_model=List[PointTransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取积分交易记录"""
    transactions = get_point_transactions(db, current_user.id, skip, limit)
    return [PointTransactionResponse.from_orm(t) for t in transactions]

# ============ 任务相关 ============

@router.get("/tasks/list", response_model=List[TaskListResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取任务列表"""
    # 初始化默认任务
    init_default_tasks(db)
    
    tasks = get_user_tasks(db, current_user.id)
    return [TaskListResponse(**t) for t in tasks]

@router.post("/tasks/complete", response_model=TaskCompleteResponse)
def complete_user_task(
    request: TaskCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """完成任务"""
    result = complete_task(db, current_user.id, request.task_code)
    return TaskCompleteResponse(**result)

# ============ 积分兑换 ============

@router.get("/exchange/rules", response_model=List[ExchangeRuleResponse])
def list_exchange_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取积分兑换规则"""
    # 初始化默认规则
    init_default_exchange_rules(db)
    
    rules = get_exchange_rules(db)
    return [ExchangeRuleResponse.from_orm(r) for r in rules]

@router.post("/exchange", response_model=PointExchangeResponse)
def exchange_user_points(
    request: PointExchangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """积分兑换"""
    result = exchange_points(db, current_user.id, request.rule_id)
    return PointExchangeResponse(**result)
