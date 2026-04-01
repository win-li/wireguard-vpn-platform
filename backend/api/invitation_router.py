from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from api.deps import get_current_user
from models.users import User
from schemas.invitations import (
    InviteCodeResponse,
    InvitationRegister,
    InvitationStats,
    InvitationList,
    CommissionBalance,
    CommissionWithdrawRequest,
    CommissionWithdrawResponse,
    CommissionList
)
from crud.invitations import (
    get_or_create_user_invite_code,
    create_invitation,
    complete_invitation,
    get_invitation_stats,
    get_invitations_by_user
)
from crud.commissions import (
    get_commission_balance,
    get_commissions_by_user,
    create_withdrawal,
    get_withdrawals_by_user
)
from crud.users import create_user
from schemas.users import UserCreate
from decimal import Decimal

router = APIRouter()

@router.post("/generate-code", response_model=InviteCodeResponse)
def generate_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成用户专属邀请码"""
    invite_code = get_or_create_user_invite_code(db, current_user.id)
    
    # 生成分享链接
    base_url = "https://vpn.example.com"  # TODO: 从配置读取
    share_url = f"{base_url}/register?code={invite_code.invite_code}"
    
    return InviteCodeResponse(
        invite_code=invite_code.invite_code,
        total_invites=invite_code.total_invites,
        successful_invites=invite_code.successful_invites,
        share_url=share_url
    )

@router.get("/my-stats", response_model=InvitationStats)
def get_my_invitation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的邀请统计"""
    stats = get_invitation_stats(db, current_user.id)
    return InvitationStats(**stats)

@router.get("/my-invitations", response_model=List[InvitationList])
def get_my_invitations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的邀请列表"""
    invitations = get_invitations_by_user(db, current_user.id, skip, limit)
    return [InvitationList.from_orm(inv) for inv in invitations]

# ============ 佣金相关 ============

@router.get("/commissions/balance", response_model=CommissionBalance)
def get_my_commission_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的佣金余额"""
    balance = get_commission_balance(db, current_user.id)
    return CommissionBalance(**balance)

@router.get("/commissions/list", response_model=List[CommissionList])
def get_my_commissions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的佣金记录"""
    commissions = get_commissions_by_user(db, current_user.id, skip, limit)
    return [CommissionList.from_orm(com) for com in commissions]

@router.post("/commissions/withdraw", response_model=CommissionWithdrawResponse)
def request_withdrawal(
    request: CommissionWithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请佣金提现"""
    # 检查余额
    balance = get_commission_balance(db, current_user.id)
    if balance["balance"] < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足"
        )
    
    # 最低提现金额
    if request.amount < Decimal('10'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="最低提现金额为10元"
        )
    
    withdrawal = create_withdrawal(
        db, current_user.id, request.amount, 
        request.withdraw_method, request.account_info
    )
    
    return CommissionWithdrawResponse.from_orm(withdrawal)

@router.get("/commissions/withdrawals")
def get_my_withdrawals(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的提现记录"""
    withdrawals = get_withdrawals_by_user(db, current_user.id, skip, limit)
    return withdrawals
