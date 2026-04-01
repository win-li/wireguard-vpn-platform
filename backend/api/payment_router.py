from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
import asyncio

from config.database import get_db
from models.users import User
from models.payments import Payment, USDTWallet
from schemas.payments import (
    PaymentCreate, PaymentResponse, PaymentCallback,
    USDTPaymentCreate, USDTPaymentResponse, PaymentStatusResponse
)
from crud.payments import (
    get_payment_by_id,
    get_user_payments,
    get_payments,
    create_payment,
    update_payment_status,
    process_payment_callback
)
from crud.subscriptions import get_subscription_by_id
from crud.plans import get_plan_by_id
from api.deps import get_current_user
from utils.usdt_payment import USDTPayment, check_all_pending_payments

router = APIRouter(prefix="/payments", tags=["payments"])


# 用户接口 - 获取支付历史
@router.get("/history", response_model=List[PaymentResponse])
def get_payment_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的支付历史"""
    return get_user_payments(db, current_user.id, skip, limit)


# 用户接口 - 创建USDT支付订单
@router.post("/usdt/create", response_model=USDTPaymentResponse)
async def create_usdt_payment(
    payment_data: USDTPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建USDT支付订单"""
    # 验证订阅
    sub = get_subscription_by_id(db, payment_data.subscription_id)
    if not sub or sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription"
        )
    
    # 创建基础支付记录
    payment = Payment(
        user_id=current_user.id,
        subscription_id=payment_data.subscription_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=f"usdt_{payment_data.network.lower()}",
        status="pending"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # 创建USDT支付详情
    usdt_payment = USDTPayment(db)
    result = await usdt_payment.create_payment(payment.id, payment_data.network)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return USDTPaymentResponse(**result)


# 用户接口 - 检查USDT支付状态
@router.get("/usdt/{payment_id}/status", response_model=PaymentStatusResponse)
async def check_usdt_payment_status(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查USDT支付状态"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # 只检查USDT支付
    if not payment.payment_method or not payment.payment_method.startswith("usdt_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a USDT payment"
        )
    
    usdt_payment = USDTPayment(db)
    result = await usdt_payment.check_payment_status(payment_id)
    
    return PaymentStatusResponse(
        payment_id=payment_id,
        status=result.get("status", payment.status),
        wallet_address=payment.wallet_address,
        network=payment.network_type,
        usdt_amount=float(payment.usdt_amount) if payment.usdt_amount else None,
        tx_hash=result.get("tx_hash") or payment.tx_hash,
        remaining_seconds=result.get("remaining_seconds"),
        paid_at=payment.paid_at
    )


# 用户接口 - 创建支付订单
@router.post("/create", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_order(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建支付订单"""
    # 验证订阅
    sub = get_subscription_by_id(db, payment.subscription_id)
    if not sub or sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription"
        )
    
    # 创建支付记录
    db_payment = create_payment(db, payment, current_user.id)
    
    # TODO: 集成实际支付网关（支付宝、微信、Stripe等）
    # 这里返回模拟数据，实际应调用支付网关API获取支付链接
    
    return db_payment


# 用户接口 - 查询支付状态
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_status(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询支付状态"""
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return payment


# 支付回调接口 - 支付宝回调
@router.post("/callback/alipay")
def alipay_callback(
    transaction_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """支付宝支付回调"""
    payment = process_payment_callback(db, transaction_id, status)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return {"success": True, "payment_id": payment.id}


# 支付回调接口 - 微信支付回调
@router.post("/callback/wechat")
def wechat_callback(
    transaction_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """微信支付回调"""
    payment = process_payment_callback(db, transaction_id, status)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return {"success": True, "payment_id": payment.id}


# 支付回调接口 - Stripe Webhook
@router.post("/callback/stripe")
def stripe_callback(
    transaction_id: str,
    status: str,
    metadata: str = None,
    db: Session = Depends(get_db)
):
    """Stripe支付回调"""
    payment = process_payment_callback(db, transaction_id, status, metadata)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return {"success": True, "payment_id": payment.id}


# 管理接口 - 获取所有支付记录
@router.get("/admin/all", response_model=List[PaymentResponse])
def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有支付记录（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return get_payments(db, skip, limit, status_filter)


# 管理接口 - 手动确认支付
@router.post("/admin/{payment_id}/confirm", response_model=PaymentResponse)
def admin_confirm_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动确认支付（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    callback = PaymentCallback(
        transaction_id=f"manual_{uuid.uuid4().hex[:16]}",
        status="success"
    )
    return update_payment_status(db, payment_id, callback)


# 管理接口 - 退款
@router.post("/admin/{payment_id}/refund", response_model=PaymentResponse)
def admin_refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """退款（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    if payment.status != "success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund successful payments"
        )
    callback = PaymentCallback(
        transaction_id=payment.transaction_id,
        status="refunded"
    )
    return update_payment_status(db, payment_id, callback)


# 管理接口 - 添加USDT钱包
@router.post("/admin/wallets/add")
def add_usdt_wallet(
    address: str,
    network: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加USDT钱包地址（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # 检查是否已存在
    existing = db.query(USDTWallet).filter(USDTWallet.address == address).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address already exists"
        )
    
    wallet = USDTWallet(
        address=address,
        network=network.upper(),
        is_active=True
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    
    return {"success": True, "wallet_id": wallet.id}


# 管理接口 - 获取USDT钱包列表
@router.get("/admin/wallets")
def get_usdt_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取USDT钱包列表（管理员接口）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    wallets = db.query(USDTWallet).all()
    return [{
        "id": w.id,
        "address": w.address,
        "network": w.network,
        "is_active": w.is_active,
        "current_payment_id": w.current_payment_id,
        "last_used_at": w.last_used_at
    } for w in wallets]


# 定时任务接口 - 检查USDT支付
@router.post("/internal/check-usdt-payments")
async def trigger_check_usdt_payments():
    """触发检查USDT支付（供定时任务调用）"""
    result = await check_all_pending_payments()
    return result
