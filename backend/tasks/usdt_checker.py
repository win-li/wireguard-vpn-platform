"""
USDT支付检查定时任务
定时检查待支付的USDT订单，确认到账后自动激活订阅
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from celery import shared_task
from celery_app import app
from config.database import SessionLocal
from models.payments import Payment
from models.subscriptions import Subscription
from sqlalchemy import and_
from utils.usdt_payment import USDTPayment, check_all_pending_payments

logger = logging.getLogger(__name__)


@shared_task(name="check_usdt_payments")
def check_usdt_payments_task():
    """
    定时任务：检查USDT支付状态
    建议每1-2分钟执行一次
    """
    logger.info("Starting USDT payment check task")
    
    try:
        # 运行异步检查
        result = asyncio.run(check_all_pending_payments())
        logger.info(f"USDT payment check completed: {result}")
        
        # 激活已确认的订阅
        activated = asyncio.run(activate_confirmed_subscriptions())
        logger.info(f"Activated {activated} subscriptions")
        
        return {
            "payments_checked": result.get("checked", 0),
            "payments_confirmed": result.get("confirmed", 0),
            "subscriptions_activated": activated
        }
    except Exception as e:
        logger.error(f"USDT payment check failed: {e}")
        return {"error": str(e)}


async def activate_confirmed_subscriptions() -> int:
    """激活已支付成功但未激活的订阅"""
    db = SessionLocal()
    try:
        # 查找支付成功但订阅未激活的记录
        payments = db.query(Payment).filter(
            and_(
                Payment.status == "success",
                Payment.paid_at != None
            )
        ).all()
        
        activated_count = 0
        for payment in payments:
            sub = db.query(Subscription).filter(
                Subscription.id == payment.subscription_id
            ).first()
            
            if sub and not sub.is_active:
                sub.is_active = True
                sub.activated_at = datetime.now()
                activated_count += 1
                logger.info(f"Activated subscription {sub.id} for user {sub.user_id}")
        
        db.commit()
        return activated_count
        
    except Exception as e:
        logger.error(f"Failed to activate subscriptions: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


@shared_task(name="cleanup_expired_usdt_payments")
def cleanup_expired_usdt_payments():
    """
    定时任务：清理过期的USDT支付订单
    建议每小时执行一次
    """
    db = SessionLocal()
    try:
        from utils.usdt_payment import USDTPayment as USDTConfig
        
        # 查找过期但状态仍为pending的订单
        expired_payments = db.query(Payment).filter(
            and_(
                Payment.status == "pending",
                Payment.payment_method.in_(["usdt_trc20", "usdt_erc20"]),
                Payment.expires_at < datetime.now()
            )
        ).all()
        
        for payment in expired_payments:
            payment.status = "expired"
            logger.info(f"Marked payment {payment.id} as expired")
        
        db.commit()
        
        return {"expired_count": len(expired_payments)}
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired payments: {e}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


# 配置Celery Beat定时任务
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # 每2分钟检查一次USDT支付
    sender.add_periodic_task(120.0, check_usdt_payments_task.s(), name="check-usdt-payments")
    
    # 每小时清理过期订单
    sender.add_periodic_task(3600.0, cleanup_expired_usdt_payments.s(), name="cleanup-expired-usdt")
