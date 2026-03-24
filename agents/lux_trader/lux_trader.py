#!/usr/bin/env python3
"""
LuxTrader v1.0 - Self-Learning Paper Trading System
Core trading engine with learning capabilities.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lux_trader")


@dataclass
class Trade:
    """Single paper trade record"""
    id: int
    token_symbol: str
    token_address: str
    entry_price: float
    entry_time: str
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    status: str = "OPEN"  # OPEN, CLOSED, RUG
    pnl_pct: float = 0.0
    outcome: str = ""  # win, loss, rug, timeout
    exit_reason: str = ""
    target: float = 0.15
    stop_loss: float = -0.07
    
    @property
    def is_open(self) -> bool:
        return self.status == "OPEN"


@dataclass  
class StrategyConfig:
    """Current trading strategy - evolves with learning"""
    version: str = "0.1"
    max_positions: int = 3
    position_size_sol: float = 0.01
    target_profit: float = 0.15
    stop_loss: float = -0.07
    time_stop_minutes: int = 240
    min_liquidity: float = 5000
    max_age_hours: int = 24
    min_score: float = 75
    
    # Learned parameters (start empty, fill with patterns)
    learned_rules: List[Dict] = None
    
    def __post_init__(self):
        if self.learned_rules is None:
            self.learned_rules = []


@dataclass
class LearningPattern:
    """Extracted pattern from trade analysis"""
    pattern_type: str  # "entry", "exit", "filter", "sizing"
    condition: str     # Description of what to check
    result: str       # "improves_win_rate", "reduces_losses", "neutral"
    confidence: float  # 0.0-1.0 based on sample size
    avg_pnl_when_applied: float
    sample_size: int
    created_at: str


class LuxTrader:
    """
    Self-learning paper trading system.
    Learns from every trade and evolves strategy.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path("/home/skux/.openclaw/workspace/agents/lux_trader")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Files
        self.strategy_file = self.data_dir / "strategy.json"
        self.trades_file = self.data_dir / "trades.json"
        self.learning_file = self.data_dir / "learning.json"
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.performance_file = self.data_dir / "performance.json"
        
        # Load state
        self.strategy = self._load_strategy()
        self.trades: List[Trade] = self._load_trades()
        self.patterns: List[LearningPattern] = self._load_patterns()
        self.portfolio: List[Trade] = self._load_portfolio()
        
        # Trade counter
        self.trade_counter = len(self.trades)
    
    def _load_strategy(self) -> StrategyConfig:
        """Load or create initial strategy"""
        if self.strategy_file.exists():
            try:
                with open(self.strategy_file) as f:
                    data = json.load(f)
                return StrategyConfig(**data)
            except:
                pass
        return StrategyConfig()
    
    def _save_strategy(self):
        """Save current strategy"""
        with open(self.strategy_file, 'w') as f:
            json.dump(asdict(self.strategy), f, indent=2)
    
    def _load_trades(self) -> List[Trade]:
        """Load trade history"""
        if not self.trades_file.exists():
            return []
        try:
            with open(self.trades_file) as f:
                data = json.load(f)
            return [Trade(**t) for t in data]
        except:
            return []
    
    def _save_trades(self):
        """Save all trades"""
        with open(self.trades_file, 'w') as f:
            json.dump([asdict(t) for t in self.trades], f, indent=2)
    
    def _load_patterns(self) -> List[LearningPattern]:
        """Load learned patterns"""
        if not self.learning_file.exists():
            return []
        try:
            with open(self.learning_file) as f:
                data = json.load(f)
            return [LearningPattern(**p) for p in data.get('patterns', [])]
        except:
            return []
    
    def _save_patterns(self):
        """Save learned patterns"""
        data = {
            'patterns': [asdict(p) for p in self.patterns],
            'last_updated': datetime.now().isoformat()
        }
        with open(self.learning_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_portfolio(self) -> List[Trade]:
        """Load open positions"""
        if not self.portfolio_file.exists():
            return []
        try:
            with open(self.portfolio_file) as f:
                data = json.load(f)
            return [Trade(**t) for t in data.get('positions', [])]
        except:
            return []
    
    def _save_portfolio(self):
        """Save open positions"""
        data = {
            'positions': [asdict(t) for t in self.portfolio],
            'updated_at': datetime.now().isoformat()
        }
        with open(self.portfolio_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def execute_paper_trade(self, token: Dict) -> Optional[Trade]:
        """
        Execute paper trade for a token.
        
        Args:
            token: Dict with symbol, address, price, score, etc.
        
        Returns:
            Trade object if executed, None if rejected
        """
        # Check constraints
        if len(self.portfolio) >= self.strategy.max_positions:
            logger.info(f"Max positions ({self.strategy.max_positions}) reached, skipping {token['symbol']}")
            return None
        
        # Check for duplicate
        if any(t.token_address == token['address'] for t in self.portfolio):
            logger.info(f"Position already exists for {token['symbol']}, skipping")
            return None
        
        # Apply learned filters (if any)
        for rule in self.strategy.learned_rules:
            if not self._apply_rule(token, rule):
                logger.info(f"Filtered by rule: {rule.get('condition', 'unknown')}")
                return None
        
        # Create trade
        self.trade_counter += 1
        trade = Trade(
            id=self.trade_counter,
            token_symbol=token['symbol'],
            token_address=token['address'],
            entry_price=token['price'],
            entry_time=datetime.now().isoformat(),
            target=self.strategy.target_profit,
            stop_loss=self.strategy.stop_loss
        )
        
        # Add to portfolio
        self.portfolio.append(trade)
        self.trades.append(trade)
        
        # Save
        self._save_portfolio()
        self._save_trades()
        
        logger.info(f"📝 PAPER TRADE #{trade.id}: {trade.token_symbol} @ ${trade.entry_price:.6f}")
        logger.info(f"   Target: +{trade.target:.0%} | Stop: {trade.stop_loss:.0%}")
        
        return trade
    
    def _apply_rule(self, token: Dict, rule: Dict) -> bool:
        """Apply a learned filter rule"""
        # TODO: Implement rule application
        return True
    
    def check_exits(self, price_data: Dict[str, float]):
        """
        Check all open positions for exit conditions.
        
        Args:
            price_data: Dict mapping token addresses to current prices
        """
        closed = []
        
        for trade in self.portfolio:
            if not trade.is_open:
                continue
            
            current_price = price_data.get(trade.token_address)
            if not current_price:
                continue
            
            # Calculate P&L
            pnl = (current_price - trade.entry_price) / trade.entry_price
            
            # Check exit conditions
            exit_triggered = False
            exit_reason = ""
            
            if pnl >= trade.target:
                exit_triggered = True
                exit_reason = "target_hit"
            elif pnl <= trade.stop_loss:
                exit_triggered = True
                exit_reason = "stop_loss"
            elif self._time_stop_reached(trade):
                exit_triggered = True
                exit_reason = "time_stop"
            elif pnl < -0.50:  # 50% down is effectively a rug
                exit_triggered = True
                exit_reason = "rug"
            
            if exit_triggered:
                trade.exit_price = current_price
                trade.exit_time = datetime.now().isoformat()
                trade.pnl_pct = pnl
                trade.exit_reason = exit_reason
                trade.status = "RUG" if exit_reason == "rug" else "CLOSED"
                trade.outcome = "rug" if exit_reason == "rug" else ("win" if pnl > 0 else "loss")
                
                closed.append(trade)
                logger.info(f"🔚 PAPER TRADE #{trade.id} CLOSED: {trade.token_symbol}")
                logger.info(f"   P&L: {pnl:+.1%} | Reason: {exit_reason}")
        
        # Remove closed from portfolio
        for trade in closed:
            self.portfolio.remove(trade)
        
        if closed:
            self._save_portfolio()
            self._save_trades()
            
            # Learn from these trades
            for trade in closed:
                self._learn_from_trade(trade)
    
    def _time_stop_reached(self, trade: Trade) -> bool:
        """Check if time stop has been reached"""
        entry = datetime.fromisoformat(trade.entry_time)
        elapsed = datetime.now() - entry
        return elapsed.total_seconds() / 60 >= self.strategy.time_stop_minutes
    
    def _learn_from_trade(self, trade: Trade):
        """
        Extract patterns from a completed trade.
        This is where the magic happens.
        """
        logger.info(f"🧠 Learning from trade #{trade.id}...")
        
        # Pattern 1: Win rate by outcome type
        pattern = LearningPattern(
            pattern_type="outcome",
            condition=f"Outcome was {trade.outcome}",
            result="analyzed",
            confidence=0.5,
            avg_pnl_when_applied=trade.pnl_pct,
            sample_size=1,
            created_at=datetime.now().isoformat()
        )
        self.patterns.append(pattern)
        
        # Save patterns
        self._save_patterns()
    
    def evolve_strategy(self):
        """
        Analyze all patterns and update strategy.
        Called periodically (e.g., after every 5 trades).
        """
        if len(self.trades) < 5:
            return  # Need more data
        
        logger.info("🔄 Evolving strategy based on learnings...")
        
        # Simple evolution: update learned_rules
        wins = [t for t in self.trades if t.outcome == "win"]
        losses = [t for t in self.trades if t.outcome == "loss"]
        
        if not wins:
            return
        
        # Extract common patterns in wins
        avg_win_pnl = sum(t.pnl_pct for t in wins) / len(wins)
        win_rate = len(wins) / len(self.trades)
        
        # Update strategy version
        current_version = float(self.strategy.version)
        self.strategy.version = f"{current_version + 0.1:.1f}"
        
        # Add learned insight
        self.strategy.learned_rules.append({
            'insight': f'Win rate {win_rate:.1%} with {len(self.trades)} trades',
            'avg_win': f'{avg_win_pnl:.1%}',
            'improvement': 'Continue current approach' if win_rate > 0.5 else 'Need adjustment'
        })
        
        self._save_strategy()
        logger.info(f"✅ Strategy updated to v{self.strategy.version}")
    
    def get_performance(self) -> Dict:
        """Get current performance metrics"""
        if not self.trades:
            return {'message': 'No trades yet'}
        
        closed = [t for t in self.trades if not t.is_open]
        if not closed:
            return {'message': 'No completed trades yet'}
        
        wins = [t for t in closed if t.outcome == "win"]
        losses = [t for t in closed if t.outcome == "loss"]
        rugs = [t for t in closed if t.outcome == "rug"]
        
        total_pnl = sum(t.pnl_pct for t in closed)
        avg_win = sum(t.pnl_pct for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl_pct for t in losses) / len(losses) if losses else 0
        
        return {
            'total_trades': len(self.trades),
            'completed_trades': len(closed),
            'open_positions': len(self.portfolio),
            'wins': len(wins),
            'losses': len(losses),
            'rugs': len(rugs),
            'win_rate': f"{len(wins)/len(closed)*100:.1f}%",
            'total_pnl': f"{total_pnl:+.1f}%",
            'avg_win': f"{avg_win:+.1f}%",
            'avg_loss': f"{avg_loss:+.1f}%",
            'strategy_version': self.strategy.version,
            'patterns_learned': len(self.patterns)
        }
    
    def print_status(self):
        """Print current status"""
        print("\n" + "="*60)
        print("📊 LUXTRADER STATUS")
        print("="*60)
        
        perf = self.get_performance()
        for key, value in perf.items():
            print(f"  {key}: {value}")
        
        if self.portfolio:
            print("\n📈 OPEN POSITIONS:")
            for t in self.portfolio:
                print(f"  #{t.id}: {t.token_symbol} - Open since {t.entry_time[:16]}")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test mode
    trader = LuxTrader()
    trader.print_status()
    
    # Simulate a trade
    test_token = {
        'symbol': 'TEST',
        'address': 'TEST123',
        'price': 0.0001,
        'score': 80
    }
    
    trade = trader.execute_paper_trade(test_token)
    if trade:
        print(f"\nTrade executed: #{trade.id}")
        
        # Simulate price check with profit
        trader.check_exits({'TEST123': 0.000115})  # +15%
        
        # Show updated status
        trader.print_status()
