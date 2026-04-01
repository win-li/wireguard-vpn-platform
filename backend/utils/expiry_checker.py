from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict
import logging

from config.database import SessionLocal
from models.subscriptions import Subscription
from models.user_nodes import UserNode
from models.users import User

logger = logging.getLogger(__name__)

class SubscriptionExpiryChecker:
    """Check and handle expired subscriptions"""
    
    @staticmethod
    def get_expired_subscriptions(db: Session) -> List[Subscription]:
        """Get expired but still active subscriptions"""
        now = datetime.utcnow()
        expired = db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.expire_at < now
            )
        ).all()
        return expired
    
    @staticmethod
    def get_expiring_soon(db: Session, days: int = 7) -> List[Subscription]:
        """Get subscriptions expiring within specified days"""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        return db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.expire_at >= now,
                Subscription.expire_at <= future
            )
        ).all()
    
    @staticmethod
    def disable_user_connections(db: Session, user_id: int) -> int:
        """Disable all active connections for a user"""
        disabled = db.query(UserNode).filter(
            and_(
                UserNode.user_id == user_id,
                UserNode.is_active == True
            )
        ).update({
            "is_active": False,
            "disconnected_at": datetime.utcnow()
        })
        db.commit()
        return disabled
    
    @staticmethod
    def mark_subscription_expired(db: Session, sub_id: int) -> bool:
        """Mark subscription as expired"""
        sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
        if sub:
            sub.status = "expired"
            sub.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    @staticmethod
    def check_and_process_expired(db: Session) -> Dict:
        """Main method: check and process expired subscriptions"""
        results = {
            "expired_subscriptions": 0,
            "disabled_connections": 0,
            "processed_users": [],
            "errors": []
        }
        
        try:
            expired_subs = SubscriptionExpiryChecker.get_expired_subscriptions(db)
            
            for sub in expired_subs:
                try:
                    SubscriptionExpiryChecker.mark_subscription_expired(db, sub.id)
                    results["expired_subscriptions"] += 1
                    
                    disabled = SubscriptionExpiryChecker.disable_user_connections(db, sub.user_id)
                    results["disabled_connections"] += disabled
                    
                    user = db.query(User).filter(User.id == sub.user_id).first()
                    if user:
                        results["processed_users"].append({
                            "user_id": user.id,
                            "username": user.username,
                            "subscription_id": sub.id,
                            "connections_disabled": disabled
                        })
                        logger.info(f"Expired sub {sub.id} for user {user.username}: disabled {disabled} connections")
                except Exception as e:
                    logger.error(f"Error processing subscription {sub.id}: {e}")
                    results["errors"].append({"subscription_id": sub.id, "error": str(e)})
        except Exception as e:
            logger.error(f"Error in expiry check: {e}")
            results["errors"].append({"error": str(e)})
        
        return results

    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """Get subscription expiry statistics"""
        now = datetime.utcnow()
        
        expired_count = db.query(Subscription).filter(
            Subscription.status == "expired"
        ).count()
        
        active_count = db.query(Subscription).filter(
            Subscription.status == "active"
        ).count()
        
        expiring_7d = db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.expire_at >= now,
                Subscription.expire_at < now + timedelta(days=7)
            )
        ).count()
        
        return {
            "total_active": active_count,
            "total_expired": expired_count,
            "expiring_in_7_days": expiring_7d,
            "checked_at": now.isoformat()
        }


def run_expiry_check():
    """Run expiry check standalone"""
    db = SessionLocal()
    try:
        results = SubscriptionExpiryChecker.check_and_process_expired(db)
        print(f"Expiry check complete:")
        print(f"  Expired: {results[expired_subscriptions]}")
        print(f"  Disabled: {results[disabled_connections]}")
        return results
    finally:
        db.close()


if __name__ == "__main__":
    run_expiry_check()
