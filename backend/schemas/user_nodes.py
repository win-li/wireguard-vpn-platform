from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserNodeCreate(BaseModel):
    node_id: int

class UserNodeResponse(BaseModel):
    id: int
    user_id: int
    node_id: int
    allowed_ips: Optional[str] = None
    connected_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
