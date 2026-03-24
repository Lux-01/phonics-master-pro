#!/usr/bin/env python3
"""
Rug-Radar Scalper Strategy
High-frequency micro-cap trading with strict rug filters
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any
import statistics

@dataclass
class Trade:
    symbol: str
    pnl_pct: float
    pnl_sol: float
    entry_reason: str
    exit_reason: str
    day: int
    mcap: float
    age_hours: float
    risk_score: float
    position_size: float

@dataclass
class StrategyState:
    balance: float = 1.0
    trades: List[Trade] = None
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    rugs_avoided: int = 0
    
    def __post_init__(self):
        if self.trades is None:
            self.trades = []

class RugRadarScalper:
    """
    High-frequency scalping with strict rug detection:
    - Micro-cap focus (high volatility)
    - Rapid entry/exit (scalping)
    - Multi-layer rug filters
    - Dynamic position sizing based on risk
    """
    
    def __init__(self, initial_balance: float = 1.0):
        self.state = StrategyState(balance=initial_balance)
        self.learning_params = {
            'min_mcap': 5000,           # Minimum market cap
            'max_mcap': 80000,          # Maximum for micro-cap
            'max_age_hours': 36,        # Fresh tokens only
            'profit_target': 0.08,      # 8% quick profit
            'stop_loss': 0.05,         # 5% tight stop
            'base_position': 0.12,      # 12% base position
            'max_position': 0.25,       # 25% max position
            'rug_threshold': 0.3,       # Max risk score
            'volume_boost': 1.5         # Boost on high volume
        }
        self.performance_history = []
        self.risk_patterns = []
        
    def calculate_risk_score(self, trade_data: Dict) -> float:
        """
        Calculate rug risk score (0-1, higher = riskier)
        """
        risk = 0.0
        
        # Check if already marked as rug
        if trade_data.get('is_rug', False):
            return 1.0
            
        result = trade_data.get('result', '')
        exit_reason = trade_data.get('exit_reason', '').lower()
        
        # Result-based risk
        if 'rug' in result.lower() or 'rug' in exit_reason:
            return 1.0
        if result == 'rug_or_bag':
            risk += 0.4
            
        # Age-based risk (very new = risky)
        age = trade_data.get('age_hours', 999)
        if age < 2:
            risk += 0.25  # Ultra fresh is risky
        elif age > 24:
            risk += 0.1   # Older tokens have different risks
            
        # Market cap risk
        mcap = trade_data.get('mcap', 0)
        if mcap < 10000:
            risk += 0.3  # Very low cap
        elif mcap > 100000:
            risk += 0.05  # Higher cap = safer
            
        # Grade-based adjustment
        grade = trade_data.get('grade', 'C')
        grade_risk = {'A+': 0.0, 'A': 0.05, 'B': 0.15, 'C': 0.3, 'D': 0.5, 'F': 0.7}
        risk += grade_risk.get(grade, 0.3)
        
        # Entry reason analysis
        entry = trade_data.get('entry_reason', '').lower()
        if 'ultra fresh' in entry:
            risk += 0.1
        if 'high 5m volume' in entry:
            risk -= 0.05  # Volume reduces rug risk slightly
            
        return min(risk, 1.0)
    
    def should_enter(self, trade_data: Dict) -> tuple[bool, float]:
        """
        Entry with strict rug filtering
        """
        risk_score = self.calculate_risk_score(trade_data)
        
        # Skip if too risky
        if risk_score > self.learning_params['rug_threshold']:
            return False, risk_score
            
        # Market cap filter
        mcap = trade_data.get('mcap', 0)
        if mcap < self.learning_params['min_mcap'] or mcap > self.learning_params['max_mcap']:
            return False, risk_score
            
        # Age filter
        age = trade_data.get('age_hours', 999)
        if age > self.learning_params['max_age_hours']:
            return False, risk_score
            
        # Only take A/A+ grades for scalping
        grade = trade_data.get('grade', 'C')
        if grade not in ['A+', 'A']:
            return False, risk_score
            
        return True, risk_score
    
    def calculate_position_size(self, risk_score: float, trade_data: Dict) -> float:
        """
        Dynamic position sizing: higher risk = smaller position
        """
        # Base position
        base = self.state.balance * self.learning_params['base_position']
        
        # Risk adjustment (inverse relationship)
        risk_factor = 1 - (risk_score * 0.8)  # Reduce size for high risk
        
        # Volume boost
        entry = trade_data.get('entry_reason', '').lower()
        volume_multiplier = self.learning_params['volume_boost'] if 'high 5m volume' in entry else 1.0
        
        # Grade bonus
        grade = trade_data.get('grade', 'C')
        grade_multiplier = 1.3 if grade == 'A+' else (1.1 if grade == 'A' else 1.0)
        
        position = base * risk_factor * volume_multiplier * grade_multiplier
        max_pos = self.state.balance * self.learning_params['max_position']
        
        return min(position, max_pos, self.state.balance * 0.5)  # Never more than 50%
    
    def execute_trade(self, trade_data: Dict, risk_score: float) -> Dict[str, Any]:
        """
        Execute scalping trade
        """
        result = trade_data.get('result', 'unknown')
        pnl_pct = trade_data.get('pnl_pct', 0)
        pnl_sol = trade_data.get('pnl_sol', 0)
        
        position_size = self.calculate_position_size(risk_score, trade_data)
        
        # Adjust PnL based on actual position size vs assumed
        position_multiplier = position_size / (self.state.balance * 0.1)  # Normalize
        adjusted_pnl_sol = pnl_sol * min(position_multiplier, 1.0)
        
        trade = Trade(
            symbol=trade_data.get('symbol', 'UNKNOWN'),
            pnl_pct=pnl_pct,
            pnl_sol=adjusted_pnl_sol,
            entry_reason=trade_data.get('entry_reason', 'Scalp entry'),
            exit_reason=trade_data.get('exit_reason', 'Scalp exit'),
            day=trade_data.get('day', 0),
            mcap=trade_data.get('mcap', 0),
            age_hours=trade_data.get('age_hours', 0),
            risk_score=risk_score,
            position_size=position_size
        )
        
        self.state.trades.append(trade)
        self.state.total_trades += 1
        
        # Update balance
        if result == 'win':
            self.state.wins += 1
            self.state.balance += adjusted_pnl_sol
        else:
            self.state.losses += 1
            self.state.balance += adjusted_pnl_sol
            
        # Track risk patterns
        self.risk_patterns.append({
            'risk_score': risk_score,
            'pnl': pnl_pct,
            'result': result
        })
            
        return trade_data
    
    def evolve_parameters(self):
        """
        Learning: Adjust risk thresholds based on performance
        """
        if len(self.state.trades) < 12:
            return
            
        recent = self.state.trades[-12:]
        
        # Analyze risk-reward
        low_risk = [t for t in recent if t.risk_score < 0.2]
        high_risk = [t for t in recent if t.risk_score > 0.2]
        
        if low_risk and high_risk:
            low_return = statistics.mean([t.pnl_pct for t in low_risk])
            high_return = statistics.mean([t.pnl_pct for t in high_risk])
            
            # Adjust threshold based on which performs better
            if high_return > low_return * 1.2:
                self.learning_params['rug_threshold'] = min(
                    0.5, self.learning_params['rug_threshold'] * 1.05
                )
            elif low_return > high_return:
                self.learning_params['rug_threshold'] = max(
                    0.2, self.learning_params['rug_threshold'] * 0.97
                )
        
        # Adjust profit target based on holding time
        avg_pnl = statistics.mean([t.pnl_pct for t in recent])
        if avg_pnl > self.learning_params['profit_target'] * 100 * 1.5:
            # We're leaving money on the table
            self.learning_params['profit_target'] = min(
                0.15, self.learning_params['profit_target'] * 1.03
            )
        elif avg_pnl < 0:
            # Taking too much risk
            self.learning_params['profit_target'] = max(
                0.05, self.learning_params['profit_target'] * 0.97
            )
        
        win_rate = self.state.wins / max(self.state.total_trades, 1)
        
        self.performance_history.append({
            'trade_count': len(self.state.trades),
            'win_rate': win_rate,
            'avg_risk': statistics.mean([t.risk_score for t in recent]),
            'params': self.learning_params.copy()
        })
    
    def run_backtest(self, data_path: str) -> Dict[str, Any]:
        """
        Run full backtest
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        print(f"🎯 Rug-Radar Scalper: Processing {len(trades)} trades...")
        
        skipped_rugs = 0
        
        for i, trade_data in enumerate(trades):
            risk_score = self.calculate_risk_score(trade_data)
            
            # Count rugs we avoided
            if risk_score > self.learning_params['rug_threshold']:
                if trade_data.get('result') == 'rug_or_bag' or trade_data.get('is_rug'):
                    skipped_rugs += 1
                    
            should_enter, _ = self.should_enter(trade_data)
            if should_enter:
                self.execute_trade(trade_data, risk_score)
                
                if self.state.total_trades % 15 == 0:
                    self.evolve_parameters()
        
        self.state.rugs_avoided = skipped_rugs
        
        # Calculate rug detection accuracy
        all_risks = [r for r in self.risk_patterns if r['result'] == 'rug_or_bag']
        avg_rug_risk = statistics.mean([r['risk_score'] for r in all_risks]) if all_risks else 0
        
        results = {
            'strategy': 'Rug-Radar Scalper',
            'description': 'High-frequency micro-cap trading with strict rug filters',
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
            'rugs_avoided': skipped_rugs,
            'avg_risk_score': round(
                statistics.mean([t.risk_score for t in self.state.trades]) if self.state.trades else 0, 3
            ),
            'avg_position_size_sol': round(
                statistics.mean([t.position_size for t in self.state.trades]) if self.state.trades else 0, 4
            ),
            'learning_history': self.performance_history,
            'final_params': self.learning_params,
            'trades': [{
                'symbol': t.symbol,
                'pnl_pct': round(t.pnl_pct, 2),
                'pnl_sol': round(t.pnl_sol, 6),
                'risk_score': round(t.risk_score, 3),
                'mcap': t.mcap,
                'day': t.day
            } for t in self.state.trades]
        }
        
        return results


def main():
    scalper = RugRadarScalper(initial_balance=1.0)
    results = scalper.run_backtest('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json')
    
    output_path = '/home/skux/.openclaw/workspace/rug_radar_scalper_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Rug-Radar Scalper Results:")
    print(f"   Initial: 1.0 SOL")
    print(f"   Final: {results['final_balance']:.6f} SOL")
    print(f"   Return: {results['total_return_pct']:+.2f}%")
    print(f"   Trades: {results['total_trades']} (Win rate: {results['win_rate_pct']}%)")
    print(f"   Rugs Avoided: {results['rugs_avoided']}")
    print(f"   Avg Risk Score: {results['avg_risk_score']}")
    print(f"   Results saved to: {output_path}")


if __name__ == '__main__':
    main()
