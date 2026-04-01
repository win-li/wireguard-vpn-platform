from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 订阅创建
class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int
    auto_renew: bool = False

# 订阅更新
class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    auto_renew: Optional[bool] = None

# 订阅响应
class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    start_at: datetime
    expire_at: datetime
    bandwidth_used: int
    bandwidth_limit: Optional[int] = None
    auto_renew: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 订阅详情（含套餐信息）
class SubscriptionDetail(BaseModel):
    id: int
    user_id: int
    plan_id: int
    plan_name: str
    status: str
    start_at: datetime
    expire_at: datetime
    bandwidth_used: int
    bandwidth_limit: Optional[int] = None
    auto_renew: bool
    days_remaining: int
    bandwidth_remaining: Optional[int] = None
    created_at: datetime
