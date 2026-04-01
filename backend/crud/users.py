from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.users import User
from schemas.users import UserCreate, UserUpdate
import bcrypt
from datetime import datetime
import logging

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            username=user.username,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError('Email or username already registered')

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['password_hash'] = get_password_hash(update_data.pop('password'))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def update_last_login(db: Session, user_id: int, ip_address: str = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.last_login_at = datetime.now()
        if ip_address:
            db_user.last_login_ip = ip_address
        db.commit()
        db.refresh(db_user)
    return db_user
