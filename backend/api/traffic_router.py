from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from config.database import get_db
from models.traffic_logs import TrafficLog
from models.users import User
from models.nodes import Node
from api.deps import get_current_user

router = APIRouter()


# ============ Pydantic Models ============

class TrafficRecordCreate(BaseModel):
    user_id: int
    node_id: int
    bytes_sent: int
    bytes_received: int
    session_duration: Optional[int] = None
    client_ip: Optional[str] = None


class TrafficRecordResponse(BaseModel):
    id: int
    user_id: int
    node_id: int
    bytes_sent: int
    bytes_received: int
    session_duration: Optional[int]
    client_ip: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True


class UserTrafficSummary(BaseModel):
    user_id: int
    username: Optional[str]
    email: str
    total_sent: int
    total_received: int
    total_bytes: int
    total_gb: float
    session_count: int


class DailyTrafficStats(BaseModel):
    date: str
    total_sent: int
    total_received: int
    total_gb: float


class NodeTrafficStats(BaseModel):
    node_id: int
    node_name: str
    region: str
    total_bytes: int
    total_gb: float
    user_count: int


# ============ Traffic Recording ============

@router.post("/record")
def record_traffic(
    traffic_data: TrafficRecordCreate,
    db: Session = Depends(get_db)
):
    log = TrafficLog(
        user_id=traffic_data.user_id,
        node_id=traffic_data.node_id,
        bytes_sent=traffic_data.bytes_sent,
        bytes_received=traffic_data.bytes_received,
        session_duration=traffic_data.session_duration,
        client_ip=traffic_data.client_ip
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Traffic recorded", "id": log.id}


@router.get("/my", response_model=UserTrafficSummary)
def get_my_traffic(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    result = db.query(
        func.sum(TrafficLog.bytes_sent).label('total_sent'),
        func.sum(TrafficLog.bytes_received).label('total_received'),
        func.count(TrafficLog.id).label('session_count')
    ).filter(
        TrafficLog.user_id == current_user.id,
        TrafficLog.logged_at >= start_date
    ).first()

    total_sent = result.total_sent or 0
    total_received = result.total_received or 0
    total_bytes = total_sent + total_received

    return UserTrafficSummary(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        total_sent=total_sent,
        total_received=total_received,
        total_bytes=total_bytes,
        total_gb=round(total_bytes / (1024**3), 3),
        session_count=result.session_count or 0
    )


@router.get("/my/daily", response_model=List[DailyTrafficStats])
def get_my_daily_traffic(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        func.date(TrafficLog.logged_at).label('date'),
        func.sum(TrafficLog.bytes_sent).label('total_sent'),
        func.sum(TrafficLog.bytes_received).label('total_received')
    ).filter(
        TrafficLog.user_id == current_user.id,
        TrafficLog.logged_at >= start_date
    ).group_by(
        func.date(TrafficLog.logged_at)
    ).order_by(
        func.date(TrafficLog.logged_at).desc()
    ).all()

    return [
        DailyTrafficStats(
            date=str(r.date),
            total_sent=r.total_sent or 0,
            total_received=r.total_received or 0,
            total_gb=round((r.total_sent or 0 + r.total_received or 0) / (1024**3), 3)
        ) for r in results
    ]


@router.get("/my/by-node", response_model=List[NodeTrafficStats])
def get_my_traffic_by_node(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        TrafficLog.node_id,
        Node.name,
        Node.region,
        func.sum(TrafficLog.bytes_sent + TrafficLog.bytes_received).label('total_bytes'),
        func.count(func.distinct(TrafficLog.user_id)).label('user_count')
    ).join(
        Node, TrafficLog.node_id == Node.id
    ).filter(
        TrafficLog.user_id == current_user.id,
        TrafficLog.logged_at >= start_date
    ).group_by(
        TrafficLog.node_id, Node.name, Node.region
    ).order_by(
        func.sum(TrafficLog.bytes_sent + TrafficLog.bytes_received).desc()
    ).all()

    return [
        NodeTrafficStats(
            node_id=r.node_id,
            node_name=r.name,
            region=r.region,
            total_bytes=r.total_bytes or 0,
            total_gb=round((r.total_bytes or 0) / (1024**3), 3),
            user_count=r.user_count or 0
        ) for r in results
    ]
