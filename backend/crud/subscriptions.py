from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from models.subscriptions import Subscription
from models.plans import Plan
from schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate

def get_subscription_by_id(db: Session, sub_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.id == sub_id).first()

def get_user_subscriptions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Subscription]:
    return db.query(Subscription).filter(Subscription.user_id == user_id).offset(skip).limit(limit).all()

def get_user_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
        Subscription.expire_at > datetime.now()
    ).first()

def get_subscriptions(db: Session, skip: int = 0, limit: int = 100, status: str = None) -> List[Subscription]:
    query = db.query(Subscription)
    if status:
        query = query.filter(Subscription.status == status)
    return query.offset(skip).limit(limit).all()

def create_subscription(db: Session, sub: SubscriptionCreate, plan: Plan) -> Subscription:
    now = datetime.now()
    expire_at = now + timedelta(days=plan.duration_days)
    
    db_sub = Subscription(
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        status="active",
        start_at=now,
        expire_at=expire_at,
        bandwidth_limit=plan.bandwidth_limit,
        auto_renew=sub.auto_renew
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def update_subscription(db: Session, sub_id: int, sub_update: SubscriptionUpdate) -> Optional[Subscription]:
    db_sub = get_subscription_by_id(db, sub_id)
    if not db_sub:
        return None
    update_data = sub_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sub, key, value)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def cancel_subscription(db: Session, sub_id: int) -> Optional[Subscription]:
    db_sub = get_subscription_by_id(db, sub_id)
    if not db_sub:
        return None
    db_sub.status = "cancelled"
    db_sub.auto_renew = False
    db.commit()
    db.refresh(db_sub)
    return db_sub

def update_bandwidth_usage(db: Session, sub_id: int, bytes_used: int) -> Optional[Subscription]:
    db_sub = get_subscription_by_id(db, sub_id)
    if not db_sub:
        return None
    db_sub.bandwidth_used += bytes_used
    db.commit()
    db.refresh(db_sub)
    return db_sub

def check_expired_subscriptions(db: Session) -> List[Subscription]:
    expired = db.query(Subscription).filter(
        Subscription.status == "active",
        Subscription.expire_at < datetime.now()
    ).all()
    for sub in expired:
        sub.status = "expired"
    db.commit()
    return expired
