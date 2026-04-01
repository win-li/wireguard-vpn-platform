from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict

from config.database import get_db
from utils.expiry_checker import SubscriptionExpiryChecker

router = APIRouter()

@router.post("/check")
def trigger_expiry_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger subscription expiry check (async)"""
    # Run in background
    def run_check():
        from config.database import SessionLocal
        db_local = SessionLocal()
        try:
            SubscriptionExpiryChecker.check_and_process_expired(db_local)
        finally:
            db_local.close()
    
    background_tasks.add_task(run_check)
    return {"status": "check_started"}

@router.get("/run")
def run_expiry_check_sync(db: Session = Depends(get_db)):
    """Run subscription expiry check synchronously"""
    results = SubscriptionExpiryChecker.check_and_process_expired(db)
    return results

@router.get("/statistics")
def get_expiry_statistics(db: Session = Depends(get_db)):
    """Get subscription expiry statistics"""
    stats = SubscriptionExpiryChecker.get_statistics(db)
    return stats

@router.get("/expiring-soon")
def get_expiring_soon(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get subscriptions expiring within specified days"""
    subs = SubscriptionExpiryChecker.get_expiring_soon(db, days)
    return {
        "count": len(subs),
        "subscriptions": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "plan_id": s.plan_id,
                "expire_at": s.expire_at.isoformat(),
                "days_remaining": (s.expire_at.replace(tzinfo=None) - __import__("datetime").datetime.utcnow()).days
            }
            for s in subs
        ]
    }
