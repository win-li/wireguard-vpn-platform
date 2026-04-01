from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models.commissions import Commission, CommissionWithdrawal, UserCommissionBalance
from models.invitations import Invitation
from models.payments import Payment
from models.users import User
from datetime import datetime
from decimal import Decimal
import json

# 佣金比例配置
COMMISSION_RATES = {
    1: Decimal('0.05'),  # 一级佣金 5%
    2: Decimal('0.02'),  # 二级佣金 2%
}

def get_or_create_commission_balance(db: Session, user_id: int) -> UserCommissionBalance:
    """获取或创建用户佣金余额"""
    balance = db.query(UserCommissionBalance).filter(
        UserCommissionBalance.user_id == user_id
    ).first()
    
    if not balance:
        balance = UserCommissionBalance(
            user_id=user_id,
            total_earned=Decimal('0'),
            total_withdrawn=Decimal('0'),
            balance=Decimal('0')
        )
        db.add(balance)
        db.commit()
        db.refresh(balance)
    
    return balance

def calculate_commission(db: Session, payment: Payment):
    """计算订单佣金（订单完成后调用）"""
    # 获取付款用户的邀请人
    payer_id = payment.user_id
    
    # 查找一级邀请人
    first_invitation = db.query(Invitation).filter(
        Invitation.invitee_id == payer_id
    ).first()
    
    if first_invitation:
        # 一级佣金
        first_inviter_id = first_invitation.inviter_id
        first_rate = COMMISSION_RATES[1]
        first_amount = payment.amount * first_rate
        
        commission1 = Commission(
            user_id=first_inviter_id,
            from_user_id=payer_id,
            level=1,
            order_id=payment.id,
            order_amount=payment.amount,
            commission_rate=first_rate,
            commission_amount=first_amount,
            status='settled',
            settled_at=datetime.now()
        )
        db.add(commission1)
        
        # 更新一级邀请人余额
        balance1 = get_or_create_commission_balance(db, first_inviter_id)
        balance1.total_earned += first_amount
        balance1.balance += first_amount
        
        # 查找二级邀请人
        second_invitation = db.query(Invitation).filter(
            Invitation.invitee_id == first_inviter_id
        ).first()
        
        if second_invitation:
            second_inviter_id = second_invitation.inviter_id
            second_rate = COMMISSION_RATES[2]
            second_amount = payment.amount * second_rate
            
            commission2 = Commission(
                user_id=second_inviter_id,
                from_user_id=payer_id,
                level=2,
                order_id=payment.id,
                order_amount=payment.amount,
                commission_rate=second_rate,
                commission_amount=second_amount,
                status='settled',
                settled_at=datetime.now()
            )
            db.add(commission2)
            
            # 更新二级邀请人余额
            balance2 = get_or_create_commission_balance(db, second_inviter_id)
            balance2.total_earned += second_amount
            balance2.balance += second_amount
    
    db.commit()

def get_commission_balance(db: Session, user_id: int):
    """获取用户佣金余额"""
    balance = get_or_create_commission_balance(db, user_id)
    
    # 计算待结算佣金
    pending = db.query(func.sum(Commission.commission_amount)).filter(
        and_(
            Commission.user_id == user_id,
            Commission.status == 'pending'
        )
    ).scalar() or Decimal('0')
    
    return {
        'total_earned': balance.total_earned,
        'total_withdrawn': balance.total_withdrawn,
        'balance': balance.balance,
        'pending_balance': pending
    }

def get_commissions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取用户佣金列表"""
    return db.query(Commission).filter(
        Commission.user_id == user_id
    ).order_by(Commission.created_at.desc()).offset(skip).limit(limit).all()

def create_withdrawal(db: Session, user_id: int, amount: Decimal, 
                     withdraw_method: str, account_info: dict) -> CommissionWithdrawal:
    """创建提现申请"""
    withdrawal = CommissionWithdrawal(
        user_id=user_id,
        amount=amount,
        withdraw_method=withdraw_method,
        account_info=json.dumps(account_info),
        status='pending'
    )
    db.add(withdrawal)
    
    # 冻结余额
    balance = get_or_create_commission_balance(db, user_id)
    balance.balance -= amount
    balance.total_withdrawn += amount
    
    db.commit()
    db.refresh(withdrawal)
    return withdrawal

def get_withdrawals_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取用户提现记录"""
    return db.query(CommissionWithdrawal).filter(
        CommissionWithdrawal.user_id == user_id
    ).order_by(CommissionWithdrawal.created_at.desc()).offset(skip).limit(limit).all()
