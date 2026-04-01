from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 用户创建
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    phone: Optional[str] = None

# 用户响应
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: str
    balance: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None

    class Config:
        from_attributes = True

# 用户登录
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 用户登录响应
class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    user: UserResponse

# 用户更新
class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
