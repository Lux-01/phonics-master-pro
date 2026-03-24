#!/usr/bin/env python3
"""
🔄 Photon Bridge Position Sync
Synchronizes LuxTrader positions with Photon auto-sell system

Features:
- Auto-load positions from LuxTrader
- Sync position state between systems
- Handle position updates
- Track partial fills
- Integration with sell rule engine

Author: LuxTrader Photon Bridge v1.0
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Position synchronization status"""
    PENDING = "pending"         # New position, awaiting sync
    SYNCED = "synced"          # Successfully synced with Photon
    FAILED = "failed"          # Sync failed
    UPDATED = "updated"         # Position updated
    CLOSED = "closed"          # Position closed
    ERROR = "error"            # Error state


class PositionState(Enum):
        """Lifecycle states"""
        PENDING = "pending"
        OPEN = "open"
        PARTIAL_EXIT = "partial_exit"
        CLOSED = "closed"


@dataclass
class PositionData:
    """
    Unified position data structure
    
    Attributes:
        position_id: Unique identifier
        token_address: Solana token CA
        token_symbol: Token symbol
        token_name: Token name (if known)
        entry_price: Entry price in SOL/USD
        current_price: Current market price
        quantity: Token quantity held
        quantity_sold: Total quantity sold
        quantity_remaining: Remaining quantity
        entry_time: ISO timestamp
        exit_time: ISO timestamp (if closed)
        buy_tx: Buy transaction signature
        sell_txs: List of sell transaction signatures
        pnl_pct: Current/profit percentage
        realized_pnl: Realized profit/loss
        unrealized_pnl: Unrealized profit/loss
        grade: Scanner grade (A+, A, etc.)
        stage: Trading stage (9 or 10)
        status: Current status
        sync_status: Synchronization status
        sell_rules: Associated sell rules
        metadata: Additional position data
    """
    position_id: str
    token_address: str
    token_symbol: str = "UNKNOWN"
    token_name: str = ""
    entry_price: float = 0.0
    current_price: float = 0.0
    quantity: float = 0.0
    quantity_sold: float = 0.0
    quantity_remaining: float = 0.0
    entry_time: str = ""
    exit_time: Optional[str] = None
    buy_tx: Optional[str] = None
    sell_txs: List[str] = field(default_factory=list)
    pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    grade: str = "A"
    stage: int = 9
    status: str = "pending"
    sync_status: str = "pending"
    sell_rules: Dict = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.quantity_remaining:
            self.quantity_remaining = self.quantity - self.quantity_sold
        if self.entry_time and not self.position_id:
            self.position_id = f"{self.token_address[:8]}_{self.entry_time[:10]}"
        self._update_pnl()
    
    def _update_pnl(self):
        """Recalculate P&L values"""
        if self.entry_price > 0:
            self.pnl_pct = (self.current_price - self.entry_price) / self.entry_price
            self.unrealized_pnl = self.quantity_remaining * (self.current_price - self.entry_price)
            self.realized_pnl = self.quantity_sold * (sum(self.sell_txs) / max(len(self.sell_txs), 1) - self.entry_price) if self.sell_txs else 0.0
    
    def update_price(self, new_price: float):
        """Update current price and recalculate P&L"""
        self.current_price = new_price
        self._update_pnl()
    
    def record_sell(self, quantity: float, price: float, tx: str):
        """Record a partial or full sell"""
        self.quantity_sold += quantity
        self.quantity_remaining = self.quantity - self.quantity_sold
        self.sell_txs.append(tx)
        
        if self.quantity_remaining <= 0.000001:  # Dust threshold
            self.status = "closed"
            self.exit_time = datetime.utcnow().isoformat()
        else:
            self.status = "partial_exit"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PositionData':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class PositionSynchronizer:
    """
    Synchronizes LuxTrader positions with Photon system
    
    Responsibilities:
    - Load positions from various sources (LuxTrader JSON, Photon API)
    - Sync state between systems
    - Handle position lifecycle events
    - Maintain unified position view
    - Integrate with sell rule engine
    """
    
    def __init__(self, 
                rule_engine,
                execution_logger,
                wallet: str = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"):
        """
        Initialize position synchronizer
        
        Args:
            rule_engine: SellRuleEngine instance
            execution_logger: ExecutionLogger instance
            wallet: Wallet address
        """
        self.wallet = wallet
        self.rule_engine = rule_engine
        self.execution_logger = execution_logger
        
        # Data stores
        self.positions: Dict[str, PositionData] = {}
        self.sync_queue: List[PositionData] = []
        
        # Sources
        self.lux_trader_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/tracked_positions.json")
        self.lux_state_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/live_state.json")
        self.skylar_file = Path("/home/skux/.openclaw/workspace/agents/skylar/skylar_exit_tracker.json")
        
        logger.info(f"🔄 PositionSynchronizer initialized")
    
    def load_from_lux_trader(self) -> List[PositionData]:
        """
        Load positions from LuxTrader tracked_positions.json
        
        Returns:
            List of PositionData
        """
        new_positions = []
        
        try:
            with open(self.lux_trader_file, 'r') as f:
                data = json.load(f)
            
            for pos in data.get("positions", []):
                position_data = PositionData(
                    position_id=f"{pos['address'][:8]}_{pos.get('entry_time', 'unknown')[:10]}",
                    token_address=pos["address"],
                    token_symbol=pos.get("token", "UNKNOWN"),
                    entry_price=pos.get("entry_sol", 0.0) / pos.get("initial_quantity", 1.0) if pos.get("initial_quantity") else pos.get("entry_sol", 0.0),
                    quantity=pos.get("initial_quantity", 0.0),
                    quantity_sold=pos.get("quantity_sold", 0.0),
                    entry_time=pos.get("entry_time", ""),
                    buy_tx=pos.get("solscan", "").split("/")[-1] if pos.get("solscan") else None,
                    grade=pos.get("grade", "A"),
                    status="open" if pos.get("quantity_sold", 0) < pos.get("initial_quantity", 1) else "closed"
                )
                
                # Check if already synced
                if position_data.position_id not in self.positions:
                    self.positions[position_data.position_id] = position_data
                    new_positions.append(position_data)
                    logger.info(f"📥 Loaded position: {position_data.token_symbol} ({position_data.position_id})")
            
            logger.info(f"✅ Loaded {len(new_positions)} new positions from LuxTrader")
            
        except FileNotFoundError:
            logger.warning(f"⚠️ LuxTrader tracked_positions.json not found")
        except Exception as e:
            logger.error(f"❌ Error loading LuxTrader positions: {e}")
        
        return new_positions
    
    def load_from_skylar(self) -> List[PositionData]:
        """
        Load positions from Skylar exit tracker
        
        Returns:
            List of PositionData
        """
        new_positions = []
        
        try:
            with open(self.skylar_file, 'r') as f:
                data = json.load(f)
            
            for pos in data.get("positions", []):
                position_data = PositionData(
                    position_id=f"{pos['address'][:8]}_{pos.get('entry_time', 'unknown')[:10]}",
                    token_address=pos["address"],
                    token_symbol=pos.get("token", "UNKNOWN"),
                    entry_price=pos.get("entry_sol", 0.01),
                    quantity=0.01 / pos.get("entry_sol", 0.01) if pos.get("entry_sol") else 1000,
                    entry_time=pos.get("entry_time", ""),
                    buy_tx=pos.get("solscan", "").split("/")[-1] if pos.get("solscan") else None,
                    status="open"
                )
                
                if position_data.position_id not in self.positions:
                    self.positions[position_data.position_id] = position_data
                    new_positions.append(position_data)
                    logger.info(f"📥 Loaded Skylar position: {position_data.token_symbol}")
            
            logger.info(f"✅ Loaded {len(new_positions)} positions from Skylar")
            
        except FileNotFoundError:
            logger.warning(f"⚠️ Skylar exit tracker not found")
        except Exception as e:
            logger.error(f"❌ Error loading Skylar positions: {e}")
        
        return new_positions
    
    def sync_new_position(self, 
                        token_address: str,
                        token_symbol: str,
                        entry_price: float,
                        quantity: float,
                        tx_signature: str,
                        grade: str = "A",
                        stage: int = 9) -> PositionData:
        """
        Sync a new position from LuxTrader buy execution
        
        Args:
            token_address: Token CA
            token_symbol: Token symbol
            entry_price: Entry price
            quantity: Token quantity
            tx_signature: Buy transaction signature
            grade: Token grade
            stage: Trading stage
            
        Returns:
            PositionData
        """
        entry_time = datetime.utcnow().isoformat()
        position_id = f"{token_address[:8]}_{entry_time[:10]}_{entry_time[11:13]}"
        
        # Create position data
        position = PositionData(
            position_id=position_id,
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=entry_time,
            buy_tx=tx_signature,
            grade=grade,
            stage=stage,
            status="open",
            sync_status="synced"
        )
        
        # Add to tracking
        self.positions[position_id] = position
        
        # Create sell rules in rule engine
        self.rule_engine.create_rules_for_position(
            position_id=position_id,
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            stage=stage
        )
        
        # Log buy execution
        self.execution_logger.log_buy_executed(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            quantity=quantity,
            tx_signature=tx_signature,
            stage=stage,
            metadata={"grade": grade, "position_id": position_id}
        )
        
        logger.info(f"✅ Synced new position: {token_symbol} at {entry_price:.6f}")
        
        return position
    
    def sync_sell_execution(self,
                         position_id: str,
                         sell_quantity: float,
                         sell_price: float,
                         tx_signature: str,
                         reason: str) -> bool:
        """
        Sync a sell execution with position data
        
        Args:
            position_id: Position identifier
            sell_quantity: Quantity sold
            sell_price: Sale price
            tx_signature: Sell transaction signature
            reason: Reason for sell (e.g., "take_profit_1")
            
        Returns:
            True if successful
        """
        if position_id not in self.positions:
            logger.warning(f"⚠️ Position {position_id} not found for sell sync")
            return False
        
        position = self.positions[position_id]
        
        # Update position
        position.record_sell(sell_quantity, sell_price, tx_signature)
        
        # Calculate P&L
        profit_pct = (sell_price - position.entry_price) / position.entry_price if position.entry_price > 0 else 0
        sol_received = sell_quantity * sell_price
        
        # Log sell
        self.execution_logger.log_sell_executed(
            token_address=position.token_address,
            token_symbol=position.token_symbol,
            entry_price=position.entry_price,
            exit_price=sell_price,
            quantity=sell_quantity,
            sol_received=sol_received,
            fees_paid=sol_received * 0.005,  # Photon 0.5% fee
            tx_signature=tx_signature,
            reason=reason,
            stage=position.stage
        )
        
        logger.info(f"✅ Synced sell: {sell_quantity:.4f} {position.token_symbol} at {sell_price:.6f} ({reason})")
        
        # If fully closed, mark in rule engine
        if position.status == "closed":
            self.rule_engine.remove_position(position_id)
            position.sync_status = "closed"
            logger.info(f"🏁 Position fully closed: {position_id}")
        
        return True
    
    def update_prices(self, price_data: Dict[str, float]) -> List[Tuple[str, Any]]:
        """
        Update prices for all positions and evaluate rules
        
        Args:
            price_data: Dict of token_address -> price
            
        Returns:
            List of triggered rules with position IDs
        """
        triggered = []
        
        for position_id, position in self.positions.items():
            if position.status not in ["open", "partial_exit"]:
                continue
            
            # Get price for this token
            price = price_data.get(position.token_address, position.current_price)
            
            if price != position.current_price:
                # Update position price
                position.update_price(price)
                
                # Update rule engine
                rules_triggered = self.rule_engine.update_price(position_id, price)
                
                for rule in rules_triggered:
                    triggered.append((position_id, rule))
        
        return triggered
    
    def get_open_positions(self) -> List[PositionData]:
        """Get all open positions"""
        return [p for p in self.positions.values() 
                if p.status in ["open", "partial_exit"]]
    
    def get_position(self, position_id: str) -> Optional[PositionData]:
        """Get a specific position"""
        return self.positions.get(position_id)
    
    def get_position_by_token(self, token_address: str) -> Optional[PositionData]:
        """Find position by token address"""
        for pos in self.positions.values():
            if pos.token_address == token_address:
                return pos
        return None
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        open_positions = self.get_open_positions()
        closed_positions = [p for p in self.positions.values() if p.status == "closed"]
        
        total_realized = sum(p.realized_pnl for p in closed_positions)
        total_unrealized = sum(p.unrealized_pnl for p in open_positions)
        total_invested = sum(p.entry_price * p.quantity for p in self.positions.values())
        
        return {
            "open_positions": len(open_positions),
            "closed_positions": len(closed_positions),
            "total_positions": len(self.positions),
            "total_invested_sol": total_invested,
            "total_realized_pnl": total_realized,
            "total_unrealized_pnl": total_unrealized,
            "total_pnl": total_realized + total_unrealized,
            "avg_pnl_pct": sum(p.pnl_pct for p in open_positions) / len(open_positions) if open_positions else 0,
            "positions": [p.to_dict() for p in open_positions]
        }
    
    def export_positions(self, filepath: str = None) -> str:
        """Export all positions to JSON"""
        filepath = filepath or f"/home/skux/.openclaw/workspace/logs/photon_bridge/positions_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "wallet": self.wallet,
            "positions_count": len(self.positions),
            "positions": {k: v.to_dict() for k, v in self.positions.items()}
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"💾 Exported {len(self.positions)} positions to {filepath}")
        return filepath
    
    def sync_all_sources(self) -> int:
        """
        Sync positions from all sources
        
        Returns:
            Total new positions loaded
        """
        total = 0
        total += len(self.load_from_lux_trader())
        total += len(self.load_from_skylar())
        
        logger.info(f"✅ Sync complete: {total} new positions from all sources")
        return total


if __name__ == "__main__":
    # Demo/test - requires rule_engine and logger
    print("🔄 Position Synchronizer module loaded")
    print("   Use with SellRuleEngine and ExecutionLogger for full functionality")