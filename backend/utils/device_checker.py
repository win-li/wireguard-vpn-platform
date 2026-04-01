from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, List, Optional
import logging
import re

from models.device_posture import DevicePosture, DeviceAlert
from models.users import User

logger = logging.getLogger(__name__)

# Minimum supported client versions
MIN_CLIENT_VERSIONS = {
    "windows": "1.0.0",
    "macos": "1.0.0",
    "linux": "1.0.0",
    "ios": "1.0.0",
    "android": "1.0.0",
}

# Suspicious IP ranges (example)
SUSPICIOUS_IP_RANGES = [
    "10.0.0.0/8",  # Could be internal, but suspicious from public
]

class DevicePostureChecker:
    """Device posture checking and management"""
    
    @staticmethod
    def compare_versions(v1: str, v2: str) -> int:
        """Compare semantic versions. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2"""
        def parse_version(v):
            return [int(x) for x in re.findall(r"\d+", v)]
        
        parts1 = parse_version(v1)
        parts2 = parse_version(v2)
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0
            if p1 < p2:
                return -1
            if p1 > p2:
                return 1
        return 0
    
    @staticmethod
    def register_device(
        db: Session,
        user_id: int,
        device_info: Dict,
        user_node_id: int = None
    ) -> DevicePosture:
        """Register or update a device"""
        device_id = device_info.get("device_id")
        
        # Check if device exists
        device = db.query(DevicePosture).filter(
            DevicePosture.device_id == device_id
        ).first()
        
        if device:
            # Update existing device
            device.last_seen_at = datetime.utcnow()
            device.public_ip = device_info.get("public_ip", device.public_ip)
            device.local_ip = device_info.get("local_ip", device.local_ip)
            device.client_version = device_info.get("client_version", device.client_version)
            device.os_version = device_info.get("os_version", device.os_version)
            device.last_check_at = datetime.utcnow()
        else:
            # Create new device
            device = DevicePosture(
                user_id=user_id,
                user_node_id=user_node_id,
                device_id=device_id,
                device_name=device_info.get("device_name"),
                device_type=device_info.get("device_type"),
                client_version=device_info.get("client_version"),
                client_type=device_info.get("client_type", "official"),
                os_name=device_info.get("os_name"),
                os_version=device_info.get("os_version"),
                local_ip=device_info.get("local_ip"),
                public_ip=device_info.get("public_ip"),
                mac_address=device_info.get("mac_address"),
                is_jailbroken=device_info.get("is_jailbroken", False),
                has_firewall=device_info.get("has_firewall"),
                has_antivirus=device_info.get("has_antivirus"),
                disk_encrypted=device_info.get("disk_encrypted"),
                user_agent=device_info.get("user_agent"),
                extra_data=device_info.get("extra_data"),
                last_check_at=datetime.utcnow(),
            )
            db.add(device)
        
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def check_client_version(db: Session, device: DevicePosture) -> Optional[Dict]:
        """Check if client version is supported"""
        device_type = device.device_type
        client_version = device.client_version
        
        if not device_type or not client_version:
            return None
        
        min_version = MIN_CLIENT_VERSIONS.get(device_type.lower())
        if not min_version:
            return None
        
        comparison = DevicePostureChecker.compare_versions(client_version, min_version)
        
        if comparison < 0:
            return {
                "is_outdated": True,
                "current_version": client_version,
                "min_version": min_version,
                "message": f"Client version {client_version} is outdated. Minimum: {min_version}",
            }
        
        return {"is_outdated": False, "current_version": client_version}
    
    @staticmethod
    def create_alert(
        db: Session,
        device_id: int,
        user_id: int,
        alert_type: str,
        severity: str,
        message: str
    ) -> DeviceAlert:
        """Create a device security alert"""
        alert = DeviceAlert(
            device_id=device_id,
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.warning(f"Device alert created: {alert_type} - {message}")
        return alert
    
    @staticmethod
    def perform_posture_check(db: Session, device_id: str) -> Dict:
        """
        Perform full posture check on a device
        Returns check results and any alerts
        """
        device = db.query(DevicePosture).filter(
            DevicePosture.device_id == device_id
        ).first()
        
        if not device:
            return {"error": "Device not found", "passed": False}
        
        results = {
            "device_id": device_id,
            "passed": True,
            "warnings": [],
            "alerts": [],
        }
        
        # Check 1: Client version
        version_check = DevicePostureChecker.check_client_version(db, device)
        if version_check and version_check.get("is_outdated"):
            results["warnings"].append(version_check["message"])
            results["passed"] = False
            
            DevicePostureChecker.create_alert(
                db, device.id, device.user_id,
                "outdated_client", "medium",
                version_check["message"]
            )
        
        # Check 2: Jailbreak detection
        if device.is_jailbroken:
            results["warnings"].append("Device appears to be jailbroken")
            results["passed"] = False
            
            DevicePostureChecker.create_alert(
                db, device.id, device.user_id,
                "jailbroken_device", "high",
                "Device is jailbroken - security risk"
            )
        
        # Check 3: Disk encryption
        if device.disk_encrypted is False:
            results["warnings"].append("Disk encryption not enabled")
            # Not a hard fail, but warning
        
        # Check 4: Device blocked
        if device.is_blocked:
            results["passed"] = False
            results["warnings"].append(f"Device is blocked: {device.block_reason}")
        
        # Update last check time
        device.last_check_at = datetime.utcnow()
        db.commit()
        
        return results
    
    @staticmethod
    def block_device(db: Session, device_id: str, reason: str) -> bool:
        """Block a device"""
        device = db.query(DevicePosture).filter(
            DevicePosture.device_id == device_id
        ).first()
        
        if device:
            device.is_blocked = True
            device.block_reason = reason
            db.commit()
            
            DevicePostureChecker.create_alert(
                db, device.id, device.user_id,
                "device_blocked", "critical",
                f"Device blocked: {reason}"
            )
            return True
        return False
    
    @staticmethod
    def trust_device(db: Session, device_id: str) -> bool:
        """Mark a device as trusted"""
        device = db.query(DevicePosture).filter(
            DevicePosture.device_id == device_id
        ).first()
        
        if device:
            device.is_trusted = True
            device.is_blocked = False
            device.block_reason = None
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_user_devices(db: Session, user_id: int) -> List[DevicePosture]:
        """Get all devices for a user"""
        return db.query(DevicePosture).filter(
            DevicePosture.user_id == user_id
        ).all()
    
    @staticmethod
    def get_active_alerts(db: Session, user_id: int = None) -> List[DeviceAlert]:
        """Get unresolved alerts"""
        query = db.query(DeviceAlert).filter(DeviceAlert.is_resolved == False)
        if user_id:
            query = query.filter(DeviceAlert.user_id == user_id)
        return query.all()
