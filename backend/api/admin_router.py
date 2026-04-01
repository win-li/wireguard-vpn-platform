from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from config.database import get_db
from models.users import User
from models.nodes import Node
from models.payments import Payment
from models.subscriptions import Subscription
from models.traffic_logs import TrafficLog
from models.admin_logs import AdminLog
from api.deps import get_current_user

router = APIRouter()


# ============ Pydantic Models ============

class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    phone: Optional[str]
    role: str
    status: str
    balance: int
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    status: Optional[str] = None
    role: Optional[str] = None
    balance: Optional[int] = None


class AdminNodeCreate(BaseModel):
    name: str
    region: str
    country: str
    city: Optional[str] = None
    ip_address: str
    port: int = 51820
    protocol: str = "wireguard"
    public_key: Optional[str] = None
    bandwidth_limit: Optional[int] = None
    max_load: int = 100
    is_premium: bool = False
    sort_order: int = 0


class AdminNodeUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    bandwidth_limit: Optional[int] = None
    max_load: Optional[int] = None
    is_premium: Optional[bool] = None
    sort_order: Optional[int] = None


class AdminNodeResponse(BaseModel):
    id: int
    name: str
    region: str
    country: str
    city: Optional[str]
    ip_address: str
    port: int
    protocol: str
    status: str
    current_load: int
    max_load: int
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminPaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    currency: str
    payment_method: Optional[str]
    transaction_id: Optional[str]
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    reason: str


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_week: int
    total_nodes: int
    active_nodes: int
    total_revenue: float
    revenue_today: float
    revenue_month: float
    total_traffic_gb: float
    traffic_today_gb: float


class TrafficStats(BaseModel):
    user_id: int
    username: Optional[str]
    email: str
    total_bytes: int
    total_gb: float


# ============ Admin Dependency ============

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def log_admin_action(db: Session, admin_id: int, action: str, target_type: str, target_id: int, details: str = None):
    log = AdminLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        log_details=details
    )
    db.add(log)
    db.commit()


# ============ Dashboard Stats ============

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar()
    new_users_today = db.query(func.count(User.id)).filter(User.created_at >= today_start).scalar()
    new_users_week = db.query(func.count(User.id)).filter(User.created_at >= week_start).scalar()

    total_nodes = db.query(func.count(Node.id)).scalar()
    active_nodes = db.query(func.count(Node.id)).filter(Node.status == "active").scalar()

    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "success").scalar() or 0
    revenue_today = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "success",
        Payment.paid_at >= today_start
    ).scalar() or 0
    revenue_month = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "success",
        Payment.paid_at >= month_start
    ).scalar() or 0

    total_traffic = db.query(
        func.sum(TrafficLog.bytes_sent) + func.sum(TrafficLog.bytes_received)
    ).scalar() or 0
    traffic_today = db.query(
        func.sum(TrafficLog.bytes_sent) + func.sum(TrafficLog.bytes_received)
    ).filter(TrafficLog.logged_at >= today_start).scalar() or 0

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        total_nodes=total_nodes,
        active_nodes=active_nodes,
        total_revenue=float(total_revenue),
        revenue_today=float(revenue_today),
        revenue_month=float(revenue_month),
        total_traffic_gb=total_traffic / (1024**3),
        traffic_today_gb=traffic_today / (1024**3)
    )


# ============ User Management ============

@router.get("/users", response_model=List[AdminUserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    query = db.query(User)

    if status:
        query = query.filter(User.status == status)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
        )

    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    update_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.status:
        user.status = update_data.status
    if update_data.role:
        user.role = update_data.role
    if update_data.balance is not None:
        user.balance = update_data.balance

    db.commit()
    log_admin_action(db, admin.id, "update_user", "user", user_id, f"Updated user {user.email}")

    return {"message": "User updated successfully", "user_id": user_id}


@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "suspended"
    db.commit()
    log_admin_action(db, admin.id, "suspend_user", "user", user_id, f"Suspended user {user.email}")

    return {"message": "User suspended", "user_id": user_id}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "active"
    db.commit()
    log_admin_action(db, admin.id, "activate_user", "user", user_id, f"Activated user {user.email}")

    return {"message": "User activated", "user_id": user_id}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "deleted"
    db.commit()
    log_admin_action(db, admin.id, "delete_user", "user", user_id, f"Deleted user {user.email}")

    return {"message": "User deleted", "user_id": user_id}


# ============ Node Management ============

@router.get("/nodes", response_model=List[AdminNodeResponse])
def list_nodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    region: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    query = db.query(Node)

    if status:
        query = query.filter(Node.status == status)
    if region:
        query = query.filter(Node.region == region)

    nodes = query.order_by(Node.sort_order, Node.created_at.desc()).offset(skip).limit(limit).all()
    return nodes


@router.post("/nodes", response_model=AdminNodeResponse)
def create_node(
    node_data: AdminNodeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    node = Node(**node_data.dict())
    db.add(node)
    db.commit()
    db.refresh(node)

    log_admin_action(db, admin.id, "create_node", "node", node.id, f"Created node {node.name}")

    return node


@router.put("/nodes/{node_id}")
def update_node(
    node_id: int,
    update_data: AdminNodeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(node, field, value)

    db.commit()
    log_admin_action(db, admin.id, "update_node", "node", node_id, f"Updated node {node.name}")

    return {"message": "Node updated", "node_id": node_id}


@router.delete("/nodes/{node_id}")
def delete_node(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()
    log_admin_action(db, admin.id, "delete_node", "node", node_id, f"Deleted node {node.name}")

    return {"message": "Node deleted", "node_id": node_id}


# ============ Order Management ============

@router.get("/orders", response_model=List[AdminPaymentResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    query = db.query(Payment)

    if status:
        query = query.filter(Payment.status == status)
    if user_id:
        query = query.filter(Payment.user_id == user_id)

    orders = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.post("/orders/{order_id}/refund")
def refund_order(
    order_id: int,
    refund_data: RefundRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    order = db.query(Payment).filter(Payment.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "success":
        raise HTTPException(status_code=400, detail="Only successful orders can be refunded")

    order.status = "refunded"
    db.commit()

    log_admin_action(
        db, admin.id, "refund_order", "payment", order_id,
        f"Refunded order {order_id}, reason: {refund_data.reason}"
    )

    return {"message": "Order refunded", "order_id": order_id}


# ============ Traffic Statistics ============

@router.get("/traffic/top-users", response_model=List[TrafficStats])
def get_top_traffic_users(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        TrafficLog.user_id,
        User.username,
        User.email,
        func.sum(TrafficLog.bytes_sent + TrafficLog.bytes_received).label('total_bytes')
    ).join(
        User, TrafficLog.user_id == User.id
    ).filter(
        TrafficLog.logged_at >= start_date
    ).group_by(
        TrafficLog.user_id, User.username, User.email
    ).order_by(
        func.sum(TrafficLog.bytes_sent + TrafficLog.bytes_received).desc()
    ).limit(limit).all()

    return [
        TrafficStats(
            user_id=r.user_id,
            username=r.username,
            email=r.email,
            total_bytes=r.total_bytes,
            total_gb=r.total_bytes / (1024**3)
        ) for r in results
    ]
