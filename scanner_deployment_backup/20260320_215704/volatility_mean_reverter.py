#!/usr/bin/env python3
"""
Volatility Mean-Reverter Strategy
Buy oversold (below average), sell on bounce
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import deque
import statistics

@dataclass
class Trade:
    symbol: str
    pnl_pct: float
    pnl_sol: float
    entry_reason: str
    exit_reason: str
    day: int
    entry_deviation: float  # How far below mean we entered
    exit_deviation: float
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

class VolatilityMeanReverter:
    """
    Mean reversion strategy that:
    - Tracks rolling average returns
    - Enters when price/returns are significantly below mean (oversold)
    - Exits on mean reversion (bounce back)
    - Volatility-adjusted position sizing
    """
    
    def __init__(self, initial_balance: float = 1.0):
        self.state = StrategyState(balance=initial_balance)
        self.learning_params = {
            'lookback_window': 20,       # Trades to calculate mean
            'entry_deviation': -0.15,     # Enter when 15% below mean
            'exit_deviation': 0.05,       # Exit when back above mean
            'min_volatility': 0.1,       # Minimum volatility to trade
            'max_volatility': 0.5,       # Skip if too volatile
            'profit_target': 0.12,       # 12% profit target
            'stop_loss': 0.10,          # 10% stop loss (wider for mean reversion)
            'position_size': 0.15,        # 15% base position
            'momentum_filter': True       # Require some momentum for entry
        }
        self.return_history = deque(maxlen=50)
        self.deviation_history = []
        self.performance_history = []
        
    def update_market_stats(self, trade_data: Dict):
        """
        Update rolling statistics from trade data
        """
        pnl_pct = trade_data.get('pnl_pct', 0)
        self.return_history.append(pnl_pct)
    
    def calculate_mean_return(self) -> float:
        """
        Calculate rolling mean return
        """
        if len(self.return_history) < 5:
            return 5.0  # Default assumption
        return statistics.mean(list(self.return_history)[-self.learning_params['lookback_window']:])
    
    def calculate_volatility(self) -> float:
        """
        Calculate rolling volatility (std dev)
        """
        if len(self.return_history) < 5:
            return 0.2
        recent = list(self.return_history)[-self.learning_params['lookback_window']:]
        return statistics.stdev(recent) if len(recent) > 1 else 0.1
    
    def get_deviation_score(self, trade_data: Dict) -> float:
        """
        Calculate how far current trade is from mean
        Negative = oversold (potential buy)
        """
        mean_return = self.calculate_mean_return()
        current_return = trade_data.get('pnl_pct', 0)
        
        # We're looking at entry points - what happened historically
        # Trade with bad recent pnl might indicate oversold conditions
        deviation = (current_return - mean_return) / 100  # Normalize
        
        return deviation
    
    def should_enter(self, trade_data: Dict) -> tuple[bool, float]:
        """
        Enter when significantly below mean return (oversold)
        """
        volatility = self.calculate_volatility()
        
        # Skip if volatility out of range
        if volatility < self.learning_params['min_volatility'] * 100:
            return False, 0
        if volatility > self.learning_params['max_volatility'] * 100:
            return False, 0
            
        deviation = self.get_deviation_score(trade_data)
        
        # For mean reversion, we want negative deviation (price below trend)
        # But not too negative (could be a falling knife)
        expected_bounce = -deviation  # How much we expect to bounce
        
        entry_threshold = self.learning_params['entry_deviation']
        
        # Enter if oversold but not crashing
        if deviation < entry_threshold and deviation > -0.5:
            return True, expected_bounce
            
        return False, expected_bounce
    
    def calculate_position_size(self, expected_bounce: float, volatility: float) -> float:
        """
        Size positions based on expected bounce and volatility
        """
        base = self.state.balance * self.learning_params['position_size']
        
        # Scale by expected bounce (more oversold = larger position)
        bounce_multiplier = min(1 + abs(expected_bounce), 2.0)
        
        # Reduce size for high volatility
        vol_adj = 1.0 / (1 + volatility / 20)
        
        position = base * bounce_multiplier * vol_adj
        max_pos = self.state.balance * 0.3  # Max 30%
        
        return min(position, max_pos, self.state.balance * 0.5)
    
    def execute_trade(self, trade_data: Dict, expected_bounce: float) -> Dict[str, Any]:
        """
        Execute mean reversion trade
        """
        result = trade_data.get('result', 'unknown')
        pnl_pct = trade_data.get('pnl_pct', 0)
        pnl_sol = trade_data.get('pnl_sol', 0)
        
        volatility = self.calculate_volatility()
        deviation = self.get_deviation_score(trade_data)
        
        position_size = self.calculate_position_size(expected_bounce, volatility)
        
        # For mean reversion, we're simulating the strategy logic
        # We enter "oversold" conditions and exit on recovery
        
        # Adjust PnL - mean reversion trades might perform differently
        # If we identify a good oversold entry, we expect positive returns
        
        trade = Trade(
            symbol=trade_data.get('symbol', 'UNKNOWN'),
            pnl_pct=pnl_pct,
            pnl_sol=pnl_sol,
            entry_reason=f"Oversold (deviation: {deviation:.2f})",
            exit_reason=trade_data.get('exit_reason', 'Mean reversion exit'),
            day=trade_data.get('day', 0),
            entry_deviation=deviation,
            exit_deviation=deviation + (pnl_pct / 100),  # Simulated
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
            self.state.balance += pnl_sol
            
        # Track deviations
        self.deviation_history.append({
            'entry_dev': deviation,
            'exit_dev': deviation + (pnl_pct / 100),
            'pnl': pnl_pct
        })
            
        return trade_data
    
    def evolve_parameters(self):
        """
        Learning: Optimize entry/exit thresholds based on performance
        """
        if len(self.state.trades) < 15:
            return
            
        recent = self.state.trades[-15:]
        
        # Analyze by entry deviation
        deep_oversold = [t for t in recent if t.entry_deviation < -0.2]
        moderate_oversold = [t for t in recent if -0.2 <= t.entry_deviation < -0.1]
        
        if deep_oversold and moderate_oversold:
            deep_avg = statistics.mean([t.pnl_pct for t in deep_oversold])
            mod_avg = statistics.mean([t.pnl_pct for t in moderate_oversold])
            
            # Adjust entry threshold
            if deep_avg > mod_avg:
                # Deeper oversold works better
                self.learning_params['entry_deviation'] = max(
                    -0.3, self.learning_params['entry_deviation'] - 0.01
                )
            elif mod_avg > deep_avg:
                # Moderate is better (avoid falling knives)
                self.learning_params['entry_deviation'] = min(
                    -0.05, self.learning_params['entry_deviation'] + 0.01
                )
        
        # Adjust lookback window
        win_rate = self.state.wins / max(self.state.total_trades, 1)
        if win_rate < 0.45:
            # Try different window size
            self.learning_params['lookback_window'] = max(
                10, self.learning_params['lookback_window'] - 2
            )
        elif win_rate > 0.6:
            self.learning_params['lookback_window'] = min(
                40, self.learning_params['lookback_window'] + 2
            )
        
        # Track volatility performance
        vols = [statistics.stdev([t.pnl_pct for t in recent]) if len(recent) > 1 else 0]
        
        self.performance_history.append({
            'trade_count': len(self.state.trades),
            'win_rate': win_rate,
            'avg_deviation': statistics.mean([t.entry_deviation for t in recent]),
            'params': self.learning_params.copy()
        })
    
    def run_backtest(self, data_path: str) -> Dict[str, Any]:
        """
        Run full backtest
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        print(f"📉 Volatility Mean-Reverter: Processing {len(trades)} trades...")
        
        for i, trade_data in enumerate(trades):
            # Update market stats first
            self.update_market_stats(trade_data)
            
            should_enter, expected_bounce = self.should_enter(trade_data)
            if should_enter:
                self.execute_trade(trade_data, expected_bounce)
                
                if self.state.total_trades % 15 == 0:
                    self.evolve_parameters()
        
        # Calculate reversion statistics
        if self.deviation_history:
            successful_reversions = [d for d in self.deviation_history if d['pnl'] > 0]
            reversion_rate = len(successful_reversions) / len(self.deviation_history)
            
            avg_entry_dev = statistics.mean([t.entry_deviation for t in self.state.trades]) if self.state.trades else 0
            avg_exit_dev = statistics.mean([t.exit_deviation for t in self.state.trades]) if self.state.trades else 0
        else:
            reversion_rate = 0
            avg_entry_dev = 0
            avg_exit_dev = 0
        
        results = {
            'strategy': 'Volatility Mean-Reverter',
            'description': 'Buy oversold (below average), sell on bounce',
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
            'reversion_success_rate': round(reversion_rate * 100, 2),
            'avg_entry_deviation': round(avg_entry_dev, 4),
            'avg_exit_deviation': round(avg_exit_dev, 4),
            'final_volatility': round(self.calculate_volatility(), 4),
            'learning_history': self.performance_history,
            'final_params': self.learning_params,
            'trades': [{
                'symbol': t.symbol,
                'pnl_pct': round(t.pnl_pct, 2),
                'pnl_sol': round(t.pnl_sol, 6),
                'entry_deviation': round(t.entry_deviation, 4),
                'exit_deviation': round(t.exit_deviation, 4),
                'day': t.day
            } for t in self.state.trades]
        }
        
        return results


def main():
    reverter = VolatilityMeanReverter(initial_balance=1.0)
    results = reverter.run_backtest('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json')
    
    output_path = '/home/skux/.openclaw/workspace/volatility_mean_reverter_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Volatility Mean-Reverter Results:")
    print(f"   Initial: 1.0 SOL")
    print(f"   Final: {results['final_balance']:.6f} SOL")
    print(f"   Return: {results['total_return_pct']:+.2f}%")
    print(f"   Trades: {results['total_trades']} (Win rate: {results['win_rate_pct']}%)")
    print(f"   Reversion Success: {results['reversion_success_rate']}%")
    print(f"   Results saved to: {output_path}")


if __name__ == '__main__':
    main()
