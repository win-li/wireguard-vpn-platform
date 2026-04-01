from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CheckinResponse(BaseModel):
    success: bool
    message: str
    points_earned: int
    bonus_points: int
    consecutive_days: int
    total_points: int

class CheckinStatus(BaseModel):
    today_checked_in: bool
    current_streak: int
    max_streak: int
    total_checkins: int
    last_checkin_date: Optional[datetime]
    points_balance: int

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    task_type: str
    task_code: str
    points: int
    reward_days: int
    max_completions: int
    completion_count: int
    status: str
    can_complete: bool

    class Config:
        from_attributes = True

class TaskCompleteRequest(BaseModel):
    task_code: str

class TaskCompleteResponse(BaseModel):
    success: bool
    message: str
    points_earned: int
    task_name: str

class PointExchangeRequest(BaseModel):
    rule_id: int

class PointExchangeResponse(BaseModel):
    success: bool
    message: str
    points_used: int
    reward_type: str
    reward_value: int
    reward_description: str

class PointBalanceResponse(BaseModel):
    total_points: int
    used_points: int
    balance: int

    class Config:
        from_attributes = True

class PointTransactionResponse(BaseModel):
    id: int
    amount: int
    balance_after: int
    type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ExchangeRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    points_required: int
    reward_type: str
    reward_value: int
    is_active: bool

    class Config:
        from_attributes = True
