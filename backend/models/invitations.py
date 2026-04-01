from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Boolean, Text
from sqlalchemy.sql import func
from config.database import Base

class Invitation(Base):
    """邀请记录表"""
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    invitee_id = Column(Integer, ForeignKey("users.id"), index=True)
    invite_code = Column(String(20), nullable=False, index=True)
    invitee_email = Column(String(255))
    status = Column(String(20), default="pending")
    reward_days = Column(Integer, default=0)
    reward_granted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserInviteCode(Base):
    """用户邀请码表"""
    __tablename__ = "user_invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    invite_code = Column(String(20), unique=True, nullable=False, index=True)
    total_invites = Column(Integer, default=0)
    successful_invites = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
