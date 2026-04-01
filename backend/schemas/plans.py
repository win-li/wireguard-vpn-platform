from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

# 套餐创建
class PlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    duration_days: int
    bandwidth_limit: Optional[int] = None
    device_limit: int = 3
    node_access: Optional[str] = None
    features: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

# 套餐更新
class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    duration_days: Optional[int] = None
    bandwidth_limit: Optional[int] = None
    device_limit: Optional[int] = None
    node_access: Optional[str] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

# 套餐响应
class PlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    duration_days: int
    bandwidth_limit: Optional[int] = None
    device_limit: int
    node_access: Optional[str] = None
    features: Optional[str] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
