import socket
import asyncio
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NATType(Enum):
    """NAT type classification"""
    UNKNOWN = "unknown"
    FULL_CONE = "full_cone"  # Easy NAT - no restrictions
    RESTRICTED_CONE = "restricted_cone"  # Moderate NAT
    PORT_RESTRICTED = "port_restricted"  # Strict NAT
    SYMMETRIC = "symmetric"  # Hardest NAT for P2P

@dataclass
class NATInfo:
    """NAT information"""
    nat_type: NATType
    public_ip: str
    public_port: int
    local_ip: str
    local_port: int
    is_cone_nat: bool
    supports_hairpin: Optional[bool] = None

class STUNClient:
    """Basic STUN client for NAT detection"""
    
    # Public STUN servers
    STUN_SERVERS = [
        ("stun.l.google.com", 19302),
        ("stun1.l.google.com", 19302),
        ("stun2.l.google.com", 19302),
        ("stun.stunprotocol.org", 3478),
    ]
    
    @staticmethod
    async def get_public_address(stun_server: Tuple[str, int] = None) -> Tuple[str, int]:
        """
        Get public IP and port using STUN
        Returns (public_ip, public_port)
        """
        if stun_server is None:
            stun_server = STUNClient.STUN_SERVERS[0]
        
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Basic STUN binding request
            # This is a simplified version - real STUN requires proper encoding
            stun_host, stun_port = stun_server
            
            # Get local address
            sock.connect((stun_host, stun_port))
            local_ip, local_port = sock.getsockname()
            
            # For now, return local address as fallback
            # In production, implement full STUN protocol
            sock.close()
            
            return local_ip, local_port
            
        except Exception as e:
            logger.error(f"STUN request failed: {e}")
            raise
    
    @staticmethod
    def detect_nat_type() -> NATInfo:
        """
        Detect NAT type using STUN
        Returns NATInfo with detected type
        """
        try:
            # Get local IP
            local_ip = socket.gethostbyname(socket.gethostname())
            local_port = 0
            
            # Get public address
            public_ip, public_port = asyncio.run(
                STUNClient.get_public_address()
            )
            
            # Determine NAT type (simplified)
            if public_ip == local_ip:
                nat_type = NATType.FULL_CONE  # No NAT
            else:
                # Default to symmetric NAT (most restrictive)
                nat_type = NATType.SYMMETRIC
            
            return NATInfo(
                nat_type=nat_type,
                public_ip=public_ip,
                public_port=public_port,
                local_ip=local_ip,
                local_port=local_port,
                is_cone_nat=nat_type in [NATType.FULL_CONE, NATType.RESTRICTED_CONE]
            )
            
        except Exception as e:
            logger.error(f"NAT detection failed: {e}")
            return NATInfo(
                nat_type=NATType.UNKNOWN,
                public_ip="0.0.0.0",
                public_port=0,
                local_ip="0.0.0.0",
                local_port=0,
                is_cone_nat=False
            )

class UDPHolePuncher:
    """UDP hole punching helper for NAT traversal"""
    
    def __init__(self, local_port: int = 0):
        self.local_port = local_port
        self.sock = None
    
    async def create_hole(self, remote_ip: str, remote_port: int) -> bool:
        """
        Create UDP hole to remote endpoint
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("0.0.0.0", self.local_port))
            self.sock.setblocking(False)
            
            # Send keepalive packets
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.sock, b"PUNCH", (remote_ip, remote_port))
            
            logger.info(f"UDP hole created to {remote_ip}:{remote_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create UDP hole: {e}")
            return False
    
    async def listen_for_peer(self, timeout: int = 30) -> Optional[Tuple[str, int]]:
        """Listen for peer connection"""
        try:
            loop = asyncio.get_event_loop()
            self.sock.settimeout(timeout)
            
            data, addr = await loop.sock_recvfrom(self.sock, 1024)
            logger.info(f"Received from peer {addr}: {data}")
            return addr
            
        except socket.timeout:
            logger.warning("Timeout waiting for peer")
            return None
        except Exception as e:
            logger.error(f"Error listening for peer: {e}")
            return None
    
    def close(self):
        """Close socket"""
        if self.sock:
            self.sock.close()

class NATTraversalConfig:
    """NAT traversal configuration for VPN"""
    
    # STUN servers configuration
    STUN_SERVERS = [
        "stun.l.google.com:19302",
        "stun1.l.google.com:19302",
        "stun.stunprotocol.org:3478",
    ]
    
    # TURN servers for relay (when P2P fails)
    TURN_SERVERS = []  # Add your TURN servers here
    
    # Keepalive settings
    KEEPALIVE_INTERVAL = 25  # seconds
    KEEPALIVE_PACKET = b"KEEPALIVE"
    
    @staticmethod
    def get_wireguard_keepalive() -> int:
        """Get recommended WireGuard keepalive based on NAT type"""
        nat_info = STUNClient.detect_nat_type()
        
        if nat_info.nat_type == NATType.SYMMETRIC:
            return 15  # More frequent for symmetric NAT
        elif nat_info.nat_type == NATType.PORT_RESTRICTED:
            return 20
        else:
            return 25  # Standard for cone NAT
    
    @staticmethod
    def get_config_dict() -> Dict:
        """Get NAT traversal config as dictionary"""
        return {
            "stun_servers": NATTraversalConfig.STUN_SERVERS,
            "turn_servers": NATTraversalConfig.TURN_SERVERS,
            "keepalive_interval": NATTraversalConfig.KEEPALIVE_INTERVAL,
            "recommended_keepalive": NATTraversalConfig.get_wireguard_keepalive(),
        }

def get_nat_info() -> Dict:
    """Get NAT information for API response"""
    nat_info = STUNClient.detect_nat_type()
    return {
        "nat_type": nat_info.nat_type.value,
        "public_ip": nat_info.public_ip,
        "public_port": nat_info.public_port,
        "local_ip": nat_info.local_ip,
        "is_cone_nat": nat_info.is_cone_nat,
        "recommended_keepalive": NATTraversalConfig.get_wireguard_keepalive(),
        "stun_servers": NATTraversalConfig.STUN_SERVERS,
    }
