from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models.invitations import Invitation, UserInviteCode
from models.commissions import Commission, UserCommissionBalance
from models.users import User
from models.subscriptions import Subscription
from datetime import datetime
import random
import string
from decimal import Decimal

def generate_invite_code(length=8):
    """生成随机邀请码"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_or_create_user_invite_code(db: Session, user_id: int) -> UserInviteCode:
    """获取或创建用户邀请码"""
    invite_code = db.query(UserInviteCode).filter(UserInviteCode.user_id == user_id).first()
    if not invite_code:
        # 生成唯一邀请码
        code = generate_invite_code()
        while db.query(UserInviteCode).filter(UserInviteCode.invite_code == code).first():
            code = generate_invite_code()
        
        invite_code = UserInviteCode(
            user_id=user_id,
            invite_code=code,
            total_invites=0,
            successful_invites=0
        )
        db.add(invite_code)
        db.commit()
        db.refresh(invite_code)
    return invite_code

def create_invitation(db: Session, inviter_id: int, invite_code: str, invitee_email: str) -> Invitation:
    """创建邀请记录"""
    invitation = Invitation(
        inviter_id=inviter_id,
        invite_code=invite_code,
        invitee_email=invitee_email,
        status='pending'
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # 更新邀请统计
    user_code = db.query(UserInviteCode).filter(UserInviteCode.invite_code == invite_code).first()
    if user_code:
        user_code.total_invites += 1
        db.commit()
    
    return invitation

def complete_invitation(db: Session, invitee_id: int, invitee_email: str) -> Invitation:
    """完成邀请注册"""
    # 查找待完成的邀请记录
    invitation = db.query(Invitation).filter(
        and_(
            Invitation.invitee_email == invitee_email,
            Invitation.status == 'pending'
        )
    ).first()
    
    if invitation:
        invitation.invitee_id = invitee_id
        invitation.status = 'registered'
        db.commit()
        db.refresh(invitation)
        
        # 更新邀请统计
        user_code = db.query(UserInviteCode).filter(
            UserInviteCode.invite_code == invitation.invite_code
        ).first()
        if user_code:
            user_code.successful_invites += 1
            db.commit()
    
    return invitation

def grant_invite_reward(db: Session, invitation_id: int, reward_days: int = 3) -> Invitation:
    """发放邀请奖励"""
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if invitation and invitation.status == 'registered':
        invitation.status = 'rewarded'
        invitation.reward_days = reward_days
        invitation.reward_granted_at = datetime.now()
        db.commit()
        db.refresh(invitation)
    return invitation

def get_invitation_stats(db: Session, user_id: int):
    """获取用户邀请统计"""
    user_code = get_or_create_user_invite_code(db, user_id)
    
    # 获取邀请列表
    invitations = db.query(Invitation).filter(Invitation.inviter_id == user_id).all()
    
    # 统计各级邀请
    first_level_ids = [inv.invitee_id for inv in invitations if inv.invitee_id]
    second_level_count = 0
    
    if first_level_ids:
        # 查找二级邀请（被邀请人邀请的人）
        second_level = db.query(Invitation).filter(
            Invitation.inviter_id.in_(first_level_ids)
        ).count()
        second_level_count = second_level
    
    return {
        'total_invites': user_code.total_invites,
        'successful_invites': user_code.successful_invites,
        'pending_invites': user_code.total_invites - user_code.successful_invites,
        'total_rewards_days': sum(inv.reward_days for inv in invitations if inv.status == 'rewarded'),
        'first_level_invites': len(first_level_ids),
        'second_level_invites': second_level_count
    }

def get_invitations_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """获取用户邀请列表"""
    return db.query(Invitation).filter(
        Invitation.inviter_id == user_id
    ).order_by(Invitation.created_at.desc()).offset(skip).limit(limit).all()
