from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel

from config.database import get_db
from models.device_posture import DevicePosture, DeviceAlert
from utils.device_checker import DevicePostureChecker

router = APIRouter()

class DeviceRegisterRequest(BaseModel):
    device_id: str
    device_name: str = None
    device_type: str = None  # windows, macos, linux, ios, android
    client_version: str = None
    client_type: str = "official"
    os_name: str = None
    os_version: str = None
    local_ip: str = None
    public_ip: str = None
    mac_address: str = None
    is_jailbroken: bool = False
    has_firewall: bool = None
    has_antivirus: bool = None
    disk_encrypted: bool = None
    user_agent: str = None
    extra_data: dict = None
    user_node_id: int = None

class DeviceCheckResponse(BaseModel):
    device_id: str
    passed: bool
    warnings: List[str]
    alerts: List[Dict]

@router.post("/register")
def register_device(
    user_id: int,
    device_info: DeviceRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register or update a device"""
    device = DevicePostureChecker.register_device(
        db,
        user_id=user_id,
        device_info=device_info.dict(),
        user_node_id=device_info.user_node_id
    )
    
    return {
        "status": "success",
        "device_id": device.device_id,
        "is_trusted": device.is_trusted,
        "is_blocked": device.is_blocked,
    }

@router.post("/check")
def check_device(device_id: str, db: Session = Depends(get_db)):
    """Perform posture check on device"""
    results = DevicePostureChecker.perform_posture_check(db, device_id)
    return results

@router.get("/user/{user_id}")
def get_user_devices(user_id: int, db: Session = Depends(get_db)):
    """Get all devices for a user"""
    devices = DevicePostureChecker.get_user_devices(db, user_id)
    return {
        "devices": [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "device_type": d.device_type,
                "client_version": d.client_version,
                "is_trusted": d.is_trusted,
                "is_blocked": d.is_blocked,
                "last_seen": d.last_seen_at.isoformat() if d.last_seen_at else None,
            }
            for d in devices
        ]
    }

@router.post("/block")
def block_device(device_id: str, reason: str, db: Session = Depends(get_db)):
    """Block a device"""
    success = DevicePostureChecker.block_device(db, device_id, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "blocked", "device_id": device_id}

@router.post("/trust")
def trust_device(device_id: str, db: Session = Depends(get_db)):
    """Mark device as trusted"""
    success = DevicePostureChecker.trust_device(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "trusted", "device_id": device_id}

@router.get("/alerts")
def get_alerts(user_id: int = None, db: Session = Depends(get_db)):
    """Get active device alerts"""
    alerts = DevicePostureChecker.get_active_alerts(db, user_id)
    return {
        "alerts": [
            {
                "id": a.id,
                "device_id": a.device_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ]
    }
