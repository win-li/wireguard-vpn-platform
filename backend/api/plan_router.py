from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.users import User
from schemas.plans import PlanCreate, PlanUpdate, PlanResponse
from crud.plans import get_plan_by_id, get_plans, get_active_plans, create_plan, update_plan, delete_plan
from api.deps import get_current_user

router = APIRouter(prefix="/plans", tags=["plans"])

# 公开接口 - 获取所有可用套餐
@router.get("/active", response_model=List[PlanResponse])
def get_available_plans(db: Session = Depends(get_db)):
    """获取所有可用套餐（公开接口）"""
    return get_active_plans(db)

# 公开接口 - 获取单个套餐详情
@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan_detail(plan_id: int, db: Session = Depends(get_db)):
    """获取套餐详情（公开接口）"""
    plan = get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

# 管理接口 - 获取所有套餐（含禁用）
@router.get("/admin/all", response_model=List[PlanResponse])
def get_all_plans(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有套餐（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return get_plans(db, skip=skip, limit=limit)

# 管理接口 - 创建套餐
@router.post("/admin", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_new_plan(
    plan: PlanCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新套餐（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return create_plan(db, plan)

# 管理接口 - 更新套餐
@router.put("/admin/{plan_id}", response_model=PlanResponse)
def update_plan_info(
    plan_id: int, 
    plan_update: PlanUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新套餐（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    updated = update_plan(db, plan_id, plan_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return updated

# 管理接口 - 删除套餐
@router.delete("/admin/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_plan(
    plan_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除套餐（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    if not delete_plan(db, plan_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
