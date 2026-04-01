from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from config.database import get_db
from models.users import User
from schemas.users import UserLogin, UserLoginResponse, UserResponse
from crud.users import authenticate_user, update_last_login
from utils.security import create_access_token, create_refresh_token, verify_token
from api.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=UserLoginResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )
    
    # Update last login
    update_last_login(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
def logout_user():
    # In a real implementation, you might add the token to a blacklist
    return {"message": "Logged out successfully"}

@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...)):
    # Verify refresh token
    token_data = verify_token(refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    new_access_token = create_access_token(
        data={"sub": token_data.get("sub")}, expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}
