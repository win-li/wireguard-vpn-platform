from sqlalchemy.orm import Session
from models.user_nodes import UserNode
from models.nodes import Node
from models.users import User
from utils.wireguard import generate_wireguard_keys, generate_client_config
from datetime import datetime

def create_user_node_connection(db: Session, user_id: int, node_id: int):
    # Generate WireGuard keys for the user
    private_key, public_key = generate_wireguard_keys()

    # Get node information
    node = db.query(Node).filter(Node.id == node_id).first()

    # Assign a unique IP address to the user in the node subnet
    # This is simplified logic - in production, you would need to track assigned IPs
    user_ip = f"10.8.{node_id}.{user_id+100}"

    # Create new user-node connection record
    user_node = UserNode(
        user_id=user_id,
        node_id=node_id,
        private_key=private_key,
        allowed_ips=user_ip,
        connected_at=datetime.utcnow(),
        is_active=True
    )
    db.add(user_node)
    db.commit()
    db.refresh(user_node)

    # Also update node load
    node.current_load += 1
    db.commit()

    return user_node

def get_user_node_connection(db: Session, user_id: int, node_id: int):
    return db.query(UserNode).filter(
        UserNode.user_id == user_id,
        UserNode.node_id == node_id
    ).first()

def get_user_connections(db: Session, user_id: int):
    return db.query(UserNode).filter(UserNode.user_id == user_id).all()

def update_user_node_connection(db: Session, user_node_id: int, **kwargs):
    user_node = db.query(UserNode).filter(UserNode.id == user_node_id).first()
    for key, value in kwargs.items():
        setattr(user_node, key, value)
    db.commit()
    db.refresh(user_node)
    return user_node

def delete_user_node_connection(db: Session, user_node_id: int):
    user_node = db.query(UserNode).filter(UserNode.id == user_node_id).first()
    if user_node:
        # Update node load
        node = db.query(Node).filter(Node.id == user_node.node_id).first()
        if node:
            node.current_load -= 1
            db.commit()

        db.delete(user_node)
        db.commit()
        return True
    return False
