from fastapi import APIRouter
from . import (
    user_router, 
    auth_router, 
    node_router, 
    config_router, 
    plan_router, 
    subscription_router, 
    payment_router, 
    admin_router, 
    traffic_router,
    metrics_router,
    device_router,
    qrcode_router,
    expiry_router,
    nat_router,
    invitation_router,
    checkin_router
)

router = APIRouter()

router.include_router(auth_router.router, prefix="/auth", tags=["authentication"])
router.include_router(user_router.router, prefix="/users", tags=["users"])
router.include_router(node_router.router, prefix="/nodes", tags=["nodes"])
router.include_router(config_router.router, prefix="/configs", tags=["configs"])
router.include_router(plan_router.router, tags=["plans"])
router.include_router(subscription_router.router, tags=["subscriptions"])
router.include_router(payment_router.router, tags=["payments"])
router.include_router(admin_router.router, prefix="/admin", tags=["admin"])
router.include_router(traffic_router.router, prefix="/traffic", tags=["traffic"])

# New feature routers
router.include_router(metrics_router.router, prefix="/metrics", tags=["metrics"])
router.include_router(device_router.router, prefix="/devices", tags=["devices"])
router.include_router(qrcode_router.router, prefix="/qrcode", tags=["qrcode"])
router.include_router(expiry_router.router, prefix="/expiry", tags=["expiry"])
router.include_router(nat_router.router, prefix="/nat", tags=["nat"])

# Gamification features
router.include_router(invitation_router.router, prefix="/invitations", tags=["invitations"])
router.include_router(checkin_router.router, prefix="/checkin", tags=["checkin"])
