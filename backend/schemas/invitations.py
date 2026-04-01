from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class InviteCodeGenerate(BaseModel):
    pass

class InviteCodeResponse(BaseModel):
    invite_code: str
    total_invites: int
    successful_invites: int
    share_url: str

    class Config:
        from_attributes = True

class InvitationRegister(BaseModel):
    invite_code: str
    email: str
    password: str
    username: Optional[str] = None

class InvitationStats(BaseModel):
    total_invites: int
    successful_invites: int
    pending_invites: int
    total_rewards_days: int
    first_level_invites: int
    second_level_invites: int

    class Config:
        from_attributes = True

class InvitationList(BaseModel):
    id: int
    invitee_email: Optional[str]
    status: str
    reward_days: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommissionBalance(BaseModel):
    total_earned: Decimal
    total_withdrawn: Decimal
    balance: Decimal
    pending_balance: Decimal

    class Config:
        from_attributes = True

class CommissionWithdrawRequest(BaseModel):
    amount: Decimal
    withdraw_method: str  # alipay, wechat, bank
    account_info: dict  # 账户信息

class CommissionWithdrawResponse(BaseModel):
    id: int
    amount: Decimal
    withdraw_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CommissionList(BaseModel):
    id: int
    from_user_id: Optional[int]
    level: int
    order_amount: Optional[Decimal]
    commission_rate: Optional[Decimal]
    commission_amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
