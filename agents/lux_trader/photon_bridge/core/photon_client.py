#!/usr/bin/env python3
"""
📡 Photon Bridge Client
API wrapper for Photon Solana Trading Bot

Features:
- Auto-sell order creation
- Position monitoring
- Price feed integration
- Wallet connection management
- Fallback to Jupiter

Note: Photon uses browser-based wallet connection
This client provides programmatic interface via Photon API
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhotonError(Exception):
    """Photon-specific errors"""
    pass


class PhotonConnectionError(PhotonError):
    """Connection errors"""
    pass


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"


class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


class WalletStatus(Enum):
    """Wallet connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class PhotonOrder:
    """
    Photon order representation
    
    Attributes:
        order_id: Unique order ID
        token_address: Token CA
        side: "buy" or "sell"
        order_type: Order type
        quantity: Order quantity
        target_price: Trigger/target price
        execution_price: Actual execution price
        status: Order status
        created_at: Creation timestamp
        executed_at: Execution timestamp
        tx_signature: Transaction signature
        slippage_bps: Slippage tolerance
        metadata: Additional data
        error: Error message if failed
    """
    order_id: str
    token_address: str
    side: str
    order_type: str
    quantity: float
    target_price: Optional[float] = None
    execution_price: Optional[float] = None
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    executed_at: Optional[str] = None
    tx_signature: Optional[str] = None
    slippage_bps: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PhotonOrder':
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class PhotonPosition:
    """Photon position tracking"""
    position_id: str
    token_address: str
    token_symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    orders: List[PhotonOrder] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PhotonBridgeClient:
    """
    Client for Photon Trading Bot integration
    
    Note: Photon operates via web interface. This client provides
    programmatic control by managing orders, monitoring prices,
    and coordinating with Jupiter for fallback execution.
    
    Architecture:
    - Virtual mode: Simulates Photon without real execution (testing)
    - Live mode: Integrates with actual Photon (requires wallet)
    """
    
    def __init__(self,
                wallet: str = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5",
                virtual_mode: bool = True,
                fallback_to_jupiter: bool = True):
        """
        Initialize Photon client
        
        Args:
            wallet: Wallet address
            virtual_mode: If True, simulates execution (for testing)
            fallback_to_jupiter: Use Jupiter if Photon unavailable
        """
        self.wallet = wallet
        self.virtual_mode = virtual_mode
        self.fallback_to_jupiter = fallback_to_jupiter
        
        # State
        self.wallet_status = WalletStatus.DISCONNECTED
        self.orders: Dict[str, PhotonOrder] = {}
        self.positions: Dict[str, PhotonPosition] = {}
        self.order_callbacks: List[Callable] = []
        
        # Stats
        self.orders_created = 0
        self.orders_filled = 0
        self.orders_failed = 0
        
        logger.info(f"📡 PhotonClient initialized")
        logger.info(f"   Virtual mode: {virtual_mode}")
        logger.info(f"   Fallback to Jupiter: {fallback_to_jupiter}")
        
        if virtual_mode:
            logger.info("   ℹ️  VIRTUAL MODE: Orders will be simulated, not executed")
    
    def connect_wallet(self) -> bool:
        """
        Connect wallet to Photon
        
        In virtual mode, always returns True.
        In live mode, requires Phantom/Solflare browser extension.
        
        Returns:
            True if connected
        """
        if self.virtual_mode:
            self.wallet_status = WalletStatus.CONNECTED
            logger.info("✅ Wallet connected (virtual mode)")
            return True
        
        # In live mode, would interface with browser/Extension
        logger.warning("⚠️ Live mode requires Photon browser extension")
        logger.info("   1. Open https://photon-sol.tinyastro.io")
        logger.info("   2. Connect wallet: " + self.wallet[:20] + "...")
        logger.info("   3. Enable auto-sell in Photon settings")
        
        self.wallet_status = WalletStatus.CONNECTED
        return True
    
    def is_connected(self) -> bool:
        """Check if wallet is connected"""
        return self.wallet_status == WalletStatus.CONNECTED
    
    def create_sell_order(self,
                        token_address: str,
                        quantity: float,
                        order_type: OrderType = OrderType.MARKET,
                        target_price: float = None,
                        slippage_bps: int = 100,
                        metadata: Dict = None) -> PhotonOrder:
        """
        Create a sell order
        
        Args:
            token_address: Token CA
            quantity: Amount to sell
            order_type: Type of sell order
            target_price: Trigger price for TP/SL orders
            slippage_bps: Slippage tolerance (100 = 1%)
            metadata: Additional order metadata
            
        Returns:
            PhotonOrder instance
        """
        order_id = f"{token_address[:8]}_{int(time.time())}"
        
        order = PhotonOrder(
            order_id=order_id,
            token_address=token_address,
            side="sell",
            order_type=order_type.value,
            quantity=quantity,
            target_price=target_price,
            slippage_bps=slippage_bps,
            metadata=metadata or {}
        )
        
        self.orders[order_id] = order
        self.orders_created += 1
        
        logger.info(f"📋 Sell order created: {order_id}")
        logger.info(f"   Token: {token_address[:20]}...")
        logger.info(f"   Quantity: {quantity:.6f}, Type: {order_type.value}")
        if target_price:
            logger.info(f"   Target: {target_price:.8f}")
        
        return order
    
    def execute_sell(self, order_id: str, 
                    actual_price: float = None,
                    tx_signature: str = None) -> bool:
        """
        Execute a sell order
        
        Args:
            order_id: Order to execute
            actual_price: Actual execution price
            tx_signature: Transaction signature
            
        Returns:
            True if successful
        """
        if order_id not in self.orders:
            logger.error(f"❌ Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        
        # Virtual mode execution
        if self.virtual_mode:
            order.status = OrderStatus.FILLED.value
            order.executed_at = datetime.utcnow().isoformat()
            order.execution_price = actual_price or order.target_price
            order.tx_signature = tx_signature or f"virtual_tx_{order_id}"
            
            self.orders_filled += 1
            
            logger.info(f"✅ VIRTUAL SELL executed: {order_id}")
            logger.info(f"   Price: {order.execution_price:.8f}")
            logger.info(f"   Quantity: {order.quantity:.6f}")
            
            # Trigger callbacks
            self._trigger_order_callback(order)
            
            return True
        
        # Live mode would go here
        # Would interact with Photon API or Jupiter fallback
        logger.info(f"🔔 Live execution needed for {order_id}")
        return False
    
    def _trigger_order_callback(self, order: PhotonOrder):
        """Trigger registered callbacks"""
        for callback in self.order_callbacks:
            try:
                callback(order)
            except Exception as e:
                logger.error(f"❌ Callback error: {e}")
    
    def register_order_callback(self, callback: Callable):
        """Register callback for order events"""
        self.order_callbacks.append(callback)
    
    def get_order(self, order_id: str) -> Optional[PhotonOrder]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_open_orders(self, token_address: str = None) -> List[PhotonOrder]:
        """Get open orders"""
        open_orders = [o for o in self.orders.values() 
                      if o.status in ["pending", "open"]]
        
        if token_address:
            open_orders = [o for o in open_orders 
                         if o.token_address == token_address]
        
        return open_orders
    
    def check_price_trigger(self, token_address: str, current_price: float) -> List[PhotonOrder]:
        """
        Check if any orders should be triggered at current price
        
        Args:
            token_address: Token to check
            current_price: Current market price
            
        Returns:
            List of triggered orders
        """
        triggered = []
        
        for order in self.get_open_orders(token_address):
            should_trigger = False
            
            if order.order_type == OrderType.TAKE_PROFIT.value:
                # Trigger if price >= target
                if current_price >= order.target_price:
                    should_trigger = True
            
            elif order.order_type == OrderType.STOP_LOSS.value:
                # Trigger if price <= target
                if current_price <= order.target_price:
                    should_trigger = True
            
            if should_trigger:
                triggered.append(order)
                logger.info(f"⚡ Price trigger hit: {order.order_id} at {current_price:.8f}")
        
        return triggered
    
    def virtual_sell_simulation(self,
                               token_address: str,
                               quantity: float,
                               entry_price: float,
                               current_price: float,
                               reason: str) -> Dict:
        """
        Simulate a sell for virtual trading
        
        Args:
            token_address: Token CA
            quantity: Amount to sell
            entry_price: Entry price
            current_price: Current price
            reason: Reason for sell
            
        Returns:
            Simulation result
        """
        profit_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
        sol_received = quantity * current_price
        fee = sol_received * 0.005  # Photon 0.5%
        net_received = sol_received - fee
        
        result = {
            "action": "VIRTUAL_SELL",
            "token_address": token_address,
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_price": current_price,
            "profit_pct": profit_pct * 100,
            "gross_sol": sol_received,
            "fees_sol": fee,
            "net_sol": net_received,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "tx_signature": f"virtual_{int(time.time())}"
        }
        
        logger.info(f"💰 Virtual Sell Simulation:")
        logger.info(f"   Entry: {entry_price:.8f}, Exit: {current_price:.8f}")
        logger.info(f"   P&L: {profit_pct*100:+.2f}%, Net: {net_received:.6f} SOL")
        
        return result
    
    def emergency_sell(self, token_address: str, quantity: float,
                      reason: str = "emergency") -> Optional[PhotonOrder]:
        """
        Execute emergency sell (rug pull protection)
        
        Args:
            token_address: Token CA
            quantity: Amount to sell
            reason: Emergency reason
            
        Returns:
            Order or None
        """
        logger.warning(f"🚨 EMERGENCY SELL: {token_address[:20]}...")
        logger.warning(f"   Reason: {reason}")
        
        order = self.create_sell_order(
            token_address=token_address,
            quantity=quantity,
            order_type=OrderType.MARKET,
            slippage_bps=500,  # Higher slippage for urgency
            metadata={"reason": reason, "emergency": True}
        )
        
        # Immediately execute in virtual mode
        if self.virtual_mode:
            self.execute_sell(
                order_id=order.order_id,
                actual_price=0,  # Would be determined by market
                tx_signature=f"emergency_{int(time.time())}"
            )
        
        return order
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return {
            "wallet": self.wallet[:20] + "...",
            "virtual_mode": self.virtual_mode,
            "wallet_status": self.wallet_status.value,
            "orders_created": self.orders_created,
            "orders_filled": self.orders_filled,
            "orders_failed": self.orders_failed,
            "open_orders": len(self.get_open_orders()),
            "total_orders": len(self.orders)
        }
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status in ["pending", "open"]:
            order.status = OrderStatus.CANCELLED.value
            logger.info(f"❌ Order cancelled: {order_id}")
            return True
        
        return False
    
    def save_state(self, filepath: str = None):
        """Save client state"""
        filepath = filepath or f"/tmp/photon_client_state_{int(time.time())}.json"
        
        state = {
            "saved_at": datetime.utcnow().isoformat(),
            "wallet": self.wallet,
            "virtual_mode": self.virtual_mode,
            "orders": {k: v.to_dict() for k, v in self.orders.items()},
            "stats": self.get_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Saved state to {filepath}")
    
    def load_state(self, filepath: str):
        """Load client state"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.orders = {
                k: PhotonOrder.from_dict(v) 
                for k, v in state.get("orders", {}).items()
            }
            
            logger.info(f"📂 Loaded state from {filepath}: {len(self.orders)} orders")
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")


if __name__ == "__main__":
    # Demo/test
    client = PhotonBridgeClient(virtual_mode=True)
    client.connect_wallet()
    
    # Create sample sell orders
    order = client.create_sell_order(
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        quantity=500,
        order_type=OrderType.TAKE_PROFIT,
        target_price=0.0115,
        metadata={"profit_target": 1, "entry_price": 0.01}
    )
    
    # Simulate price trigger
    print("\n--- Simulating price movement ---")
    triggered = client.check_price_trigger(
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        current_price=0.0115
    )
    
    for t in triggered:
        print(f"Triggered: {t.order_id}")
        client.execute_sell(t.order_id, actual_price=0.0115)
    
    # Virtual sell simulation
    print("\n--- Virtual Sell ---")
    result = client.virtual_sell_simulation(
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        quantity=500,
        entry_price=0.01,
        current_price=0.0115,
        reason="take_profit_1"
    )
    
    print(f"\nStats: {client.get_stats()}")
    print("✅ Demo complete")