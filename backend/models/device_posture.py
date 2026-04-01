from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from config.database import Base

class DevicePosture(Base):
    """Device posture information for security checks"""
    __tablename__ = "device_postures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_node_id = Column(Integer, ForeignKey("user_nodes.id"))
    
    # Device identification
    device_id = Column(String(255), unique=True, index=True)  # Unique device identifier
    device_name = Column(String(255))  # User-friendly device name
    device_type = Column(String(50))  # windows, macos, linux, ios, android
    
    # Client information
    client_version = Column(String(50))  # WireGuard client version
    client_type = Column(String(50))  # official, third-party
    
    # OS information
    os_name = Column(String(50))
    os_version = Column(String(50))
    
    # Network information
    local_ip = Column(String(50))
    public_ip = Column(String(50))
    mac_address = Column(String(17))  # If available
    
    # Security posture
    is_jailbroken = Column(Boolean, default=False)  # iOS/Android jailbreak detection
    has_firewall = Column(Boolean)
    has_antivirus = Column(Boolean)
    disk_encrypted = Column(Boolean)
    
    # Additional metadata
    user_agent = Column(Text)
    extra_data = Column(JSON)  # Additional device info
    
    # Status
    is_trusted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String(255))
    
    # Timestamps
    first_seen_at = Column(DateTime, default=func.now())
    last_seen_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_check_at = Column(DateTime)  # Last posture check
    
class DeviceAlert(Base):
    """Device security alerts"""
    __tablename__ = "device_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("device_postures.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Alert details
    alert_type = Column(String(50))  # outdated_client, jailbreak, suspicious_ip, etc.
    severity = Column(String(20))  # low, medium, high, critical
    message = Column(Text)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
