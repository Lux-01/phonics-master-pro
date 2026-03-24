#!/usr/bin/env python3
"""
Whale Tracker Strategy
Monitors large wallet buy patterns, enters when whale activity detected
"""

import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import statistics

@dataclass
class Trade:
    symbol: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    pnl_sol: float
    entry_reason: str
    exit_reason: str
    timestamp: int
    position_size: float

@dataclass
class StrategyState:
    balance: float = 1.0
    trades: List[Trade] = None
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    
    def __post_init__(self):
        if self.trades is None:
            self.trades = []

class WhaleTracker:
    """
    Detects whale activity by analyzing:
    - High 5m volume spikes (indicates large buying)
    - Market cap changes (whale accumulation)
    - New coin + strong momentum (early whale entry)
    """
    
    def __init__(self, initial_balance: float = 1.0):
        self.state = StrategyState(balance=initial_balance)
        self.learning_params = {
            'volume_threshold': 1.5,  # Multiplier above average
            'mcap_entry_max': 50000,   # Max market cap for entry
            'age_threshold': 24,       # Hours since launch
            'profit_target': 0.15,     # 15% take profit
            'stop_loss': 0.08,         # 8% stop loss
            'position_size': 0.1       # 10% of balance per trade
        }
        self.performance_history = []
        
    def detect_whale_activity(self, trade_data: Dict) -> bool:
        """
        Detect whale buying patterns from trade metadata
        """
        entry_reason = trade_data.get('entry_reason', '').lower()
        
        # Whale signals
        whale_signals = [
            'high 5m volume' in entry_reason,
            'strong momentum' in entry_reason,
            'new coin' in entry_reason and trade_data.get('age_hours', 999) < 12,
            trade_data.get('grade') in ['A+', 'A'] and trade_data.get('mcap', 999999) < 50000,
        ]
        
        return sum(whale_signals) >= 2  # Need 2+ signals
    
    def should_enter(self, trade_data: Dict) -> bool:
        """
        Entry logic: Enter when whale activity detected
        """
        if self.detect_whale_activity(trade_data):
            # Additional filters
            mcap = trade_data.get('mcap', 0)
            age = trade_data.get('age_hours', 999)
            
            # Whales prefer fresh, lower cap coins
            if mcap < self.learning_params['mcap_entry_max'] and age < self.learning_params['age_threshold']:
                return True
        return False
    
    def should_exit(self, trade_data: Dict, current_pnl: float) -> tuple[bool, str]:
        """
        Exit logic based on profit target or stop loss
        """
        if current_pnl >= self.learning_params['profit_target']:
            return True, f"Whale profit target +{current_pnl*100:.1f}%"
        if current_pnl <= -self.learning_params['stop_loss']:
            return True, f"Whale stop loss -{abs(current_pnl)*100:.1f}%"
        
        # Exit on rug signals
        if trade_data.get('is_rug', False):
            return True, "Rug detected - emergency exit"
            
        return False, ""
    
    def execute_trade(self, trade_data: Dict) -> Dict[str, Any]:
        """
        Execute a single trade based on whale signals
        """
        result = trade_data.get('result', 'unknown')
        pnl_pct = trade_data.get('pnl_pct', 0) / 100
        pnl_sol = trade_data.get('pnl_sol', 0)
        
        # Calculate position size
        position_size = min(
            self.state.balance * self.learning_params['position_size'],
            self.state.balance * 0.2  # Max 20% per trade
        )
        
        # Simulate trade execution
        trade = Trade(
            symbol=trade_data.get('symbol', 'UNKNOWN'),
            entry_price=1.0,  # Normalized
            exit_price=1.0 + pnl_pct,
            pnl_pct=pnl_pct * 100,
            pnl_sol=pnl_sol,
            entry_reason=trade_data.get('entry_reason', 'Whale signal'),
            exit_reason=trade_data.get('exit_reason', 'Strategy exit'),
            timestamp=trade_data.get('day', 0),
            position_size=position_size
        )
        
        self.state.trades.append(trade)
        self.state.total_trades += 1
        
        # Update balance
        if result == 'win':
            self.state.wins += 1
            self.state.balance += pnl_sol
        else:
            self.state.losses += 1
            self.state.balance += pnl_sol  # pnl_sol is negative for losses
            
        return trade_data
    
    def evolve_parameters(self):
        """
        Learning: Adjust parameters based on performance
        """
        if len(self.state.trades) < 10:
            return
            
        recent_trades = self.state.trades[-20:]
        win_rate = sum(1 for t in recent_trades if t.pnl_pct > 0) / len(recent_trades)
        avg_return = statistics.mean([t.pnl_pct for t in recent_trades])
        
        # Adjust profit target based on performance
        if win_rate > 0.6:
            self.learning_params['profit_target'] = min(0.25, self.learning_params['profit_target'] * 1.05)
        elif win_rate < 0.4:
            self.learning_params['profit_target'] = max(0.08, self.learning_params['profit_target'] * 0.95)
            
        # Adjust stop loss based on volatility
        if avg_return < -0.05:
            self.learning_params['stop_loss'] = min(0.15, self.learning_params['stop_loss'] * 1.1)
        elif avg_return > 0.05:
            self.learning_params['stop_loss'] = max(0.05, self.learning_params['stop_loss'] * 0.95)
            
        self.performance_history.append({
            'trade_count': len(self.state.trades),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'params': self.learning_params.copy()
        })
    
    def run_backtest(self, data_path: str) -> Dict[str, Any]:
        """
        Run full backtest on historical data
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        print(f"🐋 Whale Tracker: Processing {len(trades)} trades...")
        
        for i, trade_data in enumerate(trades):
            if self.should_enter(trade_data):
                self.execute_trade(trade_data)
                
                # Evolve parameters every 20 trades
                if self.state.total_trades % 20 == 0:
                    self.evolve_parameters()
        
        # Generate results
        results = {
            'strategy': 'Whale Tracker',
            'description': 'Monitors large wallet buy patterns, enters when whale activity detected',
            'initial_balance': 1.0,
            'final_balance': round(self.state.balance, 6),
            'total_return_pct': round((self.state.balance - 1.0) * 100, 2),
            'total_trades': self.state.total_trades,
            'wins': self.state.wins,
            'losses': self.state.losses,
            'win_rate_pct': round(self.state.wins / max(self.state.total_trades, 1) * 100, 2),
            'avg_trade_return_pct': round(
                sum(t.pnl_pct for t in self.state.trades) / max(len(self.state.trades), 1), 2
            ),
            'learning_history': self.performance_history,
            'final_params': self.learning_params,
            'trades': [{
                'symbol': t.symbol,
                'pnl_pct': round(t.pnl_pct, 2),
                'pnl_sol': round(t.pnl_sol, 6),
                'entry_reason': t.entry_reason,
                'exit_reason': t.exit_reason,
                'day': t.timestamp
            } for t in self.state.trades]
        }
        
        return results


def main():
    tracker = WhaleTracker(initial_balance=1.0)
    results = tracker.run_backtest('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json')
    
    # Save results
    output_path = '/home/skux/.openclaw/workspace/whale_tracker_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Whale Tracker Results:")
    print(f"   Initial: 1.0 SOL")
    print(f"   Final: {results['final_balance']:.6f} SOL")
    print(f"   Return: {results['total_return_pct']:+.2f}%")
    print(f"   Trades: {results['total_trades']} (Win rate: {results['win_rate_pct']}%)")
    print(f"   Results saved to: {output_path}")


if __name__ == '__main__':
    main()
