from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from utils.nat_traversal import get_nat_info, NATTraversalConfig

router = APIRouter()

@router.get("/info")
def get_nat_information():
    """Get NAT type and configuration"""
    return get_nat_info()

@router.get("/config")
def get_nat_config():
    """Get NAT traversal configuration"""
    return NATTraversalConfig.get_config_dict()

@router.get("/recommended-keepalive")
def get_recommended_keepalive():
    """Get recommended WireGuard keepalive based on NAT type"""
    return {
        "keepalive": NATTraversalConfig.get_wireguard_keepalive(),
        "unit": "seconds"
    }

@router.get("/stun-servers")
def get_stun_servers():
    """Get list of STUN servers"""
    return {
        "servers": NATTraversalConfig.STUN_SERVERS
    }
