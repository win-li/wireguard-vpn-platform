"""
USDT支付工具
支持 TRC20 (Tron网络) 和 ERC20 (以太坊网络)
"""
import os
import json
import secrets
import qrcode
import io
import base64
import httpx
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.payments import Payment, USDTWallet
from config.database import get_db


class USDTConfig:
    """USDT支付配置"""
    # TronGrid API (Tron网络)
    TRONGRID_API = os.getenv("TRONGRID_API", "https://api.trongrid.io")
    TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY", "")
    
    # Etherscan API (以太坊网络)
    ETHERSCAN_API = os.getenv("ETHERSCAN_API", "https://api.etherscan.io/api")
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
    
    # USDT合约地址
    USDT_TRC20_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # Tron网络USDT合约
    USDT_ERC20_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # 以太坊USDT合约
    
    # 支付过期时间（分钟）
    PAYMENT_EXPIRE_MINUTES = int(os.getenv("USDT_EXPIRE_MINUTES", "30"))
    
    # 最小确认数
    TRC20_CONFIRMATIONS = int(os.getenv("TRC20_CONFIRMATIONS", "19"))  # Tron网络确认数
    ERC20_CONFIRMATIONS = int(os.getenv("ERC20_CONFIRMATIONS", "12"))  # 以太坊确认数
    
    # 汇率API
    EXCHANGE_RATE_API = os.getenv("EXCHANGE_RATE_API", "https://api.exchangerate-api.com/v4/latest/USD")


class USDTPayment:
    """USDT支付处理类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = USDTConfig()
    
    async def get_exchange_rate(self) -> Decimal:
        """获取USDT对CNY的汇率"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.config.EXCHANGE_RATE_API, timeout=10)
                data = response.json()
                return Decimal(str(data["rates"]["CNY"]))
        except Exception as e:
            # 默认汇率
            return Decimal("7.24")
    
    def cny_to_usdt(self, cny_amount: Decimal, rate: Optional[Decimal] = None) -> Decimal:
        """CNY转USDT"""
        if rate is None:
            rate = Decimal("7.24")  # 默认汇率
        usdt_amount = cny_amount / rate
        # 四舍五入到6位小数
        return usdt_amount.quantize(Decimal("0.000001"))
    
    async def get_available_wallet(self, network: str) -> Optional[USDTWallet]:
        """获取可用的钱包地址"""
        # 查找未被使用的活跃钱包
        wallet = self.db.query(USDTWallet).filter(
            and_(
                USDTWallet.network == network,
                USDTWallet.is_active == True,
                USDTWallet.current_payment_id == None
            )
        ).first()
        
        # 如果没有可用钱包，生成一个新地址（演示用）
        if not wallet:
            # 在实际生产环境中，应该从钱包池获取或通过HD钱包派生
            # 这里使用演示地址
            wallet = self._create_demo_wallet(network)
        
        return wallet
    
    def _create_demo_wallet(self, network: str) -> USDTWallet:
        """创建演示钱包地址（实际生产环境应使用真实的钱包服务）"""
        # 演示用固定地址（实际生产环境需要真实钱包）
        demo_addresses = {
            "TRC20": "TYourTronAddressHere123456789",
            "ERC20": "0xYourEthereumAddressHere123456789abcdef"
        }
        
        wallet = USDTWallet(
            address=demo_addresses.get(network, demo_addresses["TRC20"]),
            network=network,
            is_active=True
        )
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet
    
    def bind_wallet_to_payment(self, wallet: USDTWallet, payment_id: int):
        """绑定钱包到支付订单"""
        wallet.current_payment_id = payment_id
        wallet.last_used_at = datetime.now()
        self.db.commit()
    
    def release_wallet(self, wallet_id: int):
        """释放钱包绑定"""
        wallet = self.db.query(USDTWallet).filter(USDTWallet.id == wallet_id).first()
        if wallet:
            wallet.current_payment_id = None
            self.db.commit()
    
    async def create_payment(
        self,
        payment_id: int,
        network: str = "TRC20"
    ) -> Dict[str, Any]:
        """创建USDT支付订单"""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"error": "Payment not found"}
        
        # 获取可用钱包
        wallet = await self.get_available_wallet(network)
        if not wallet:
            return {"error": "No available wallet"}
        
        # 计算USDT金额
        rate = await self.get_exchange_rate()
        usdt_amount = self.cny_to_usdt(payment.amount, rate)
        
        # 更新支付信息
        payment.wallet_address = wallet.address
        payment.network_type = network
        payment.usdt_amount = usdt_amount
        payment.payment_method = f"usdt_{network.lower()}"
        payment.expires_at = datetime.now() + timedelta(minutes=self.config.PAYMENT_EXPIRE_MINUTES)
        
        # 绑定钱包
        self.bind_wallet_to_payment(wallet, payment_id)
        
        self.db.commit()
        self.db.refresh(payment)
        
        # 生成二维码
        qr_code_base64 = self.generate_qr_code(wallet.address, usdt_amount, network)
        
        return {
            "payment_id": payment.id,
            "wallet_address": wallet.address,
            "network": network,
            "usdt_amount": float(usdt_amount),
            "exchange_rate": float(rate),
            "expires_at": payment.expires_at.isoformat(),
            "qr_code": qr_code_base64,
            "contract_address": self._get_contract_address(network)
        }
    
    def _get_contract_address(self, network: str) -> str:
        """获取USDT合约地址"""
        if network == "TRC20":
            return self.config.USDT_TRC20_CONTRACT
        elif network == "ERC20":
            return self.config.USDT_ERC20_CONTRACT
        return ""
    
    def generate_qr_code(
        self,
        address: str,
        amount: Decimal,
        network: str
    ) -> str:
        """生成二维码"""
        # 格式: usdt:address?amount=xxx&network=xxx
        qr_data = f"usdt:{address}?amount={amount}&network={network}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转为base64
        buffer = io.BytesIO()
        img.save(buffer)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    async def check_trc20_transaction(
        self,
        address: str,
        expected_amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """检查TRC20交易"""
        try:
            async with httpx.AsyncClient() as client:
                # 查询TRC20转账记录
                url = f"{self.config.TRONGRID_API}/v1/accounts/{address}/transactions/trc20"
                headers = {}
                if self.config.TRONGRID_API_KEY:
                    headers["TRON-PRO-API-KEY"] = self.config.TRONGRID_API_KEY
                
                params = {
                    "limit": 20,
                    "contract_address": self.config.USDT_TRC20_CONTRACT
                }
                
                response = await client.get(url, headers=headers, params=params, timeout=15)
                data = response.json()
                
                if "data" not in data:
                    return None
                
                for tx in data["data"]:
                    # 检查是否是转入交易
                    if tx.get("to", "").lower() == address.lower():
                        tx_value = Decimal(str(tx.get("value", 0))) / Decimal("1000000")  # USDT有6位小数
                        
                        # 检查金额是否匹配（允许小误差）
                        if abs(tx_value - expected_amount) < Decimal("0.01"):
                            return {
                                "tx_hash": tx.get("transaction_id"),
                                "amount": float(tx_value),
                                "from_address": tx.get("from"),
                                "to_address": tx.get("to"),
                                "timestamp": tx.get("block_timestamp"),
                                "confirmed": True
                            }
                
                return None
                
        except Exception as e:
            print(f"Error checking TRC20 transaction: {e}")
            return None
    
    async def check_erc20_transaction(
        self,
        address: str,
        expected_amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """检查ERC20交易"""
        try:
            async with httpx.AsyncClient() as client:
                # 查询ERC20转账记录
                params = {
                    "module": "account",
                    "action": "tokentx",
                    "contractaddress": self.config.USDT_ERC20_CONTRACT,
                    "address": address,
                    "apikey": self.config.ETHERSCAN_API_KEY,
                    "sort": "desc"
                }
                
                response = await client.get(
                    self.config.ETHERSCAN_API,
                    params=params,
                    timeout=15
                )
                data = response.json()
                
                if data.get("status") != "1" or "result" not in data:
                    return None
                
                for tx in data["result"]:
                    tx_value = Decimal(str(tx.get("value", 0))) / Decimal("1000000")
                    
                    # 检查金额是否匹配
                    if abs(tx_value - expected_amount) < Decimal("0.01"):
                        confirmations = int(tx.get("confirmations", 0))
                        
                        return {
                            "tx_hash": tx.get("hash"),
                            "amount": float(tx_value),
                            "from_address": tx.get("from"),
                            "to_address": tx.get("to"),
                            "timestamp": int(tx.get("timeStamp", 0)),
                            "confirmations": confirmations,
                            "confirmed": confirmations >= self.config.ERC20_CONFIRMATIONS
                        }
                
                return None
                
        except Exception as e:
            print(f"Error checking ERC20 transaction: {e}")
            return None
    
    async def check_payment_status(self, payment_id: int) -> Dict[str, Any]:
        """检查支付状态"""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"error": "Payment not found"}
        
        # 检查是否过期
        if payment.expires_at and datetime.now() > payment.expires_at:
            payment.status = "expired"
            self.db.commit()
            return {"status": "expired", "message": "Payment expired"}
        
        # 如果已经成功，直接返回
        if payment.status == "success":
            return {"status": "success", "tx_hash": payment.tx_hash}
        
        # 检查链上交易
        tx_info = None
        if payment.network_type == "TRC20":
            tx_info = await self.check_trc20_transaction(
                payment.wallet_address,
                payment.usdt_amount
            )
        elif payment.network_type == "ERC20":
            tx_info = await self.check_erc20_transaction(
                payment.wallet_address,
                payment.usdt_amount
            )
        
        if tx_info and tx_info.get("confirmed"):
            # 更新支付状态
            payment.tx_hash = tx_info["tx_hash"]
            payment.status = "success"
            payment.paid_at = datetime.now()
            payment.payment_metadata = json.dumps(tx_info)
            self.db.commit()
            
            # 释放钱包
            wallet = self.db.query(USDTWallet).filter(
                USDTWallet.address == payment.wallet_address
            ).first()
            if wallet:
                self.release_wallet(wallet.id)
            
            return {
                "status": "success",
                "tx_hash": tx_info["tx_hash"],
                "amount": tx_info["amount"]
            }
        
        # 计算剩余时间
        remaining_seconds = 0
        if payment.expires_at:
            remaining = payment.expires_at - datetime.now()
            remaining_seconds = max(0, int(remaining.total_seconds()))
        
        return {
            "status": "pending",
            "remaining_seconds": remaining_seconds
        }


async def check_all_pending_payments():
    """定时任务：检查所有待支付的USDT订单"""
    from config.database import SessionLocal
    
    db = SessionLocal()
    try:
        # 查找所有待支付的USDT订单
        pending_payments = db.query(Payment).filter(
            and_(
                Payment.status == "pending",
                Payment.payment_method.in_(["usdt_trc20", "usdt_erc20"]),
                Payment.expires_at > datetime.now()
            )
        ).all()
        
        usdt_payment = USDTPayment(db)
        confirmed_count = 0
        
        for payment in pending_payments:
            result = await usdt_payment.check_payment_status(payment.id)
            if result.get("status") == "success":
                confirmed_count += 1
                print(f"Payment {payment.id} confirmed: {result.get('tx_hash')}")
        
        return {
            "checked": len(pending_payments),
            "confirmed": confirmed_count
        }
    
    finally:
        db.close()
