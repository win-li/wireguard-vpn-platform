from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from config.database import get_db
from models.users import User
from models.user_nodes import UserNode
from models.subscriptions import Subscription
from models.nodes import Node
from models.traffic_logs import TrafficLog

router = APIRouter()

# Prometheus metrics collector
class MetricsCollector:
    def __init__(self):
        self._metrics = {}
    
    def gauge(self, name: str, value: float, labels: dict = None):
        key = name
        if labels:
            label_str = ','.join([f'{k}="{v}"' for k, v in labels.items()])
            key = f'{name}{{{label_str}}}'
        self._metrics[key] = value
    
    def counter(self, name: str, value: float, labels: dict = None):
        key = name
        if labels:
            label_str = ','.join([f'{k}="{v}"' for k, v in labels.items()])
            key = f'{name}{{{label_str}}}'
        if key in self._metrics:
            self._metrics[key] += value
        else:
            self._metrics[key] = value
    
    def export(self):
        lines = []
        for key, value in self._metrics.items():
            lines.append(f'{key} {value}')
        return '\n'.join(lines)


metrics = MetricsCollector()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    # User metrics
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.status == "active").scalar() or 0
    metrics.gauge("vpn_users_total", total_users)
    metrics.gauge("vpn_users_active", active_users)
    
    # Node metrics
    total_nodes = db.query(func.count(Node.id)).scalar() or 0
    active_nodes = db.query(func.count(Node.id)).filter(Node.status == "active").scalar() or 0
    metrics.gauge("vpn_nodes_total", total_nodes)
    metrics.gauge("vpn_nodes_active", active_nodes)
    
    # Subscription metrics
    active_subs = db.query(func.count(Subscription.id)).filter(
        Subscription.status == "active",
        Subscription.expire_at > datetime.now()
    ).scalar() or 0
    metrics.gauge("vpn_subscriptions_active", active_subs)
    
    # Traffic metrics (last 24h)
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    traffic_24h = db.query(
        func.sum(TrafficLog.bytes_sent + TrafficLog.bytes_received)
    ).filter(TrafficLog.logged_at >= yesterday).scalar() or 0
    metrics.gauge("vpn_traffic_bytes_24h", float(traffic_24h))
    
    # Connection metrics
    active_connections = db.query(func.count(UserNode.id)).filter(
        UserNode.is_active == True
    ).scalar() or 0
    metrics.gauge("vpn_connections_active", active_connections)
    
    return Response(content=metrics.export(), media_type="text/plain")


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "metrics"}
