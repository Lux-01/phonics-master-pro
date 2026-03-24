#!/usr/bin/env python3
"""
Position Manager - Track and Monitor Open Trading Positions

Manages:
- Open position tracking
- Portfolio performance
- Position sizing
- Risk management
- P&L calculations
- Historical trade logging

Integrates with:
- Photon client (execution)
- Sell rule engine (auto-sell triggers)
- v54 scanner (entry signals)
- Jupiter client (backup execution)
"""
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Position lifecycle states"""
    PENDING = "pending"           # Entry confirmed, waiting for fill
    OPEN = "open"                  # Active position
    PARTIAL_EXIT = "partial_exit"  # Some sold, some remaining
    CLOSED = "closed"              # Fully exited
    CANCELLED = "cancelled"        # Entry cancelled
    FAILED = "failed"              # Entry/exit failed


class TradeSide(Enum):
    """Buy or sell"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Trade:
    """
    Individual trade execution record
    """
    trade_id: str
    token_address: str
    token_symbol: str
    side: TradeSide
    quantity: float
    price: float
    timestamp: datetime
    value_usd: float = 0.0
    fees_paid: float = 0.0
    tx_signature: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    reason: str = ""  # e.g., "take_profit", "stop_loss"
    
    def __post_init__(self):
        if self.value_usd == 0.0:
            self.value_usd = self.quantity * self.price
    
    def to_dict(self) -> Dict:
        return {
            "trade_id": self.trade_id,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
            "value_usd": self.value_usd,
            "fees_paid": self.fees_paid,
            "tx_signature": self.tx_signature,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error,
            "reason": self.reason
        }


@dataclass
class Position:
    """
    Complete position with entry, exits, and P&L tracking
    
    Tracks:
    - Entry details
    - Multiple partial exits
    - Realized and unrealized P&L
    - Trade history per position
    - Risk metrics
    """
    position_id: str
    token_address: str
    token_symbol: str
    entry_price: float
    initial_quantity: float
    entry_time: datetime
    scanner_grade: str = ""           # v54 scanner grade (A+, A, etc.)
    scanner_score: int = 0            # Raw score from scanner
    
    # Current state
    quantity_remaining: float = 0.0
    avg_exit_price: float = 0.0
    status: PositionStatus = PositionStatus.PENDING
    
    # Tracking
    trades: List[Trade] = field(default_factory=list)
    highest_price: float = 0.0
    lowest_price: float = float('inf')
    exit_time: Optional[datetime] = None
    
    # Targets from rule engine
    take_profit_1_price: Optional[float] = None
    take_profit_2_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    time_limit: Optional[datetime] = None
    
    # Metadata
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.quantity_remaining == 0.0:
            self.quantity_remaining = self.initial_quantity
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price
        if self.lowest_price == float('inf'):
            self.lowest_price = self.entry_price
    
    @property
    def initial_value(self) -> float:
        """Initial position value in USD"""
        return self.initial_quantity * self.entry_price
    
    @property
    def realized_pnl(self) -> float:
        """Realized P&L from completed sells"""
        total_sell_value = sum(
            t.value_usd for t in self.trades 
            if t.side == TradeSide.SELL and t.success
        )
        total_sell_qty = sum(
            t.quantity for t in self.trades 
            if t.side == TradeSide.SELL and t.success
        )
        cost_basis = total_sell_qty * self.entry_price
        return total_sell_value - cost_basis - sum(t.fees_paid for t in self.trades)
    
    def unrealized_pnl(self, current_price: float) -> float:
        """Unrealized P&L on remaining position"""
        if self.quantity_remaining <= 0:
            return 0.0
        value_now = self.quantity_remaining * current_price
        cost_basis = self.quantity_remaining * self.entry_price
        return value_now - cost_basis
    
    def total_pnl(self, current_price: float) -> float:
        """Total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl(current_price)
    
    def pnl_pct(self, current_price: float) -> float:
        """Total P&L percentage"""
        if self.initial_value == 0:
            return 0.0
        return self.total_pnl(current_price) / self.initial_value
    
    def add_trade(self, trade: Trade):
        """Add a trade to this position"""
        self.trades.append(trade)
        
        if trade.side == TradeSide.BUY and trade.success:
            # Initial entry
            self.status = PositionStatus.OPEN
            
        elif trade.side == TradeSide.SELL and trade.success:
            self.quantity_remaining -= trade.quantity
            
            if self.quantity_remaining <= 0:
                self.status = PositionStatus.CLOSED
                self.exit_time = trade.timestamp
                self.avg_exit_price = sum(t.value_usd for t in self.trades if t.side == TradeSide.SELL) / sum(t.quantity for t in self.trades if t.side == TradeSide.SELL)
            else:
                self.status = PositionStatus.PARTIAL_EXIT
    
    def update_price(self, current_price: float):
        """Update price tracking for metrics"""
        self.highest_price = max(self.highest_price, current_price)
        self.lowest_price = min(self.lowest_price, current_price)
    
    def is_expired(self) -> bool:
        """Check if position hit time limit"""
        if not self.time_limit:
            return False
        return datetime.now() > self.time_limit
    
    def get_hold_time_minutes(self) -> float:
        """Time since entry in minutes"""
        end = self.exit_time or datetime.now()
        return (end - self.entry_time).total_seconds() / 60
    
    def to_dict(self) -> Dict:
        return {
            "position_id": self.position_id,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "entry_price": self.entry_price,
            "initial_quantity": self.initial_quantity,
            "quantity_remaining": self.quantity_remaining,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "status": self.status.value,
            "scanner_grade": self.scanner_grade,
            "scanner_score": self.scanner_score,
            "realized_pnl": self.realized_pnl,
            "trades": [t.to_dict() for t in self.trades],
            "highest_price": self.highest_price,
            "lowest_price": self.lowest_price if self.lowest_price != float('inf') else self.entry_price,
            "time_limit": self.time_limit.isoformat() if self.time_limit else None,
            "tags": self.tags,
            "notes": self.notes
        }


class PositionManager:
    """
    Central manager for all trading positions
    
    Features:
    - Position lifecycle management
    - Portfolio-level analytics
    - Risk tracking
    - Performance reporting
    - Trade history
    """
    
    def __init__(self, storage_path: str = "data/positions.json"):
        self.storage_path = storage_path
        self.positions: Dict[str, Position] = {}  # token_address -> Position
        self.position_history: List[Position] = []
        self.daily_stats: Dict[str, Dict] = defaultdict(lambda: {
            "trades": 0,
            "pnl": 0.0,
            "winners": 0,
            "losers": 0
        })
        
        # Load existing positions
        self._load_positions()
    
    def _load_positions(self):
        """Load positions from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for pos_data in data.get("positions", []):
                    pos_id = pos_data["position_id"]
                    token = pos_data["token_address"]
                    # Reconstruct position
                    pos = self._dict_to_position(pos_data)
                    self.positions[token] = pos
            logger.info(f"✅ Loaded {len(self.positions)} positions from storage")
        except FileNotFoundError:
            logger.info("ℹ️ No position storage found, starting fresh")
        except Exception as e:
            logger.error(f"❌ Failed to load positions: {e}")
    
    def _save_positions(self):
        """Save positions to storage"""
        try:
            data = {
                "positions": [pos.to_dict() for pos in self.positions.values()],
                "history": [pos.to_dict() for pos in self.position_history[-100:]]  # Last 100 closed
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save positions: {e}")
    
    def _dict_to_position(self, data: Dict) -> Position:
        """Reconstruct Position from dict"""
        pos = Position(
            position_id=data["position_id"],
            token_address=data["token_address"],
            token_symbol=data["token_symbol"],
            entry_price=data["entry_price"],
            initial_quantity=data["initial_quantity"],
            entry_time=datetime.fromisoformat(data["entry_time"]),
            scanner_grade=data.get("scanner_grade", ""),
            scanner_score=data.get("scanner_score", 0),
            quantity_remaining=data.get("quantity_remaining", data["initial_quantity"]),
            status=PositionStatus(data.get("status", "open")),
            highest_price=data.get("highest_price", data["entry_price"]),
            lowest_price=data.get("lowest_price", data["entry_price"]),
            exit_time=datetime.fromisoformat(data["exit_time"]) if data.get("exit_time") else None,
            time_limit=datetime.fromisoformat(data["time_limit"]) if data.get("time_limit") else None,
            tags=data.get("tags", []),
            notes=data.get("notes", "")
        )
        
        # Rebuild trades
        for trade_data in data.get("trades", []):
            trade = Trade(
                trade_id=trade_data["trade_id"],
                token_address=trade_data["token_address"],
                token_symbol=trade_data["token_symbol"],
                side=TradeSide(trade_data["side"]),
                quantity=trade_data["quantity"],
                price=trade_data["price"],
                timestamp=datetime.fromisoformat(trade_data["timestamp"]),
                value_usd=trade_data.get("value_usd", 0),
                fees_paid=trade_data.get("fees_paid", 0),
                tx_signature=trade_data.get("tx_signature"),
                success=trade_data.get("success", True),
                error=trade_data.get("error"),
                reason=trade_data.get("reason", "")
            )
            pos.trades.append(trade)
        
        return pos
    
    def open_position(self,
                     token_address: str,
                     token_symbol: str,
                     entry_price: float,
                     quantity: float,
                     scanner_grade: str = "",
                     scanner_score: int = 0,
                     time_limit_hours: float = 4.0) -> Position:
        """
        Open a new trading position
        
        Args:
            token_address: Token mint
            token_symbol: Token symbol
            entry_price: Entry price USD
            quantity: Token quantity
            scanner_grade: v54 scanner grade
            scanner_score: raw scanner score
            time_limit_hours: Auto-exit after N hours
        
        Returns:
            New Position object
        """
        if token_address in self.positions and self.positions[token_address].status in [PositionStatus.OPEN, PositionStatus.PARTIAL_EXIT]:
            logger.warning(f"⚠️ Position already open for {token_symbol}")
            return self.positions[token_address]
        
        position_id = f"pos_{int(time.time() * 1000)}_{token_symbol[:6]}"
        
        position = Position(
            position_id=position_id,
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            initial_quantity=quantity,
            entry_time=datetime.now(),
            scanner_grade=scanner_grade,
            scanner_score=scanner_score,
            time_limit=datetime.now() + timedelta(hours=time_limit_hours)
        )
        
        # Create entry trade
        entry_trade = Trade(
            trade_id=f"{position_id}_entry",
            token_address=token_address,
            token_symbol=token_symbol,
            side=TradeSide.BUY,
            quantity=quantity,
            price=entry_price,
            timestamp=datetime.now(),
            success=True,
            reason="scanner_signal"
        )
        position.add_trade(entry_trade)
        
        self.positions[token_address] = position
        self._save_positions()
        
        logger.info(f"✅ Position opened: {token_symbol}")
        logger.info(f"   Entry: ${entry_price:.6f} | Qty: {quantity:.2f}")
        logger.info(f"   Grade: {scanner_grade} | Time limit: {time_limit_hours}h")
        
        return position
    
    def close_position(self,
                      token_address: str,
                      exit_price: float,
                      quantity: Optional[float] = None,
                      reason: str = "manual",
                      fees: float = 0.0) -> bool:
        """
        Close or partially close a position
        
        Args:
            token_address: Token mint
            exit_price: Exit price
            quantity: Amount to sell (None = full position)
            reason: Why closed (stop_loss, take_profit, etc.)
            fees: Trading fees paid
        
        Returns:
            True if successful
        """
        if token_address not in self.positions:
            logger.error(f"❌ Position not found: {token_address[:8]}")
            return False
        
        position = self.positions[token_address]
        
        if position.status in [PositionStatus.CLOSED, PositionStatus.CANCELLED]:
            logger.warning(f"⚠️ Position already closed: {position.token_symbol}")
            return False
        
        sell_qty = quantity or position.quantity_remaining
        
        trade = Trade(
            trade_id=f"{position.position_id}_exit_{int(time.time())}",
            token_address=token_address,
            token_symbol=position.token_symbol,
            side=TradeSide.SELL,
            quantity=sell_qty,
            price=exit_price,
            timestamp=datetime.now(),
            fees_paid=fees,
            success=True,
            reason=reason
        )
        
        position.add_trade(trade)
        
        # Update stats
        pnl = trade.value_usd - (sell_qty * position.entry_price) - fees
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["trades"] += 1
        self.daily_stats[today]["pnl"] += pnl
        if pnl > 0:
            self.daily_stats[today]["winners"] += 1
        else:
            self.daily_stats[today]["losers"] += 1
        
        self._save_positions()
        
        logger.info(f"{'🔴' if pnl < 0 else '🟢'} Position {reason}: {position.token_symbol}")
        logger.info(f"   Sold: {sell_qty:.2f} @ ${exit_price:.6f}")
        logger.info(f"   P&L: ${pnl:+.2f}")
        
        return True
    
    def update_price(self, token_address: str, current_price: float):
        """Update current price for a position"""
        if token_address in self.positions:
            self.positions[token_address].update_price(current_price)
    
    def get_position(self, token_address: str) -> Optional[Position]:
        """Get position by token address"""
        return self.positions.get(token_address)
    
    def get_open_positions(self) -> List[Position]:
        """Get all open or partial positions"""
        return [
            pos for pos in self.positions.values()
            if pos.status in [PositionStatus.OPEN, PositionStatus.PARTIAL_EXIT]
        ]
    
    def get_closed_positions(self, limit: int = 100) -> List[Position]:
        """Get recently closed positions"""
        closed = [
            pos for pos in self.positions.values()
            if pos.status == PositionStatus.CLOSED
        ]
        return sorted(closed, key=lambda x: x.exit_time or datetime.min, reverse=True)[:limit]
    
    def get_portfolio_summary(self, current_prices: Optional[Dict[str, float]] = None) -> Dict:
        """
        Get portfolio-level summary
        
        Args:
            current_prices: Dict of token_address -> price
        
        Returns:
            Summary dict with P&L metrics
        """
        open_positions = self.get_open_positions()
        closed_positions = [p for p in self.positions.values() if p.status == PositionStatus.CLOSED]
        
        # Calculate total realized P&L
        total_realized = sum(p.realized_pnl for p in self.positions.values())
        
        # Calculate unrealized P&L
        total_unrealized = 0.0
        if current_prices:
            for pos in open_positions:
                price = current_prices.get(pos.token_address, 0)
                total_unrealized += pos.unrealized_pnl(price)
        
        # Performance metrics
        total_trades = len([t for p in self.positions.values() for t in p.trades if t.side == TradeSide.SELL])
        winning_trades = len([
            p for p in closed_positions
            if p.realized_pnl > 0
        ])
        
        win_rate = (winning_trades / len(closed_positions) * 100) if closed_positions else 0
        
        return {
            "open_positions": len(open_positions),
            "total_positions": len(self.positions),
            "realized_pnl_usd": total_realized,
            "unrealized_pnl_usd": total_unrealized,
            "total_pnl_usd": total_realized + total_unrealized,
            "total_trades": total_trades,
            "win_rate_pct": win_rate,
            "avg_position_size": sum(p.initial_value for p in open_positions) / len(open_positions) if open_positions else 0,
            "positions_by_grade": self._positions_by_grade()
        }
    
    def _positions_by_grade(self) -> Dict[str, int]:
        """Count positions by scanner grade"""
        grades = defaultdict(int)
        for pos in self.positions.values():
            if pos.scanner_grade:
                grades[pos.scanner_grade] += 1
        return dict(grades)
    
    def get_expired_positions(self) -> List[Position]:
        """Get positions that hit time limit"""
        return [
            pos for pos in self.get_open_positions()
            if pos.is_expired()
        ]
    
    def get_performance_report(self, days: int = 7) -> Dict:
        """
        Generate trading performance report
        
        Args:
            days: Number of days to report on
        
        Returns:
            Performance metrics dict
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_positions = [
            p for p in self.positions.values()
            if p.entry_time >= cutoff or (p.exit_time and p.exit_time >= cutoff)
        ]
        
        realized = sum(p.realized_pnl for p in recent_positions)
        closed = [p for p in recent_positions if p.status == PositionStatus.CLOSED]
        winners = [p for p in closed if p.realized_pnl > 0]
        losers = [p for p in closed if p.realized_pnl <= 0]
        
        return {
            "period_days": days,
            "positions_opened": len(recent_positions),
            "positions_closed": len(closed),
            "winners": len(winners),
            "losers": len(losers),
            "win_rate_pct": len(winners) / len(closed) * 100 if closed else 0,
            "total_realized_pnl": realized,
            "avg_winner": sum(w.realized_pnl for w in winners) / len(winners) if winners else 0,
            "avg_loser": sum(l.realized_pnl for l in losers) / len(losers) if losers else 0,
            "largest_winner": max((w.realized_pnl for w in winners), default=0),
            "largest_loser": min((l.realized_pnl for l in losers), default=0),
            "avg_hold_time_hours": sum(p.get_hold_time_minutes() for p in closed) / len(closed) / 60 if closed else 0
        }
    
    def export_trade_history(self, filepath: str):
        """Export all trades to CSV/JSON"""
        all_trades = []
        for pos in self.positions.values():
            for trade in pos.trades:
                all_trades.append({
                    **trade.to_dict(),
                    "position_id": pos.position_id,
                    "scanner_grade": pos.scanner_grade
                })
        
        with open(filepath, 'w') as f:
            json.dump(all_trades, f, indent=2)
        
        logger.info(f"✅ Exported {len(all_trades)} trades to {filepath}")


# Utility functions
def calculate_position_size(portfolio_value: float,
                             risk_pct: float = 0.02,
                             max_position_pct: float = 0.10) -> float:
    """
    Calculate optimal position size based on risk
    
    Args:
        portfolio_value: Total portfolio value
        risk_pct: Risk per trade (2% default)
        max_position_pct: Max as % of portfolio
    
    Returns:
        Recommended position size in USD
    """
    risk_amount = portfolio_value * risk_pct
    max_position = portfolio_value * max_position_pct
    
    return min(risk_amount, max_position)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("📊 Position Manager - Portfolio Tracking")
    print("=" * 60)
    
    # Create manager
    pm = PositionManager()
    
    # Mock position
    pos = pm.open_position(
        token_address="MockToken123",
        token_symbol="MOON",
        entry_price=0.0001,
        quantity=1000000,
        scanner_grade="A+",
        scanner_score=10
    )
    
    print(f"\n✅ Opened position: {pos.token_symbol}")
    print(f"   Entry: ${pos.entry_price:.6f}")
    print(f"   Value: ${pos.initial_value:.2f}")
    print(f"   Grade: {pos.scanner_grade}")
    
    print("\n💰 Features:")
    print("  • Real-time P&L tracking")
    print("  • Portfolio analytics")
    print("  • Risk metrics")
    print("  • Trade history")
    print("\n✅ Position manager ready")