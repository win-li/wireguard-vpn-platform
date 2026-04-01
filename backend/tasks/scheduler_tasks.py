import logging
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.celery_app import celery_app
from config.database import SessionLocal
from utils.expiry_checker import SubscriptionExpiryChecker
from models.device_posture import DeviceAlert

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.scheduler_tasks.check_expired_subscriptions")
def check_expired_subscriptions():
    """
    Periodic task: Check for expired subscriptions and disable connections
    Runs every hour
    """
    logger.info("Starting expired subscription check...")
    db = SessionLocal()
    try:
        results = SubscriptionExpiryChecker.check_and_process_expired(db)
        logger.info(f"Expired subscription check complete: {results}")
        return results
    except Exception as e:
        logger.error(f"Error in expired subscription check: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="tasks.scheduler_tasks.notify_expiring_soon")
def notify_expiring_soon():
    """
    Periodic task: Notify users about subscriptions expiring soon
    Runs every 6 hours
    """
    logger.info("Checking for expiring soon subscriptions...")
    db = SessionLocal()
    try:
        expiring = SubscriptionExpiryChecker.get_expiring_soon(db, days=7)
        
        notifications = []
        for sub in expiring:
            days_left = (sub.expire_at.replace(tzinfo=None) - datetime.utcnow()).days
            # Here you would send notification (email, push, etc.)
            notification = {
                "user_id": sub.user_id,
                "subscription_id": sub.id,
                "days_left": days_left,
                "expire_at": sub.expire_at.isoformat()
            }
            notifications.append(notification)
            logger.info(f"User {sub.user_id} subscription expires in {days_left} days")
        
        return {"notifications": notifications, "count": len(notifications)}
    except Exception as e:
        logger.error(f"Error checking expiring subscriptions: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="tasks.scheduler_tasks.cleanup_old_alerts")
def cleanup_old_alerts(days_old: int = 30):
    """
    Periodic task: Clean up old resolved device alerts
    Runs daily
    """
    logger.info("Cleaning up old device alerts...")
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted = db.query(DeviceAlert).filter(
            DeviceAlert.is_resolved == True,
            DeviceAlert.resolved_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Deleted {deleted} old resolved alerts")
        return {"deleted": deleted}
    except Exception as e:
        logger.error(f"Error cleaning up alerts: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="tasks.scheduler_tasks.send_expiry_reminder")
def send_expiry_reminder(user_id: int, subscription_id: int, days_left: int):
    """
    Send expiry reminder to specific user
    Can be called individually
    """
    logger.info(f"Sending expiry reminder to user {user_id}: {days_left} days left")
    # Implement your notification logic here (email, push notification, etc.)
    return {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "days_left": days_left,
        "sent": True
    }

@celery_app.task(name="tasks.scheduler_tasks.update_traffic_statistics")
def update_traffic_statistics():
    """
    Update daily traffic statistics
    """
    logger.info("Updating traffic statistics...")
    # Implement traffic aggregation logic
    return {"updated": True}
