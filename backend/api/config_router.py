from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse

from models.user_nodes import UserNode as UserNodeModel
from models.nodes import Node
from crud.user_nodes import get_user_node_connection
from api.deps import get_current_user, get_db
from models.users import User
from utils.wireguard import generate_client_config

router = APIRouter()

@router.get("/configs/{node_id}", response_class=PlainTextResponse)
def get_wireguard_config(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user-node connection
    user_node = get_user_node_connection(db, current_user.id, node_id)
    if not user_node:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Get the node information
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Generate the client configuration
    server_endpoint = f"{node.ip_address}:{node.port}"
    config_content = generate_client_config(
        server_public_key=node.public_key,
        client_private_key=user_node.private_key,
        server_endpoint=server_endpoint,
        client_ip=user_node.allowed_ips,
        dns_server="8.8.8.8"  # Could be configurable
    )

    # Return the config as a downloadable file
    filename = f"vpn-config-{node.name.lower().replace(' ', '-')}.conf"
    return Response(
        content=config_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
