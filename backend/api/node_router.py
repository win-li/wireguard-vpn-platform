from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.user_nodes import UserNode as UserNodeModel
from schemas.user_nodes import UserNodeCreate, UserNodeResponse
from crud.user_nodes import create_user_node_connection, get_user_connections, get_user_node_connection, delete_user_node_connection
from api.deps import get_current_user, get_db
from models.users import User

router = APIRouter()

@router.post("/connections", response_model=UserNodeResponse)
def create_connection(
    connection: UserNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify user has access to the requested node
    # In a real implementation, you would check subscription status
    return create_user_node_connection(db, current_user.id, connection.node_id)

@router.get("/connections", response_model=List[UserNodeResponse])
def get_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_connections(db, current_user.id)

@router.get("/connections/{node_id}", response_model=UserNodeResponse)
def get_connection(
    node_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connection = get_user_node_connection(db, current_user.id, node_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection

@router.delete("/connections/{connection_id}")
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_user_node_connection(db, connection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection deleted successfully"}
