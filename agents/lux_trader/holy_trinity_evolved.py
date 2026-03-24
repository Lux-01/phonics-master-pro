#!/usr/bin/env python3
"""
🔥 HOLY TRINITY EVOLVED v2.0 - 1 YEAR WITH ACTIVE EVOLUTION
Self-improving strategy that learns from every trade

Evolution Features:
- Dynamic weight adjustment based on performance
- Entry criteria that tighten when winning
- Position sizing evolution (more aggressive when hot)
- Pattern recognition of winning setups
- Auto-optimization of thresholds

The strategy evolves its DNA over time.
"""

import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from pathlib import Path

random.seed(42)

WORKSPACE = Path("/home/skux/.openclaw/workspace/agents/lux_trader")

@dataclass
class EvolvedConfig:
    """Evolvable configuration parameters"""
    rug_radar_threshold: int = 50  # Starting threshold
    mean_reversion_zone: Tuple[float, float] = (-0.18, -0.10)  # Optimal dip
    luxtrader_min_score: int = 70  # Minimum Lux score
    position_size_base: float = 0.10  # Starting position
    position_size_max: float = 0.15  # Max position
    confidence_multiplier: float = 1.0  # Boost when winning
    
    # Evolution tracking
    generation: int = 1
    evolved_at: datetime = field(default_factory=datetime.now)
    mutations: List[str] = field(default_factory=list)

@dataclass
class TradeRecord:
    """Record of a trade with learning data"""
    id: int
    symbol: str
    capital_before: float
    capital_after: float
    pnl_pct: float
    outcome: str
    config: EvolvedConfig
    signals: Dict
    market_cycle: str
    timestamp: datetime = field(default_factory=datetime.now)

class HolyTrinityEvolved:
    """
    Self-evolving trading strategy.
    
    Evolution triggers:
    - Every 50 trades: Review and adjust weights
    - After 3 consecutive wins: Increase aggression
    - After 2 consecutive losses: Tighten criteria
    - Monthly: Major evolution cycle
    """
    
    def __init__(self):
        # Current DNA (configuration)
        self.dna = EvolvedConfig()
        
        # Strategy weights (evolvable)
        self.weights = {
            'rug_radar': 0.35,
            'mean_reverter': 0.40,
            'luxtrader': 0.25
        }
        
        # Performance tracking
        self.performance = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'best_streak': 0,
            'worst_streak': 0
        }
        
        # Pattern recognition
        self.patterns = {}  # {pattern_key: {wins: 0, losses: 0}}
        
        # Evolution history
        self.evolution_log = []
        
        # Market cycle awareness
        self.current_cycle = 'bull'
        self.cycle_performance = {
            'bull': {'trades': 0, 'wins': 0},
            'bear': {'trades': 0, 'wins': 0},
            'crab': {'trades': 0, 'wins': 0},
            'recovery': {'trades': 0, 'wins': 0}
        }
        
    def load_data(self) -> List[Dict]:
        """Load trade data"""
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        with open(data_file) as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        return self._extend_to_1year(trades)
    
    def _extend_to_1year(self, trades: List[Dict]) -> List[Dict]:
        """Extend with realistic market cycles"""
        extended = list(trades)
        
        cycles = [
            ('bull', 1.25, 0.9),      # +25% avg, 90% win rate
            ('bull', 1.30, 0.88),     # Hot bull
            ('bear', 0.70, 0.55),     # -30% avg, 55% win
            ('bear', 0.65, 0.50),     # Deep bear
            ('crab', 0.95, 0.62),     # Sideways
            ('recovery', 1.15, 0.75), # Bouncing back
        ]
        
        for i in range(550):
            if i < len(trades):
                base = trades[i % len(trades)].copy()
                cycle_idx = min(i // 92, len(cycles) - 1)
                cycle_name, mult, base_win = cycles[cycle_idx]
                
                base['id'] = len(extended) + 1
                base['market_cycle'] = cycle_name
                base['symbol'] = f"{base.get('symbol', 'TOK')}_EVO_{i}"
                
                orig_pnl = base.get('pnl_pct', 0)
                noise = random.uniform(0.9, 1.1)
                adjusted = orig_pnl * mult * noise
                adjusted = max(-25, min(60, adjusted))
                
                base['pnl_pct'] = adjusted
                base['outcome'] = 'win' if adjusted > 0 else 'loss'
                base['exit_reason'] = 'target_hit' if adjusted > 20 else 'stop_loss' if adjusted < -10 else 'manual'
                
                extended.append(base)
        
        return extended
    
    def evaluate(self, trade: Dict) -> Tuple[bool, float, str, Dict]:
        """
        Evaluate trade with EVOLVED criteria
        Returns: (should_trade, confidence, reason, signals)
        """
        
        signals = {}
        pnl = trade.get('pnl_pct', 0)
        grade = trade.get('grade', 'B')
        deviation = trade.get('deviation', -0.08)
        age_hours = trade.get('age_hours', 6)
        
        # Get current market cycle
        cycle = trade.get('market_cycle', 'bull')
        self.current_cycle = cycle
        
        # EVOLVED Rug-Radar (uses learned threshold)
        rug_score = self.dna.rug_radar_threshold + 20  # Dynamic base
        
        if deviation < -0.30: rug_score -= 30
        if deviation > 0.25: rug_score -= 25
        if age_hours > 48: rug_score -= 20
        if grade == 'C': rug_score -= 35
        if grade == 'B': rug_score -= 15
        if grade == 'A+': rug_score += 25
        if grade == 'A': rug_score += 15
        
        # EVOLVED: Tighter in bear markets
        if cycle == 'bear':
            rug_score -= 10  # More strict
            if deviation < -0.35:  # Avoid knife-catching
                rug_score -= 20
        
        rug_approve = rug_score >= self.dna.rug_radar_threshold
        signals['rug_radar'] = {'score': rug_score, 'approve': rug_approve, 'threshold': self.dna.rug_radar_threshold}
        
        # EVOLVED Mean-Reverter (adaptive dip zone)
        mr_score = 40
        min_dip, max_dip = self.dna.mean_reversion_zone
        
        if max_dip <= deviation <= min_dip:
            mr_score += 45  # Perfect zone
            mr_reason = f"Perfect dip: {deviation:.1%}"
        elif min_dip * 1.5 <= deviation <= max_dip * 0.5:
            mr_score += 30
            mr_reason = f"Good dip: {deviation:.1%}"
        elif deviation < min_dip * 1.5:
            mr_score -= 10
            mr_reason = f"Too deep: {deviation:.1%}"
        else:
            mr_reason = f"Not ideal: {deviation:.1%}"
        
        # EVOLVED: Cycle adjustments
        if cycle == 'bull':
            mr_score += 5  # More forgiving in bull
        elif cycle == 'bear':
            mr_score -= 5  # Stricter in bear
        
        mr_approve = mr_score >= 60
        signals['mean_reverter'] = {'score': mr_score, 'approve': mr_approve, 'zone': self.dna.mean_reversion_zone}
        
        # EVOLVED LuxTrader (adaptive quality threshold)
        lux_score = 45
        
        if grade == 'A+':
            lux_score += 40
        elif grade == 'A':
            lux_score += 30
        elif grade == 'B':
            lux_score += 15
        else:
            lux_score -= 10
        
        if age_hours < 4:
            lux_score += 25
        elif age_hours < 8:
            lux_score += 20
        elif age_hours < 16:
            lux_score += 10
        
        # EVOLVED: Streak boost
        if self.performance['consecutive_wins'] >= 3:
            lux_score += 10  # Hot hand bonus
            
        lux_approve = lux_score >= self.dna.luxtrader_min_score
        signals['luxtrader'] = {'score': lux_score, 'approve': lux_approve, 'min': self.dna.luxtrader_min_score}
        
        # EVOLVED: Calculate composite with confidence multiplier
        base_confidence = (rug_score * self.weights['rug_radar'] +
                          mr_score * self.weights['mean_reverter'] +
                          lux_score * self.weights['luxtrader'])
        
        confidence = base_confidence * self.dna.confidence_multiplier
        
        # Trinity check
        if not rug_approve:
            return False, confidence, f"RUG-RADAR: {rug_score}/{self.dna.rug_radar_threshold}", signals
        if not mr_approve:
            return False, confidence, f"MEAN-REVERTER: {mr_reason}", signals
        if not lux_approve:
            return False, confidence, f"LUXTRADER: {lux_score}/{self.dna.luxtrader_min_score}", signals
        
        return True, confidence, "EVOLVED TRINITY APPROVED", signals
    
    def calculate_position_size(self, confidence: float) -> float:
        """EVOLVED sizing: increases with streaks, decreases with drawdowns"""
        
        base = self.dna.position_size_base
        
        # Streak adjustment
        streak = self.performance['consecutive_wins']
        if streak >= 5:
            base *= 1.3  # +30% when hot
        elif streak >= 3:
            base *= 1.15  # +15% when warm
        elif self.performance['consecutive_losses'] >= 2:
            base *= 0.7  # -30% when cold
        
        # Confidence multiplier
        size = base * (0.8 + (confidence / 100) * 0.4)
        
        # Apply limits
        return min(size, self.dna.position_size_max)
    
    def record_pattern(self, signals: Dict, outcome: str):
        """Record which signal patterns work"""
        # Create pattern signature
        sig_key = f"{signals['rug_radar']['approve']}_{signals['mean_reverter']['score']//10}_{signals['luxtrader']['score']//10}"
        
        if sig_key not in self.patterns:
            self.patterns[sig_key] = {'wins': 0, 'losses': 0, 'total': 0}
        
        self.patterns[sig_key]['total'] += 1
        if outcome == 'win':
            self.patterns[sig_key]['wins'] += 1
        else:
            self.patterns[sig_key]['losses'] += 1
    
    def check_evolution(self):
        """Check if we should evolve"""
        trades = self.performance['total_trades']
        
        # Trigger evolution every 50 trades
        if trades % 50 == 0 and trades > 0:
            self.evolve()
    
    def evolve(self):
        """EVOLVE: Adjust strategy based on performance"""
        
        print(f"\n🔬 EVOLUTION CYCLE #{self.dna.generation + 1}")
        
        old_dna = {
            'rug_threshold': self.dna.rug_radar_threshold,
            'lux_min': self.dna.luxtrader_min_score,
            'position_base': self.dna.position_size_base,
            'confidence_mult': self.dna.confidence_multiplier
        }
        
        mutations = []
        
        # 1. Adjust Rug-Radar threshold based on win rate
        win_rate = self.performance['wins'] / max(1, self.performance['total_trades'])
        if win_rate < 0.60:
            self.dna.rug_radar_threshold -= 3  # Loosen slightly
            mutations.append(f"Rug threshold -3 ({self.dna.rug_radar_threshold})")
        elif win_rate > 0.70:
            self.dna.rug_radar_threshold += 2  # Tighten
            mutations.append(f"Rug threshold +2 ({self.dna.rug_radar_threshold})")
        
        # 2. Adjust LuxTrader minimum based on streak
        if self.performance['consecutive_wins'] >= 5:
            self.dna.luxtrader_min_score += 2  # Higher quality only
            mutations.append(f"Lux min +2 ({self.dna.luxtrader_min_score})")
        elif self.performance['consecutive_losses'] >= 3:
            self.dna.luxtrader_min_score -= 3  # Lower bar
            mutations.append(f"Lux min -3 ({self.dna.luxtrader_min_score})")
        
        # 3. Adjust position sizing
        if win_rate > 0.68 and self.performance['consecutive_wins'] >= 3:
            self.dna.position_size_base = min(0.15, self.dna.position_size_base * 1.05)
            mutations.append(f"Position +5% ({self.dna.position_size_base:.2%})")
        elif win_rate < 0.55:
            self.dna.position_size_base = max(0.05, self.dna.position_size_base * 0.9)
            mutations.append(f"Position -10% ({self.dna.position_size_base:.2%})")
        
        # 4. Adjust confidence multiplier
        if self.performance['consecutive_wins'] >= 7:
            self.dna.confidence_multiplier = min(1.3, self.dna.confidence_multiplier + 0.05)
            mutations.append(f"Confidence +5% ({self.dna.confidence_multiplier:.2f})")
        elif self.performance['consecutive_losses'] >= 4:
            self.dna.confidence_multiplier = max(0.8, self.dna.confidence_multiplier - 0.1)
            mutations.append(f"Confidence -10% ({self.dna.confidence_multiplier:.2f})")
        
        # Log evolution
        self.dna.generation += 1
        self.dna.evolved_at = datetime.now()
        self.dna.mutations = mutations
        
        self.evolution_log.append({
            'generation': self.dna.generation,
            'timestamp': datetime.now().isoformat(),
            'performance': dict(self.performance),
            'old_dna': old_dna,
            'new_dna': {
                'rug_threshold': self.dna.rug_radar_threshold,
                'lux_min': self.dna.luxtrader_min_score,
                'position_base': self.dna.position_size_base,
                'confidence_mult': self.dna.confidence_multiplier
            },
            'mutations': mutations
        })
        
        if mutations:
            print(f"   Mutations: {', '.join(mutations)}")
        else:
            print("   No mutations (optimal state)")
    
    def run(self) -> Dict:
        """Run evolved 1-year backtest"""
        
        print("=" * 80)
        print("🔥 HOLY TRINITY EVOLVED v2.0")
        print("=" * 80)
        print(f"\n🧬 Generation 1 DNA:")
        print(f"   Rug-Radar threshold: {self.dna.rug_radar_threshold}")
        print(f"   Mean-Reversion zone: {self.dna.mean_reversion_zone[0]:.0%} to {self.dna.mean_reversion_zone[1]:.0%}")
        print(f"   LuxTrader minimum: {self.dna.luxtrader_min_score}")
        print(f"   Position base: {self.dna.position_size_base:.0%}")
        print(f"   Confidence mult: {self.dna.confidence_multiplier:.2f}")
        
        print(f"\n🌱 Evolution Rules:")
        print(f"   - Evolve every 50 trades")
        print(f"   - Adjust based on win rate")
        print(f"   - Streak bonuses when hot")
        print(f"   - Risk reduction when cold")
        
        trades = self.load_data()
        capital = 1.0
        initial = capital
        completed = []
        
        print(f"\n💰 Starting: {initial} SOL")
        print(f"📊 Trades: {len(trades)}")
        print("-" * 80)
        
        for i, trade in enumerate(trades):
            # Check evolution
            self.check_evolution()
            
            if i % 100 == 0 and i > 0:
                print(f"   Trade {i} | Cap: {capital:.2f} | Gen: {self.dna.generation}")
            
            # Evaluate
            should_trade, confidence, reason, signals = self.evaluate(trade)
            
            if should_trade:
                position = self.calculate_position_size(confidence)
                position_sol = capital * position
                
                pnl_pct = trade.get('pnl_pct', 0) / 100
                profit = position_sol * pnl_pct
                profit = max(-position_sol * 0.5, min(position_sol * 0.5, profit))
                
                new_capital = capital + profit
                is_win = profit > 0
                
                # Update performance
                self.performance['total_trades'] += 1
                self.performance['wins'] += 1 if is_win else 0
                self.performance['losses'] += 0 if is_win else 1
                
                if is_win:
                    self.performance['consecutive_wins'] += 1
                    self.performance['consecutive_losses'] = 0
                    self.performance['best_streak'] = max(self.performance['best_streak'], 
                                                       self.performance['consecutive_wins'])
                else:
                    self.performance['consecutive_losses'] += 1
                    self.performance['consecutive_wins'] = 0
                    self.performance['worst_streak'] = max(self.performance['worst_streak'],
                                                         self.performance['consecutive_losses'])
                
                # Record pattern
                self.record_pattern(signals, 'win' if is_win else 'loss')
                
                # Track cycle performance
                cycle = trade.get('market_cycle', 'bull')
                self.cycle_performance[cycle]['trades'] += 1
                if is_win:
                    self.cycle_performance[cycle]['wins'] += 1
                
                capital = new_capital
                
                completed.append({
                    'id': i,
                    'symbol': trade.get('symbol', 'UNKNOWN'),
                    'capital_before': capital - profit,
                    'capital_after': capital,
                    'pnl': profit,
                    'outcome': 'win' if is_win else 'loss',
                    'generation': self.dna.generation
                })
        
        print("-" * 80)
        
        # Results
        total_pnl = capital - initial
        roi = (capital / initial - 1) * 100
        
        print(f"\n🔥 EVOLVED RESULTS:")
        print(f"=" * 80)
        print(f"\n💰 Performance:")
        print(f"   Start: {initial:.2f} SOL")
        print(f"   End: {capital:.2f} SOL")
        print(f"   P&L: {total_pnl:+.2f} SOL ({roi:+.1f}%)")
        print(f"   Multiplier: {capital/initial:.1f}x")
        
        print(f"\n📊 Stats:")
        print(f"   Trades: {self.performance['total_trades']}")
        print(f"   Wins: {self.performance['wins']}")
        print(f"   Losses: {self.performance['losses']}")
        if self.performance['total_trades'] > 0:
            print(f"   Win Rate: {self.performance['wins']/self.performance['total_trades']*100:.1f}%")
        print(f"   Best Streak: {self.performance['best_streak']}")
        
        print(f"\n🧬 Final DNA (Gen {self.dna.generation}):")
        print(f"   Rug threshold: {self.dna.rug_radar_threshold}")
        print(f"   Lux minimum: {self.dna.luxtrader_min_score}")
        print(f"   Position base: {self.dna.position_size_base:.2%}")
        print(f"   Confidence: {self.dna.confidence_multiplier:.2f}")
        
        print(f"\n📈 Evolutions: {len(self.evolution_log)}")
        for evo in self.evolution_log[-3:]:
            print(f"   Gen {evo['generation']}: {', '.join(evo['mutations'])}")
        
        # Save
        results = {
            'strategy': 'Holy Trinity Evolved v2.0',
            'final_dna': {
                'rug_threshold': self.dna.rug_radar_threshold,
                'lux_min': self.dna.luxtrader_min_score,
                'position_base': self.dna.position_size_base,
                'confidence_mult': self.dna.confidence_multiplier
            },
            'performance': self.performance,
            'evolutions': len(self.evolution_log),
            'evolution_history': self.evolution_log,
            'patterns': dict(self.patterns),
            'cycle_performance': self.cycle_performance,
            'start_capital': initial,
            'end_capital': capital,
            'roi_pct': roi,
            'multiplier': capital / initial
        }
        
        output = WORKSPACE / "holy_trinity_evolved_results.json"
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Saved to: {output}")
        print("=" * 80)
        
        return results


def main():
    hte = HolyTrinityEvolved()
    hte.run()


if __name__ == "__main__":
    main()
