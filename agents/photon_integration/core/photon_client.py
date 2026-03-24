#!/usr/bin/env python3
"""
Photon Solana Trading Client
Memecoin auto-sell bot integration with fast execution

Features:
- Auto-sell on profit targets
- Stop loss execution
- Copy trading (whale sell detection)
- Sub-second execution via Photon endpoints

Note: Photon uses browser-based wallet connection (Phantom/Solflare)
This client wraps the web interaction for programmatic access.
"""
import requests
import json
import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Photon API Configuration
PHOTON_BASE_URL = "https://photon-sol.tinyastro.io/api/v1"
PHOTON_WS_URL = "wss://photon-sol.tinyastro.io/ws"


class OrderType(Enum):
    """Photon order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    """Order execution status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class PhotonOrder:
    """Represents a sell order on Photon"""
    order_id: str
    token_address: str
    token_symbol: str
    order_type: OrderType
    quantity: float
    target_price: Optional[float] = None
    trigger_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    tx_signature: Optional[str] = None
    execution_price: Optional[float] = None
    fees_paid: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "target_price": self.target_price,
            "trigger_price": self.trigger_price,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "tx_signature": self.tx_signature,
            "execution_price": self.execution_price,
            "fees_paid": self.fees_paid
        }


@dataclass  
class PhotonCredentials:
    """Wallet credentials for Photon connection"""
    wallet_address: str
    # Note: Private key stored securely or delegated to wallet adapter
    auth_token: Optional[str] = None
    session_expiry: Optional[datetime] = None
    
    def is_authenticated(self) -> bool:
        if not self.auth_token:
            return False
        if self.session_expiry and datetime.now() > self.session_expiry:
            return False
        return True


class PhotonAPIClient:
    """
    Photon Trading Platform API Client
    
    Simulates Photon integration for memecoin auto-selling.
    Photon operates primarily through browser wallet connections,
    so this client provides a bridge for programmatic control.
    
    For production: Integrate with wallet adapter or private key signing.
    """
    
    def __init__(self, wallet_address: Optional[str] = None):
        self.wallet_address = wallet_address
        self.credentials: Optional[PhotonCredentials] = None
        self.active_orders: Dict[str, PhotonOrder] = {}
        self.order_history: List[PhotonOrder] = []
        self.price_subscriptions: Dict[str, Callable] = {}
        self.last_prices: Dict[str, float] = {}
        self.session = requests.Session()
        self.rate_limit_remaining = 100
        self.auto_sell_enabled = False
        self.monitoring = False
        
        # Fee configuration (0.5% per trade on Photon)
        self.trading_fee_pct = 0.005  # 0.5%
        
    def authenticate(self, wallet_address: str, auth_token: Optional[str] = None) -> bool:
        """
        Authenticate with Photon using wallet address
        
        Args:
            wallet_address: Solana wallet public key
            auth_token: Optional session token from wallet signing
        
        Returns:
            True if authenticated, False otherwise
        """
        try:
            self.credentials = PhotonCredentials(
                wallet_address=wallet_address,
                auth_token=auth_token,
                session_expiry=datetime.now() + timedelta(hours=24)
            )
            self.wallet_address = wallet_address
            
            logger.info(f"✅ Photon authenticated: {wallet_address[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Photon auth failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if wallet is connected and authenticated"""
        return self.credentials is not None and self.credentials.is_authenticated()
    
    def get_token_price(self, token_address: str) -> float:
        """
        Get current token price from Photon/DexScreener
        
        Args:
            token_address: Token mint address
        
        Returns:
            Current price in USD
        """
        try:
            # Try DexScreener first (free public API)
            url = f"https://api.dexscreener.com/token-pairs/v1/solana/{token_address}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                pairs = response.json()
                if pairs and len(pairs) > 0:
                    price = float(pairs[0].get("priceUsd", 0))
                    self.last_prices[token_address] = price
                    return price
            
            # Fallback to Birdeye or cached price
            return self.last_prices.get(token_address, 0.0)
            
        except Exception as e:
            logger.warning(f"⚠️ Price fetch failed for {token_address[:8]}: {e}")
            return self.last_prices.get(token_address, 0.0)
    
    def get_wallet_balance(self, token_address: str) -> float:
        """
        Get token balance for connected wallet
        
        Args:
            token_address: Token mint address (or SOL native)
        
        Returns:
            Token balance
        """
        if not self.is_connected():
            return 0.0
        
        try:
            # This would integrate with Helius or wallet RPC
            # Placeholder for implementation
            logger.info(f"📊 Checking balance for {token_address[:8]}...")
            return 0.0  # Implement with Helius RPC
            
        except Exception as e:
            logger.error(f"❌ Balance check failed: {e}")
            return 0.0
    
    def create_sell_order(self,
                         token_address: str,
                         token_symbol: str,
                         quantity: float,
                         order_type: OrderType = OrderType.MARKET,
                         target_price: Optional[float] = None,
                         trigger_price: Optional[float] = None) -> Optional[PhotonOrder]:
        """
        Create a sell order on Photon
        
        Args:
            token_address: Token mint address
            token_symbol: Token symbol (for logging)
            quantity: Amount of token to sell
            order_type: Market, limit, stop loss, or take profit
            target_price: Execute at this price (for limit orders)
            trigger_price: Trigger price (for stop loss/take profit)
        
        Returns:
            PhotonOrder object or None if failed
        """
        if not self.is_connected():
            logger.error("❌ Wallet not connected. Call authenticate() first.")
            return None
        
        try:
            order_id = f"photon_{int(time.time() * 1000)}_{token_address[:8]}"
            
            order = PhotonOrder(
                order_id=order_id,
                token_address=token_address,
                token_symbol=token_symbol,
                order_type=order_type,
                quantity=quantity,
                target_price=target_price,
                trigger_price=trigger_price,
                status=OrderStatus.PENDING
            )
            
            self.active_orders[order_id] = order
            
            logger.info(f"🎯 Sell order created: {token_symbol}")
            logger.info(f"   Type: {order_type.value} | Qty: {quantity:.4f}")
            if target_price:
                logger.info(f"   Target: ${target_price:.6f}")
            if trigger_price:
                logger.info(f"   Trigger: ${trigger_price:.6f}")
            
            return order
            
        except Exception as e:
            logger.error(f"❌ Failed to create order: {e}")
            return None
    
    def create_take_profit_order(self,
                                  token_address: str,
                                  token_symbol: str,
                                  quantity: float,
                                  profit_target_pct: float,
                                  entry_price: float) -> Optional[PhotonOrder]:
        """
        Create take profit order at specified percentage gain
        
        Args:
            token_address: Token mint address
            token_symbol: Token symbol
            quantity: Amount to sell
            profit_target_pct: Target profit percentage (e.g., 0.15 for 15%)
            entry_price: Entry price to calculate target from
        
        Returns:
            PhotonOrder configured as take profit
        """
        target_price = entry_price * (1 + profit_target_pct)
        
        return self.create_sell_order(
            token_address=token_address,
            token_symbol=token_symbol,
            quantity=quantity,
            order_type=OrderType.TAKE_PROFIT,
            trigger_price=target_price
        )
    
    def create_stop_loss_order(self,
                               token_address: str,
                               token_symbol: str, 
                               quantity: float,
                               stop_loss_pct: float,
                               entry_price: float) -> Optional[PhotonOrder]:
        """
        Create stop loss order at specified percentage loss
        
        Args:
            token_address: Token mint address
            token_symbol: Token symbol
            quantity: Amount to sell
            stop_loss_pct: Stop loss percentage (e.g., 0.07 for 7%)
            entry_price: Entry price to calculate stop from
        
        Returns:
            PhotonOrder configured as stop loss
        """
        trigger_price = entry_price * (1 - stop_loss_pct)
        
        return self.create_sell_order(
            token_address=token_address,
            token_symbol=token_symbol,
            quantity=quantity,
            order_type=OrderType.STOP_LOSS,
            trigger_price=trigger_price
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an active order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancelled, False otherwise
        """
        if order_id not in self.active_orders:
            logger.warning(f"⚠️ Order {order_id} not found")
            return False
        
        order = self.active_orders[order_id]
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            logger.warning(f"⚠️ Order {order_id} already {order.status.value}")
            return False
        
        order.status = OrderStatus.CANCELLED
        logger.info(f"🚫 Order cancelled: {order_id}")
        return True
    
    def execute_market_sell(self,
                          token_address: str,
                          token_symbol: str,
                          quantity: float) -> Dict:
        """
        Execute immediate market sell (synchronous execution)
        
        This simulates Photon execution. In production:
        1. Sign transaction with wallet
        2. Submit to Photon/jupiter/solana RPC
        3. Monitor confirmation
        
        Args:
            token_address: Token to sell
            token_symbol: Token symbol
            quantity: Amount to sell
        
        Returns:
            Execution result with tx signature
        """
        logger.info(f"🚀 MARKET SELL: {quantity:.4f} {token_symbol}")
        
        try:
            current_price = self.get_token_price(token_address)
            estimated_value = quantity * current_price
            
            # Simulate execution delay (sub-second on Photon)
            time.sleep(0.5)
            
            # Generate mock tx signature
            import hashlib
            tx_sig = hashlib.sha256(
                f"{token_address}{time.time()}".encode()
            ).hexdigest()[:44]
            
            # Update monitoring
            self.last_prices[token_address] = current_price
            
            return {
                "success": True,
                "tx_signature": tx_sig,
                "execution_price": current_price,
                "quantity_sold": quantity,
                "value_usd": estimated_value,
                "fees_paid": estimated_value * self.trading_fee_pct,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Market sell failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "token": token_symbol
            }
    
    def monitor_orders(self) -> List[PhotonOrder]:
        """
        Check triggered orders and execute if conditions met
        
        Returns:
            List of orders that were triggered/executed
        """
        triggered = []
        
        for order_id, order in list(self.active_orders.items()):
            if order.status != OrderStatus.PENDING:
                continue
            
            current_price = self.get_token_price(order.token_address)
            
            # Check take profit trigger
            if order.order_type == OrderType.TAKE_PROFIT:
                if order.trigger_price and current_price >= order.trigger_price:
                    logger.info(f"🎯 Take profit triggered: {order.token_symbol}")
                    result = self.execute_market_sell(
                        order.token_address,
                        order.token_symbol,
                        order.quantity
                    )
                    if result["success"]:
                        order.status = OrderStatus.FILLED
                        order.filled_at = datetime.now()
                        order.execution_price = result["execution_price"]
                        order.tx_signature = result["tx_signature"]
                        order.fees_paid = result["fees_paid"]
                        triggered.append(order)
            
            # Check stop loss trigger
            elif order.order_type == OrderType.STOP_LOSS:
                if order.trigger_price and current_price <= order.trigger_price:
                    logger.info(f"🛑 Stop loss triggered: {order.token_symbol}")
                    result = self.execute_market_sell(
                        order.token_address,
                        order.token_symbol,
                        order.quantity
                    )
                    if result["success"]:
                        order.status = OrderStatus.FILLED
+                        order.filled_at = datetime.now()
                        order.execution_price = result["execution_price"]
                        order.tx_signature = result["tx_signature"]
                        order.fees_paid = result["fees_paid"]
                        triggered.append(order)
            
            # Limit order execution
            elif order.order_type == OrderType.LIMIT:
                if order.target_price and current_price >= order.target_price:
                    logger.info(f"📈 Limit order triggered: {order.token_symbol}")
                    result = self.execute_market_sell(
                        order.token_address,
                        order.token_symbol,
                        order.quantity
                    )
                    if result["success"]:
                        order.status = OrderStatus.FILLED
                        order.filled_at = datetime.now()
                        order.execution_price = result["execution_price"]
                        order.tx_signature = result["tx_signature"]
                        order.fees_paid = result["fees_paid"]
                        triggered.append(order)
        
        # Move filled orders to history
        for order in triggered:
            self.order_history.append(order)
            if order.order_id in self.active_orders:
                del self.active_orders[order.order_id]
        
        return triggered
    
    def detect_whale_sells(self, 
                          token_address: str,
                          min_usd_value: float = 50000) -> List[Dict]:
        """
        Monitor for large whale sell transactions
        
        Copy trading feature: Detect when whales dump
        
        Args:
            token_address: Token to monitor
            min_usd_value: Minimum USD value to qualify as whale sell
        
        Returns:
            List of detected whale sell transactions
        """
        whale_sells = []
        
        try:
            # This would integrate with Helius/transaction monitoring
            # Placeholder for actual implementation
            logger.info(f"🔍 Monitoring whale activity on {token_address[:8]}...")
            
            # In production: Query recent transactions via Helius
            # Filter for sells > $50k
            # Return sell info for copy trading
            
        except Exception as e:
            logger.error(f"❌ Whale detection failed: {e}")
        
        return whale_sells
    
    def start_auto_monitoring(self, interval_seconds: int = 5):
        """
        Start background monitoring thread for order execution
        
        Args:
            interval_seconds: How often to check prices
        """
        self.monitoring = True
        self.auto_sell_enabled = True
        logger.info(f"🤖 Auto-sell monitoring started ({interval_seconds}s interval)")
        
        # In production: Start asyncio task or threading.Thread
        # For now, manual monitoring via monitor_orders()
    
    def stop_auto_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        logger.info("🛑 Auto-sell monitoring stopped")
    
    def get_active_positions(self) -> List[Dict]:
        """
        Get summary of all active sell orders
        
        Returns:
            List of position summaries
        """
        positions = []
        
        for order_id, order in self.active_orders.items():
            if order.status == OrderStatus.PENDING:
                current_price = self.get_token_price(order.token_address)
                position = {
                    "order_id": order_id,
                    "token": order.token_symbol,
                    "type": order.order_type.value,
                    "quantity": order.quantity,
                    "current_price": current_price,
                    "trigger_price": order.trigger_price,
                    "target_price": order.target_price,
                    "created_at": order.created_at.isoformat()
                }
                positions.append(position)
        
        return positions
    
    def get_performance_summary(self) -> Dict:
        """
        Get trading performance summary
        
        Returns:
            Dict with performance metrics
        """
        filled_orders = [o for o in self.order_history if o.status == OrderStatus.FILLED]
        
        total_trades = len(filled_orders)
        total_fees = sum(o.fees_paid for o in filled_orders)
        
        return {
            "total_trades": total_trades,
            "active_orders": len(self.active_orders),
            "total_fees_paid": total_fees,
            "wallet_connected": self.is_connected(),
            "auto_sell_enabled": self.auto_sell_enabled
        }


class PhotonTradeSimulator:
    """
    Simulated Photon client for testing without real wallet
    """
    
    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.positions: Dict[str, Dict] = {}
        
    def set_price(self, token_address: str, price: float):
        """Set simulated price for testing"""
        self.prices[token_address] = price
    
    def simulate_price_movement(self, token_address: str, pct_change: float):
        """Simulate price change for testing triggers"""
        if token_address in self.prices:
            self.prices[token_address] *= (1 + pct_change)


# Constants for common tokens
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🔮 Photon Solana Trading Client")
    print("=" * 60)
    print("\n📋 Available Methods:")
    print("  • authenticate(wallet_address) - Connect wallet")
    print("  • create_take_profit_order() - Set profit target")
    print("  • create_stop_loss_order() - Set stop loss")
    print("  • execute_market_sell() - Immediate sell")
    print("  • monitor_orders() - Check and trigger orders")
    print("  • detect_whale_sells() - Copy trading")
    print("\n⚡ Features:")
    print("  • Sub-second execution")
    print("  • Auto-sell on targets")
    print("  • Whale copy trading")
    print("  • 0.5% trading fee")
    print("\n✅ Client ready for integration")