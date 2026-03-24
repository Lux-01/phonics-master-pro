#!/usr/bin/env python3
"""
Breakout Hunter Strategy
Enter on new 24h highs with volume spikes
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import defaultdict
import statistics

@dataclass
class Trade:
    symbol: str
    pnl_pct: float
    pnl_sol: float
    entry_reason: str
    exit_reason: str
    day: int
    breakout_strength: float
    volume_score: float
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

class BreakoutHunter:
    """
    Momentum breakout strategy:
    - Identifies new highs (24h+ context in data)
    - Requires volume confirmation
    - Uses momentum indicators
    - Trailing stops for winners
    """
    
    def __init__(self, initial_balance: float = 1.0):
        self.state = StrategyState(balance=initial_balance)
        self.learning_params = {
            'min_volume_signal': 1,      # Minimum volume indicators
            'momentum_threshold': 0.6,    # Momentum strength required
            'profit_target': 0.18,        # 18% take profit (breakouts run)
            'stop_loss': 0.08,           # 8% stop loss
            'trailing_start': 0.10,      # Activate trailing at 10%
            'trailing_pct': 0.05,        # 5% trailing distance
            'position_size': 0.12,        # 12% base position
            'max_position': 0.30,         # 30% max (conviction trades)
            'freshness_boost': 1.3        # Multiplier for new tokens
        }
        self.performance_history = []
        self.symbol_history = defaultdict(list)  # Track per-symbol performance
        
    def analyze_volume_signals(self, trade_data: Dict) -> float:
        """
        Score volume indicators from entry reason
        """
        entry_reason = trade_data.get('entry_reason', '').lower()
        
        score = 0.0
        if 'high 5m volume' in entry_reason:
            score += 0.5
        if 'ultra fresh' in entry_reason:
            score += 0.3
        if 'strong momentum' in entry_reason:
            score += 0.2
            
        return min(score, 1.0)
    
    def analyze_momentum(self, trade_data: Dict) -> float:
        """
        Analyze momentum signals
        """
        grade = trade_data.get('grade', 'C')
        entry_reason = trade_data.get('entry_reason', '').lower()
        
        momentum = 0.0
        
        # Grade contribution
        grade_scores = {'A+': 1.0, 'A': 0.9, 'B': 0.7, 'C': 0.5, 'D': 0.3, 'F': 0.1}
        momentum += grade_scores.get(grade, 0.5) * 0.4
        
        # Entry reason keywords
        if 'strong momentum' in entry_reason:
            momentum += 0.3
        if 'high 5m volume' in entry_reason:
            momentum += 0.2
        if 'new coin' in entry_reason:
            momentum += 0.1
            
        return min(momentum, 1.0)
    
    def is_breakout_candidate(self, trade_data: Dict, day: int) -> tuple[bool, float]:
        """
        Determine if this is a breakout trade based on:
        - Volume spikes (new interest)
        - Momentum confirmation  
        - Grade quality
        - Freshness (new highs often come from new listings)
        """
        volume_score = self.analyze_volume_signals(trade_data)
        momentum_score = self.analyze_momentum(trade_data)
        
        # Combined breakout strength
        breakout_strength = volume_score * 0.4 + momentum_score * 0.6
        
        # Requirements
        has_volume = volume_score >= 0.3
        has_momentum = momentum_score >= self.learning_params['momentum_threshold']
        
        # Fresh token bonus (new highs on new coins)
        age = trade_data.get('age_hours', 999)
        if age < 12:
            breakout_strength *= self.learning_params['freshness_boost']
            
        is_breakout = has_volume and has_momentum and breakout_strength > 0.5
        
        return is_breakout, breakout_strength
    
    def calculate_position_size(self, breakout_strength: float, trade_data: Dict) -> float:
        """
        Conviction-based position sizing
        """
        base = self.state.balance * self.learning_params['position_size']
        
        # Scale by breakout strength
        conviction = breakout_strength / 0.7  # Normalize
        conviction = min(conviction, 2.0)  # Cap at 2x
        
        # Grade bonus
        grade = trade_data.get('grade', 'C')
        grade_mult = {'A+': 1.5, 'A': 1.3, 'B': 1.0, 'C': 0.8}.get(grade, 0.8)
        
        position = base * conviction * grade_mult
        max_pos = self.state.balance * self.learning_params['max_position']
        
        return min(position, max_pos, self.state.balance * 0.4)
    
    def should_exit_early(self, current_pnl: float, trade_data: Dict) -> tuple[bool, str]:
        """
        Exit logic with trailing stops
        """
        # Standard targets
        if current_pnl >= self.learning_params['profit_target'] * 100:
            return True, f"Profit target +{current_pnl:.1f}%"
            
        if current_pnl <= -self.learning_params['stop_loss'] * 100:
            return True, f"Stop loss -{abs(current_pnl):.1f}%"
        
        # Trailing stop logic (simulated)
        if current_pnl >= self.learning_params['trailing_start'] * 100:
            trail_exit = current_pnl - self.learning_params['trailing_pct'] * 100
            if current_pnl < trail_exit:
                return True, f"Trailing stop at +{current_pnl:.1f}%"
        
        # Time-based exit for breakouts that stall
        result = trade_data.get('result', '')
        if result == 'rug_or_bag':
            return True, "Momentum stalled"
            
        return False, ""
    
    def execute_trade(self, trade_data: Dict, breakout_strength: float) -> Dict[str, Any]:
        """
        Execute breakout trade
        """
        result = trade_data.get('result', 'unknown')
        pnl_pct = trade_data.get('pnl_pct', 0)
        pnl_sol = trade_data.get('pnl_sol', 0)
        
        volume_score = self.analyze_volume_signals(trade_data)
        position_size = self.calculate_position_size(breakout_strength, trade_data)
        
        trade = Trade(
            symbol=trade_data.get('symbol', 'UNKNOWN'),
            pnl_pct=pnl_pct,
            pnl_sol=pnl_sol,
            entry_reason=f"Breakout (strength: {breakout_strength:.2f})",
            exit_reason=trade_data.get('exit_reason', 'Breakout exit'),
            day=trade_data.get('day', 0),
            breakout_strength=breakout_strength,
            volume_score=volume_score,
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
        
        # Track symbol performance
        symbol = trade_data.get('symbol', 'UNKNOWN')
        self.symbol_history[symbol].append({
            'pnl': pnl_pct,
            'win': result == 'win'
        })
            
        return trade_data
    
    def evolve_parameters(self):
        """
        Learning: Optimize breakout thresholds
        """
        if len(self.state.trades) < 12:
            return
            
        recent = self.state.trades[-12:]
        
        # Analyze high vs low breakout strength
        high_conviction = [t for t in recent if t.breakout_strength > 0.7]
        low_conviction = [t for t in recent if t.breakout_strength <= 0.7]
        
        if high_conviction and low_conviction:
            high_avg = statistics.mean([t.pnl_pct for t in high_conviction])
            low_avg = statistics.mean([t.pnl_pct for t in low_conviction])
            
            # Adjust thresholds
            if high_avg > low_avg * 1.5:
                # High conviction works well, raise bar
                self.learning_params['momentum_threshold'] = min(
                    0.8, self.learning_params['momentum_threshold'] * 1.02
                )
            elif low_avg > high_avg:
                # Lower thresholds work, be more aggressive
                self.learning_params['momentum_threshold'] = max(
                    0.4, self.learning_params['momentum_threshold'] * 0.98
                )
        
        # Adjust profit targets based on average winner
        wins = [t for t in recent if t.pnl_pct > 0]
        if wins:
            avg_win = statistics.mean([t.pnl_pct for t in wins])
            if avg_win > self.learning_params['profit_target'] * 100 * 1.3:
                # We're exiting too early
                self.learning_params['profit_target'] = min(
                    0.25, self.learning_params['profit_target'] * 1.03
                )
        
        # Adjust position size based on win rate
        win_rate = self.state.wins / max(self.state.total_trades, 1)
        if win_rate > 0.55:
            self.learning_params['position_size'] = min(
                0.2, self.learning_params['position_size'] * 1.02
            )
        elif win_rate < 0.4:
            self.learning_params['position_size'] = max(
                0.08, self.learning_params['position_size'] * 0.97
            )
        
        self.performance_history.append({
            'trade_count': len(self.state.trades),
            'win_rate': win_rate,
            'avg_breakout_strength': statistics.mean([t.breakout_strength for t in recent]),
            'params': self.learning_params.copy()
        })
    
    def run_backtest(self, data_path: str) -> Dict[str, Any]:
        """
        Run full backtest
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        print(f"🚀 Breakout Hunter: Processing {len(trades)} trades...")
        
        for i, trade_data in enumerate(trades):
            is_breakout, strength = self.is_breakout_candidate(trade_data, i)
            if is_breakout:
                self.execute_trade(trade_data, strength)
                
                if self.state.total_trades % 12 == 0:
                    self.evolve_parameters()
        
        # Calculate statistics
        if self.state.trades:
            avg_strength = statistics.mean([t.breakout_strength for t in self.state.trades])
            avg_volume = statistics.mean([t.volume_score for t in self.state.trades])
            
            # Find best performing breakout type
            high_vol = [t for t in self.state.trades if t.volume_score > 0.5]
            high_vol_wr = len([t for t in high_vol if t.pnl_pct > 0]) / len(high_vol) if high_vol else 0
        else:
            avg_strength = 0
            avg_volume = 0
            high_vol_wr = 0
        
        results = {
            'strategy': 'Breakout Hunter',
            'description': 'Enter on new 24h highs with volume spikes',
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
            'avg_breakout_strength': round(avg_strength, 3),
            'avg_volume_score': round(avg_volume, 3),
            'high_volume_win_rate': round(high_vol_wr * 100, 2),
            'learning_history': self.performance_history,
            'final_params': self.learning_params,
            'trades': [{
                'symbol': t.symbol,
                'pnl_pct': round(t.pnl_pct, 2),
                'pnl_sol': round(t.pnl_sol, 6),
                'breakout_strength': round(t.breakout_strength, 3),
                'volume_score': round(t.volume_score, 3),
                'day': t.day
            } for t in self.state.trades]
        }
        
        return results


def main():
    hunter = BreakoutHunter(initial_balance=1.0)
    results = hunter.run_backtest('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json')
    
    output_path = '/home/skux/.openclaw/workspace/breakout_hunter_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Breakout Hunter Results:")
    print(f"   Initial: 1.0 SOL")
    print(f"   Final: {results['final_balance']:.6f} SOL")
    print(f"   Return: {results['total_return_pct']:+.2f}%")
    print(f"   Trades: {results['total_trades']} (Win rate: {results['win_rate_pct']}%)")
    print(f"   Avg Breakout Strength: {results['avg_breakout_strength']}")
    print(f"   Results saved to: {output_path}")


if __name__ == '__main__':
    main()
