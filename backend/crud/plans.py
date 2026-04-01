from sqlalchemy.orm import Session
from typing import List, Optional
from models.plans import Plan
from schemas.plans import PlanCreate, PlanUpdate

def get_plan_by_id(db: Session, plan_id: int) -> Optional[Plan]:
    return db.query(Plan).filter(Plan.id == plan_id).first()

def get_plans(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Plan]:
    query = db.query(Plan)
    if active_only:
        query = query.filter(Plan.is_active == True)
    return query.order_by(Plan.sort_order, Plan.id).offset(skip).limit(limit).all()

def get_active_plans(db: Session) -> List[Plan]:
    return db.query(Plan).filter(Plan.is_active == True).order_by(Plan.sort_order, Plan.id).all()

def create_plan(db: Session, plan: PlanCreate) -> Plan:
    db_plan = Plan(
        name=plan.name,
        description=plan.description,
        price=plan.price,
        duration_days=plan.duration_days,
        bandwidth_limit=plan.bandwidth_limit,
        device_limit=plan.device_limit,
        node_access=plan.node_access,
        features=plan.features,
        is_active=plan.is_active,
        sort_order=plan.sort_order
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: int, plan_update: PlanUpdate) -> Optional[Plan]:
    db_plan = get_plan_by_id(db, plan_id)
    if not db_plan:
        return None
    update_data = plan_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int) -> bool:
    db_plan = get_plan_by_id(db, plan_id)
    if not db_plan:
        return False
    db.delete(db_plan)
    db.commit()
    return True
