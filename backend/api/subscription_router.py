from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config.database import get_db
from models.users import User
from models.plans import Plan
from schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionDetail
from crud.subscriptions import (
    get_subscription_by_id, 
    get_user_subscriptions, 
    get_user_active_subscription,
    get_subscriptions,
    create_subscription, 
    update_subscription, 
    cancel_subscription,
    check_expired_subscriptions
)
from crud.plans import get_plan_by_id
from api.deps import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# 用户接口 - 获取当前订阅
@router.get("/me", response_model=SubscriptionDetail)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的活跃订阅"""
    sub = get_user_active_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription"
        )
    plan = get_plan_by_id(db, sub.plan_id)
    days_remaining = max(0, (sub.expire_at - datetime.now()).days)
    bandwidth_remaining = None
    if sub.bandwidth_limit:
        bandwidth_remaining = max(0, sub.bandwidth_limit - sub.bandwidth_used)
    
    return SubscriptionDetail(
        id=sub.id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        plan_name=plan.name if plan else "Unknown",
        status=sub.status,
        start_at=sub.start_at,
        expire_at=sub.expire_at,
        bandwidth_used=sub.bandwidth_used,
        bandwidth_limit=sub.bandwidth_limit,
        auto_renew=sub.auto_renew,
        days_remaining=days_remaining,
        bandwidth_remaining=bandwidth_remaining,
        created_at=sub.created_at
    )

# 用户接口 - 获取订阅历史
@router.get("/history", response_model=List[SubscriptionResponse])
def get_subscription_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的订阅历史"""
    return get_user_subscriptions(db, current_user.id, skip, limit)

# 用户接口 - 购买订阅
@router.post("/purchase", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def purchase_subscription(
    sub: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """购买订阅"""
    # 验证套餐
    plan = get_plan_by_id(db, sub.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive plan"
        )
    
    # 检查是否已有活跃订阅
    active = get_user_active_subscription(db, current_user.id)
    if active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have an active subscription"
        )
    
    # 使用当前用户ID
    sub.user_id = current_user.id
    return create_subscription(db, sub, plan)

# 用户接口 - 取消订阅
@router.post("/{sub_id}/cancel", response_model=SubscriptionResponse)
def cancel_my_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消订阅"""
    sub = get_subscription_by_id(db, sub_id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    if sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return cancel_subscription(db, sub_id)

# 用户接口 - 设置自动续费
@router.put("/{sub_id}/autorenew", response_model=SubscriptionResponse)
def toggle_autorenew(
    sub_id: int,
    auto_renew: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置自动续费"""
    sub = get_subscription_by_id(db, sub_id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    if sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return update_subscription(db, sub_id, SubscriptionUpdate(auto_renew=auto_renew))

# 管理接口 - 获取所有订阅
@router.get("/admin/all", response_model=List[SubscriptionResponse])
def get_all_subscriptions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有订阅（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return get_subscriptions(db, skip, limit, status)

# 管理接口 - 更新订阅状态
@router.put("/admin/{sub_id}", response_model=SubscriptionResponse)
def admin_update_subscription(
    sub_id: int,
    sub_update: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订阅（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    updated = update_subscription(db, sub_id, sub_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    return updated

# 系统接口 - 检查过期订阅
@router.post("/system/check-expired")
def check_expired(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查并更新过期订阅（系统调用）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    expired = check_expired_subscriptions(db)
    return {"expired_count": len(expired), "expired_ids": [s.id for s in expired]}
