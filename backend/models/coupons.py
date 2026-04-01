from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.sql import func
from config.database import Base

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20))  # percentage, fixed
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    applicable_plans = Column(Text)  # 适用套餐 ID（JSON 格式）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
