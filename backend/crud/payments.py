from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.payments import Payment, USDTWallet
from schemas.payments import PaymentCreate, PaymentCallback

def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_payment_by_transaction(db: Session, transaction_id: str) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    return db.query(Payment).filter(Payment.user_id == user_id).offset(skip).limit(limit).all()

def get_payments(db: Session, skip: int = 0, limit: int = 100, status: str = None) -> List[Payment]:
    query = db.query(Payment)
    if status:
        query = query.filter(Payment.status == status)
    return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

def create_payment(db: Session, payment: PaymentCreate, user_id: int) -> Payment:
    db_payment = Payment(
        user_id=user_id,
        subscription_id=payment.subscription_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        status="pending"
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment_status(db: Session, payment_id: int, callback: PaymentCallback) -> Optional[Payment]:
    db_payment = get_payment_by_id(db, payment_id)
    if not db_payment:
        return None
    db_payment.transaction_id = callback.transaction_id
    db_payment.status = callback.status
    db_payment.metadata = callback.payment_metadata
    if callback.status == "success":
        db_payment.paid_at = datetime.now()
    db.commit()
    db.refresh(db_payment)
    return db_payment

def process_payment_callback(db: Session, transaction_id: str, status: str, metadata: str = None) -> Optional[Payment]:
    db_payment = get_payment_by_transaction(db, transaction_id)
    if not db_payment:
        return None
    db_payment.status = status
    db_payment.metadata = metadata
    if status == "success":
        db_payment.paid_at = datetime.now()
    db.commit()
    db.refresh(db_payment)
    return db_payment

# USDT钱包相关操作
def get_available_wallet(db: Session, network: str) -> Optional[USDTWallet]:
    """获取可用的钱包地址"""
    return db.query(USDTWallet).filter(
        USDTWallet.network == network,
        USDTWallet.is_active == True,
        USDTWallet.current_payment_id == None
    ).first()

def bind_wallet_to_payment(db: Session, wallet: USDTWallet, payment_id: int):
    """绑定钱包到支付订单"""
    wallet.current_payment_id = payment_id
    wallet.last_used_at = datetime.now()
    db.commit()

def release_wallet(db: Session, wallet_id: int):
    """释放钱包绑定"""
    wallet = db.query(USDTWallet).filter(USDTWallet.id == wallet_id).first()
    if wallet:
        wallet.current_payment_id = None
        db.commit()

def create_wallet(db: Session, address: str, network: str) -> USDTWallet:
    """创建新的钱包地址"""
    wallet = USDTWallet(
        address=address,
        network=network.upper(),
        is_active=True
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet
