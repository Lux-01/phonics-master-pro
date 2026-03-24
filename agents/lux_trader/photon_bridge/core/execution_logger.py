#!/usr/bin/env python3
"""
📝 Photon Bridge Execution Logger
Logs all Photon-related trades, sells, and performance metrics

Features:
- Structured logging of all sell executions
- Performance tracking per position
- JSONL format for easy parsing
- Integration with LuxTrader logging
- Alert generation on key events

Author: LuxTrader Photon Bridge v1.0
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionType(Enum):
    """Types of execution events"""
    BUY_PROPOSED = "buy_proposed"
    BUY_APPROVED = "buy_approved"
    BUY_EXECUTED = "buy_executed"
    SELL_PROFIT_1 = "sell_profit_1"
    SELL_PROFIT_2 = "sell_profit_2"
    SELL_STOP_LOSS = "sell_stop_loss"
    SELL_TIME_STOP = "sell_time_stop"
    SELL_EMERGENCY = "sell_emergency"
    SELL_WHALE_COPY = "sell_whale_copy"
    SELL_MANUAL = "sell_manual"
    RULE_TRIGGERED = "rule_triggered"
    RULE_EXECUTED = "rule_executed"
    RULE_FAILED = "rule_failed"
    PRICE_UPDATE = "price_update"
    ERROR = "error"
    ALERT = "alert"


class ExecutionStatus(Enum):
    """Execution status"""
    PENDING = "pending"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ExecutionRecord:
    """
    Single execution event record
    
    Attributes:
        event_id: Unique identifier
        event_type: Type of execution event
        timestamp: When event occurred
        token_address: Token CA
        token_symbol: Token symbol (if known)
        stage: Trading stage (9 or 10)
        status: Execution status
        wallet: Connected wallet address
        position_id: Reference to position
        entry_price: Entry price in SOL
        current_price: Current/market price
        target_price: Target trigger price
        quantity: Token quantity
        expected_profit_pct: Expected profit percentage
        actual_profit_pct: Actual realized profit
        sol_received: SOL received from sell
        fees_paid: Fees paid
        tx_signature: Transaction signature
        reason: Reason for execution (e.g., "stop_loss_trigger")
        metadata: Additional data
        error: Error message if failed
    """
    event_id: str
    event_type: str
    timestamp: str
    token_address: str
    token_symbol: str = "UNKNOWN"
    stage: int = 9
    status: str = "pending"
    wallet: str = ""
    position_id: str = ""
    entry_price: float = 0.0
    current_price: float = 0.0
    target_price: float = 0.0
    quantity: float = 0.0
    expected_profit_pct: float = 0.0
    actual_profit_pct: float = 0.0
    sol_received: float = 0.0
    fees_paid: float = 0.0
    tx_signature: Optional[str] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExecutionRecord':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DailyPerformance:
    """Daily trading performance summary"""
    date: str
    total_trades: int = 0
    profitable_trades: int = 0
    losing_trades: int = 0
    total_sol_invested: float = 0.0
    total_sol_returned: float = 0.0
    total_pnl_sol: float = 0.0
    total_pnl_pct: float = 0.0
    win_rate: float = 0.0
    avg_profit_per_trade: float = 0.0
    avg_loss_per_trade: float = 0.0
    largest_profit: float = 0.0
    largest_loss: float = 0.0
    photon_fees_paid: float = 0.0
    positions_opened: int = 0
    positions_closed: int = 0
    stop_losses_hit: int = 0
    take_profits_hit: int = 0
    time_exits: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PhotonExecutionLogger:
    """
    Central logger for all Photon bridge executions
    
    Handles:
    - Event logging to JSONL
    - Performance tracking
    - Daily summaries
    - Alert generation
    - Integration with LuxTrader
    """
    
    def __init__(self, 
                 log_dir: str = None,
                 wallet: str = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"):
        """
        Initialize execution logger
        
        Args:
            log_dir: Directory for log files (default: workspace/logs/photon_bridge)
            wallet: Solana wallet address
        """
        self.wallet = wallet
        self.base_dir = Path(log_dir) if log_dir else Path("/home/skux/.openclaw/workspace/logs/photon_bridge")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.trades_file = self.base_dir / "photon_bridge_trades.jsonl"
        self.performance_file = self.base_dir / "photon_performance.json"
        self.daily_summary_file = self.base_dir / "daily_summary.json"
        
        # In-memory cache for current session
        self.session_events: List[ExecutionRecord] = []
        self.daily_stats: Dict[str, DailyPerformance] = {}
        
        # Load existing data
        self._load_performance_data()
        
        logger.info(f"📝 ExecutionLogger initialized: {self.base_dir}")
    
    def _load_performance_data(self):
        """Load existing performance data from disk"""
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    for date_str, perf_data in data.get('daily_stats', {}).items():
                        self.daily_stats[date_str] = DailyPerformance(**perf_data)
                logger.info(f"📊 Loaded performance data for {len(self.daily_stats)} days")
            except Exception as e:
                logger.warning(f"⚠️ Could not load performance data: {e}")
    
    def log_event(self, 
                  event_type: ExecutionType,
                  token_address: str,
                  token_symbol: str = "UNKNOWN",
                  stage: int = 9,
                  status: ExecutionStatus = ExecutionStatus.PENDING,
                  entry_price: float = 0.0,
                  current_price: float = 0.0,
                  target_price: float = 0.0,
                  quantity: float = 0.0,
                  expected_profit_pct: float = 0.0,
                  actual_profit_pct: float = 0.0,
                  sol_received: float = 0.0,
                  fees_paid: float = 0.0,
                  tx_signature: str = None,
                  reason: str = "",
                  metadata: Dict = None,
                  error: str = None) -> ExecutionRecord:
        """
        Log an execution event
        
        Args:
            event_type: Type of event
            token_address: Token contract address
            token_symbol: Token symbol
            stage: Trading stage
            status: Execution status
            entry_price: Entry price
            current_price: Current price
            target_price: Target trigger price
            quantity: Token quantity
            expected_profit_pct: Expected profit %
            actual_profit_pct: Actual profit %
            sol_received: SOL received
            fees_paid: Fees paid
            tx_signature: Transaction signature
            reason: Execution reason
            metadata: Additional metadata
            error: Error message
            
        Returns:
            ExecutionRecord: The created record
        """
        timestamp = datetime.utcnow().isoformat()
        event_id = f"{timestamp.replace(':', '-')}-{token_address[:8]}"
        
        record = ExecutionRecord(
            event_id=event_id,
            event_type=event_type.value,
            timestamp=timestamp,
            token_address=token_address,
            token_symbol=token_symbol,
            stage=stage,
            status=status.value,
            wallet=self.wallet,
            position_id=f"{token_address}-{timestamp[:10]}",
            entry_price=entry_price,
            current_price=current_price,
            target_price=target_price,
            quantity=quantity,
            expected_profit_pct=expected_profit_pct,
            actual_profit_pct=actual_profit_pct,
            sol_received=sol_received,
            fees_paid=fees_paid,
            tx_signature=tx_signature,
            reason=reason,
            metadata=metadata or {},
            error=error
        )
        
        # Add to session cache
        self.session_events.append(record)
        
        # Write to JSONL
        self._append_to_jsonl(record)
        
        # Update daily stats
        self._update_daily_stats(record)
        
        # Log to console
        self._console_log(record)
        
        return record
    
    def _append_to_jsonl(self, record: ExecutionRecord):
        """Append record to JSONL file"""
        try:
            with open(self.trades_file, 'a') as f:
                f.write(json.dumps(record.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"❌ Failed to write to trades file: {e}")
    
    def _update_daily_stats(self, record: ExecutionRecord):
        """Update daily performance statistics"""
        date = record.timestamp[:10]  # YYYY-MM-DD
        
        if date not in self.daily_stats:
            self.daily_stats[date] = DailyPerformance(date=date)
        
        stats = self.daily_stats[date]
        
        # Update based on event type
        event_type = ExecutionType(record.event_type)
        
        if event_type == ExecutionType.BUY_EXECUTED:
            stats.positions_opened += 1
            stats.total_sol_invested += record.quantity * record.entry_price
        
        elif event_type in [ExecutionType.SELL_PROFIT_1, 
                          ExecutionType.SELL_PROFIT_2,
                          ExecutionType.SELL_STOP_LOSS,
                          ExecutionType.SELL_TIME_STOP]:
            stats.positions_closed += 1
            stats.total_sol_returned += record.sol_received
            stats.total_trades += 1
            
            if record.actual_profit_pct > 0:
                stats.profitable_trades += 1
                stats.largest_profit = max(stats.largest_profit, record.actual_profit_pct)
            else:
                stats.losing_trades += 1
                stats.largest_loss = min(stats.largest_loss, record.actual_profit_pct)
            
            # Categorize exit type
            if event_type == ExecutionType.SELL_STOP_LOSS:
                stats.stop_losses_hit += 1
            elif event_type in [ExecutionType.SELL_PROFIT_1, ExecutionType.SELL_PROFIT_2]:
                stats.take_profits_hit += 1
            elif event_type == ExecutionType.SELL_TIME_STOP:
                stats.time_exits += 1
        
        # Recalculate derived stats
        if stats.total_trades > 0:
            stats.win_rate = stats.profitable_trades / stats.total_trades
            stats.total_pnl_sol = stats.total_sol_returned - stats.total_sol_invested
            if stats.total_sol_invested > 0:
                stats.total_pnl_pct = (stats.total_pnl_sol / stats.total_sol_invested) * 100
        
        # Save updated stats
        self._save_performance_data()
    
    def _save_performance_data(self):
        """Save performance data to disk"""
        try:
            data = {
                'wallet': self.wallet,
                'last_updated': datetime.utcnow().isoformat(),
                'daily_stats': {k: v.to_dict() for k, v in self.daily_stats.items()}
            }
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save performance data: {e}")
    
    def _console_log(self, record: ExecutionRecord):
        """Log to console with appropriate formatting"""
        event_type = ExecutionType(record.event_type)
        
        # Color/format based on event type
        if event_type in [ExecutionType.SELL_PROFIT_1, ExecutionType.SELL_PROFIT_2]:
            icon = "💰"
        elif event_type == ExecutionType.SELL_STOP_LOSS:
            icon = "🛑"
        elif event_type == ExecutionType.ERROR:
            icon = "❌"
        elif event_type == ExecutionType.RULE_TRIGGERED:
            icon = "⚡"
        elif event_type == ExecutionType.BUY_EXECUTED:
            icon = "🎯"
        else:
            icon = "📝"
        
        msg = f"{icon} [{record.timestamp[11:19]}] {event_type.value}"
        if record.token_symbol != "UNKNOWN":
            msg += f" | {record.token_symbol}"
        msg += f" | {record.status}"
        
        if record.actual_profit_pct != 0:
            msg += f" | P&L: {record.actual_profit_pct:+.2f}%"
        
        if record.error:
            msg += f" | Error: {record.error[:50]}"
        
        logger.info(msg)
    
    def log_buy_proposed(self, token_address: str, token_symbol: str, 
                        stage: int, metadata: Dict = None) -> ExecutionRecord:
        """Log buy proposal (Stage 9)"""
        return self.log_event(
            event_type=ExecutionType.BUY_PROPOSED,
            token_address=token_address,
            token_symbol=token_symbol,
            stage=stage,
            status=ExecutionStatus.PENDING,
            reason="Buy proposal from v54 scanner",
            metadata=metadata
        )
    
    def log_buy_executed(self, token_address: str, token_symbol: str,
                        entry_price: float, quantity: float,
                        tx_signature: str, stage: int = 9,
                        metadata: Dict = None) -> ExecutionRecord:
        """Log successful buy execution"""
        return self.log_event(
            event_type=ExecutionType.BUY_EXECUTED,
            token_address=token_address,
            token_symbol=token_symbol,
            stage=stage,
            status=ExecutionStatus.SUCCESS,
            entry_price=entry_price,
            quantity=quantity,
            tx_signature=tx_signature,
            reason="Buy executed",
            metadata=metadata
        )
    
    def log_sell_executed(self, token_address: str, token_symbol: str,
                         entry_price: float, exit_price: float,
                         quantity: float, sol_received: float,
                         fees_paid: float, tx_signature: str,
                         reason: str, stage: int = 9,
                         metadata: Dict = None) -> ExecutionRecord:
        """Log successful sell execution"""
        profit_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        
        # Determine event type from reason
        if "profit_1" in reason.lower() or "take_profit_1" in reason.lower():
            event_type = ExecutionType.SELL_PROFIT_1
        elif "profit_2" in reason.lower() or "take_profit_2" in reason.lower():
            event_type = ExecutionType.SELL_PROFIT_2
        elif "stop_loss" in reason.lower():
            event_type = ExecutionType.SELL_STOP_LOSS
        elif "time" in reason.lower():
            event_type = ExecutionType.SELL_TIME_STOP
        else:
            event_type = ExecutionType.SELL_MANUAL
        
        return self.log_event(
            event_type=event_type,
            token_address=token_address,
            token_symbol=token_symbol,
            stage=stage,
            status=ExecutionStatus.SUCCESS,
            entry_price=entry_price,
            current_price=exit_price,
            quantity=quantity,
            actual_profit_pct=profit_pct,
            sol_received=sol_received,
            fees_paid=fees_paid,
            tx_signature=tx_signature,
            reason=reason,
            metadata=metadata
        )
    
    def log_error(self, token_address: str, error: str,
                  stage: int = 9, metadata: Dict = None) -> ExecutionRecord:
        """Log execution error"""
        return self.log_event(
            event_type=ExecutionType.ERROR,
            token_address=token_address,
            stage=stage,
            status=ExecutionStatus.FAILED,
            error=error,
            metadata=metadata
        )
    
    def log_rule_triggered(self, token_address: str, token_symbol: str,
                          rule_name: str, target_price: float,
                          current_price: float, stage: int = 9) -> ExecutionRecord:
        """Log when a sell rule is triggered"""
        return self.log_event(
            event_type=ExecutionType.RULE_TRIGGERED,
            token_address=token_address,
            token_symbol=token_symbol,
            stage=stage,
            target_price=target_price,
            current_price=current_price,
            reason=f"Rule triggered: {rule_name}",
            metadata={"rule_name": rule_name}
        )
    
    def get_daily_performance(self, date: str = None) -> Optional[DailyPerformance]:
        """
        Get performance for a specific date
        
        Args:
            date: Date string YYYY-MM-DD (default: today)
            
        Returns:
            DailyPerformance or None
        """
        if date is None:
            date = datetime.utcnow().strftime('%Y-%m-%d')
        return self.daily_stats.get(date)
    
    def get_session_events(self, event_type: ExecutionType = None) -> List[ExecutionRecord]:
        """
        Get events from current session
        
        Args:
            event_type: Optional filter by event type
            
        Returns:
            List of ExecutionRecord
        """
        if event_type:
            return [e for e in self.session_events if e.event_type == event_type.value]
        return self.session_events.copy()
    
    def generate_summary_report(self, days: int = 7) -> Dict:
        """
        Generate performance summary for last N days
        
        Args:
            days: Number of days to include
            
        Returns:
            Summary report dictionary
        """
        today = datetime.utcnow()
        recent_stats = []
        
        for i in range(days):
            date = (today - __import__('datetime').timedelta(days=i)).strftime('%Y-%m-%d')
            if date in self.daily_stats:
                recent_stats.append(self.daily_stats[date])
        
        if not recent_stats:
            return {"message": "No data for specified period"}
        
        total_trades = sum(s.total_trades for s in recent_stats)
        total_profit = sum(s.total_pnl_sol for s in recent_stats)
        avg_win_rate = sum(s.win_rate for s in recent_stats) / len(recent_stats) if recent_stats else 0
        
        return {
            "period_days": days,
            "total_trades": total_trades,
            "total_pnl_sol": total_profit,
            "win_rate": avg_win_rate,
            "profitable_days": len([s for s in recent_stats if s.total_pnl_sol > 0]),
            "losing_days": len([s for s in recent_stats if s.total_pnl_sol < 0]),
            "daily_breakdown": [s.to_dict() for s in recent_stats]
        }
    
    def clear_session_cache(self):
        """Clear in-memory session cache"""
        self.session_events.clear()
        logger.info("🧹 Session cache cleared")


# Convenience function for direct import
def create_logger(wallet: str = None) -> PhotonExecutionLogger:
    """
    Create a new execution logger
    
    Args:
        wallet: Wallet address (default from config)
        
    Returns:
        PhotonExecutionLogger instance
    """
    wallet = wallet or "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    return PhotonExecutionLogger(wallet=wallet)


if __name__ == "__main__":
    # Demo/test
    logger_instance = create_logger()
    
    # Log sample events
    logger_instance.log_buy_executed(
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        token_symbol="TEST",
        entry_price=0.01,
        quantity=1000,
        tx_signature="2wP4252RAmmSegucUQMU7TmW9BYCxxBwhkZcMHw8FE7a7f4LaP5pYRJLE5hTBkKMtcZzFLZfDGcg9oeZsqAw48CN",
        stage=9
    )
    
    logger_instance.log_sell_executed(
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        token_symbol="TEST",
        entry_price=0.01,
        exit_price=0.0115,
        quantity=500,
        sol_received=0.00575,
        fees_paid=0.00005,
        tx_signature="sample_tx_123",
        reason="take_profit_1",
        stage=9
    )
    
    print("\n📊 Daily Performance:")
    perf = logger_instance.get_daily_performance()
    if perf:
        print(f"Trades: {perf.total_trades}, P&L: {perf.total_pnl_sol:.4f} SOL")
    
    print("\n✅ Logger test complete")