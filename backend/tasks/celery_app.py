from celery import Celery
from celery.schedules import crontab
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "vpn_system",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks.scheduler_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Check expired subscriptions every hour
    "check-expired-subscriptions-hourly": {
        "task": "tasks.scheduler_tasks.check_expired_subscriptions",
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    # Check expiring soon subscriptions every 6 hours
    "check-expiring-soon-subscriptions": {
        "task": "tasks.scheduler_tasks.notify_expiring_soon",
        "schedule": crontab(minute="*/360"),  # Every 6 hours
    },
    # Clean up old device alerts daily
    "cleanup-old-alerts": {
        "task": "tasks.scheduler_tasks.cleanup_old_alerts",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM UTC
    },
}
