from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


# 支付创建
class PaymentCreate(BaseModel):
    subscription_id: int
    amount: Decimal
    currency: str = "CNY"
    payment_method: str


# USDT支付创建
class USDTPaymentCreate(BaseModel):
    subscription_id: int
    amount: Decimal  # CNY金额
    currency: str = "CNY"
    network: str = "TRC20"  # TRC20 或 ERC20


# USDT支付响应
class USDTPaymentResponse(BaseModel):
    payment_id: int
    wallet_address: str
    network: str
    usdt_amount: float
    exchange_rate: float
    expires_at: str
    qr_code: str
    contract_address: str

    class Config:
        from_attributes = True


# 支付状态响应
class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str
    wallet_address: Optional[str] = None
    network: Optional[str] = None
    usdt_amount: Optional[float] = None
    tx_hash: Optional[str] = None
    remaining_seconds: Optional[int] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 支付响应
class PaymentResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    amount: Decimal
    currency: str
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    wallet_address: Optional[str] = None
    network_type: Optional[str] = None
    usdt_amount: Optional[Decimal] = None
    tx_hash: Optional[str] = None
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 支付回调
class PaymentCallback(BaseModel):
    transaction_id: str
    status: str
    payment_metadata: Optional[str] = None  # 保持兼容性
