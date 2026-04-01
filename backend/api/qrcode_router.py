from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from config.database import get_db
from models.user_nodes import UserNode
from models.nodes import Node
from utils.qrcode_gen import QRCodeGenerator

router = APIRouter()

class QRCodeRequest(BaseModel):
    private_key: str
    address: str
    peer_public_key: str
    peer_endpoint: str
    dns: str = "1.1.1.1"
    allowed_ips: str = "0.0.0.0/0"
    keepalive: int = 25

class QRCodeConfigResponse(BaseModel):
    config: str
    qr_code_base64: str

@router.post("/generate")
def generate_qrcode(config: QRCodeRequest):
    """Generate QR code from WireGuard configuration"""
    qr_base64 = QRCodeGenerator.generate_wireguard_qr_base64(
        private_key=config.private_key,
        address=config.address,
        peer_public_key=config.peer_public_key,
        peer_endpoint=config.peer_endpoint,
        dns=config.dns,
        allowed_ips=config.allowed_ips,
        keepalive=config.keepalive
    )
    
    wg_config = QRCodeGenerator.generate_wireguard_config(
        private_key=config.private_key,
        address=config.address,
        peer_public_key=config.peer_public_key,
        peer_endpoint=config.peer_endpoint,
        dns=config.dns,
        allowed_ips=config.allowed_ips,
        keepalive=config.keepalive
    )
    
    return {
        "config": wg_config,
        "qr_code_base64": qr_base64
    }

@router.post("/generate/png")
def generate_qrcode_png(config: QRCodeRequest):
    """Generate QR code as PNG image"""
    img_buffer = QRCodeGenerator.generate_wireguard_qr_png(
        private_key=config.private_key,
        address=config.address,
        peer_public_key=config.peer_public_key,
        peer_endpoint=config.peer_endpoint,
        dns=config.dns,
        allowed_ips=config.allowed_ips,
        keepalive=config.keepalive
    )
    
    return StreamingResponse(
        io.BytesIO(img_buffer.getvalue()),
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=wireguard-qr.png"}
    )

@router.get("/user-node/{user_node_id}")
def get_user_node_qrcode(
    user_node_id: int,
    db: Session = Depends(get_db)
):
    """Get QR code for a specific user node configuration"""
    user_node = db.query(UserNode).filter(UserNode.id == user_node_id).first()
    
    if not user_node:
        raise HTTPException(status_code=404, detail="User node not found")
    
    # Get node information
    node = db.query(Node).filter(Node.id == user_node.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Generate QR code
    # Note: You need to have the public key stored or retrieve it
    peer_public_key = node.public_key if hasattr(node, "public_key") else "PLACEHOLDER_PUBLIC_KEY"
    peer_endpoint = f"{node.ip_address}:{node.port}" if hasattr(node, "port") else f"{node.ip_address}:51820"
    
    qr_base64 = QRCodeGenerator.generate_wireguard_qr_base64(
        private_key=user_node.private_key,
        address=user_node.allowed_ips,
        peer_public_key=peer_public_key,
        peer_endpoint=peer_endpoint
    )
    
    return {
        "user_node_id": user_node_id,
        "qr_code_base64": qr_base64
    }

@router.get("/config/{user_node_id}")
def get_wireguard_config(
    user_node_id: int,
    db: Session = Depends(get_db)
):
    """Get WireGuard configuration text for a user node"""
    user_node = db.query(UserNode).filter(UserNode.id == user_node_id).first()
    
    if not user_node:
        raise HTTPException(status_code=404, detail="User node not found")
    
    node = db.query(Node).filter(Node.id == user_node.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    peer_public_key = node.public_key if hasattr(node, "public_key") else "PLACEHOLDER_PUBLIC_KEY"
    peer_endpoint = f"{node.ip_address}:{node.port}" if hasattr(node, "port") else f"{node.ip_address}:51820"
    
    config = QRCodeGenerator.generate_wireguard_config(
        private_key=user_node.private_key,
        address=user_node.allowed_ips,
        peer_public_key=peer_public_key,
        peer_endpoint=peer_endpoint
    )
    
    return Response(
        content=config,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=wireguard-{user_node_id}.conf"}
    )
