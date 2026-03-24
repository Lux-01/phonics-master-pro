#!/usr/bin/env python3
"""
🔥 LUXTRADER EVOLVED v3.1 - SELF-IMPROVING TRADING SYSTEM
Evolved from v3.0 with adaptive learning

ACADe Method: Applied
ACA Plan:
1. Requirements: Dynamic sizing, streak tracking, pattern learning, market awareness
2. Architecture: StrategyCore + EvolutionEngine + PatternMemory
3. Data Flow: Signal → Evaluate → Size → Execute → Learn
4. Edge Cases: Drawdowns, streaks, market cycles, pattern gaps
5. Tool Constraints: JSON persistence, safe file ops, no external deps
6. Error Handling: Graceful degradation, safe defaults
7. Testing: Backtest vs v3.0 baseline

Evolution Features (Code Evolution Tracker Pattern EVO-001):
- Streak-based position sizing (+15% per 3 wins)
- Market cycle adaptation (bull/bear/crab)
- Pattern recognition of winning setups
- Dynamic rug detection threshold
- Confidence-adjusted exits
"""

import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum

# Evolution seed for reproducibility
random.seed(42)

# Paths
WORKSPACE = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
EVO_LOG = Path("/home/skux/.openclaw/workspace/memory/code_evolution")


class MarketCycle(Enum):
    """Market condition states"""
    BULL = "bull"
    BEAR = "bear"
    CRAB = "crab"
    RECOVERY = "recovery"


@dataclass
class EvolutionState:
    """Track strategy evolution over time"""
    generation: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    last_evolved: datetime = field(default_factory=datetime.now)
    
    # Dynamic parameters (evolvable)
    streak_threshold: int = 3
    position_base_pct: float = 0.006
    position_max_pct: float = 0.15
    target_tier1: float = 15.0
    target_tier2: float = 25.0
    target_tier3: float = 40.0
    stop_loss_pct: float = 7.0
    rug_threshold: int = 50
    
    # Multipliers
    streak_boost: float = 0.15  # +15% per streak
    bear_mult: float = 0.8      # Reduce targets in bear
    bull_mult: float = 1.2      # Increase targets in bull
    
    # Learning
    mutations: List[str] = field(default_factory=list)


@dataclass  
class PatternSignature:
    """Pattern for learning what works"""
    grade: str
    age_hours: int
    deviation: float
    has_narrative: bool
    market_cycle: str
    
    def to_key(self) -> str:
        # Bucket age and deviation for pattern matching
        age_bucket = "fresh" if self.age_hours < 6 else "mature" if self.age_hours < 24 else "old"
        dev_bucket = "deep_dip" if self.deviation < -0.15 else "dip" if self.deviation < -0.08 else "other"
        return f"{self.grade}_{age_bucket}_{dev_bucket}_{self.has_narrative}_{self.market_cycle}"
    

@dataclass
class TradeOutcome:
    """Single trade result"""
    symbol: str
    entry_capital: float
    exit_capital: float
    pnl_pct: float
    outcome: str  # win/loss/rug
    pattern: PatternSignature
    duration_min: int
    generation: int
    timestamp: datetime = field(default_factory=datetime.now)


class LuxTraderEvolved:
    """
    LuxTrader v3.1 - Evolved with self-improving features
    
    Key Evolutions from v3.0:
    1. Dynamic position sizing based on streaks
    2. Market cycle awareness
    3. Pattern memory of winning setups
    4. Rug-risk scoring
    5. Adaptive confidence scoring
    """
    
    def __init__(self):
        # Core state
        self.capital = 1.0
        self.initial = 1.0
        self.trades = []
        
        # Evolution
        self.dna = EvolutionState()
        
        # Performance tracking
        self.performance = {
            'total': 0,
            'wins': 0,
            'losses': 0,
            'rugs': 0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'best_streak': 0,
            'worst_streak': 0
        }
        
        # Pattern memory
        self.patterns = {}  # {pattern_key: {wins, losses}}
        
        # Market cycle detection
        self.market_cycle = MarketCycle.BULL
        self.cycle_history = []
        
        # Evolution tracking (Code Evolution Skill)
        self.evolution_log = []
        
    def load_data(self) -> List[Dict]:
        """Load 1 year of trade data with market cycles"""
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        with open(data_file) as f:
            data = json.load(f)
        
        return self._synthesize_year(data.get('trades', []))
    
    def _synthesize_year(self, base_trades: List[Dict]) -> List[Dict]:
        """Extend to 12 months with realistic market cycles"""
        extended = list(base_trades)
        
        cycles = [
            ('bull', 1.25, 0.9), ('bull', 1.3, 0.88),
            ('bear', 0.7, 0.55), ('bear', 0.65, 0.5), 
            ('crab', 0.95, 0.62), ('recovery', 1.15, 0.75)
        ]
        
        for i in range(550):
            if i < len(base_trades):
                base = base_trades[i % len(base_trades)].copy()
                cycle_name, mult, win_rate = cycles[min(i // 92, len(cycles) - 1)]
                
                base['id'] = len(extended) + 1
                base['market_cycle'] = cycle_name
                base['symbol'] = f"EVO_{base.get('symbol', 'TOK')}_{i}"
                
                orig_pnl = base.get('pnl_pct', 0)
                noise = random.uniform(0.9, 1.1)
                adjusted = orig_pnl * mult * noise
                adjusted = max(-25, min(60, adjusted))
                
                base['pnl_pct'] = adjusted
                base['outcome'] = 'win' if adjusted > 0 else 'loss'
                
                extended.append(base)
        
        return extended
    
    def detect_market_cycle(self, recent_trades: List[TradeOutcome]) -> MarketCycle:
        """Detect current market condition"""
        if len(recent_trades) < 20:
            return MarketCycle.BULL
        
        # Look at last 20 trades
        last_20 = recent_trades[-20:]
        win_rate = sum(1 for t in last_20 if t.outcome == 'win') / len(last_20)
        avg_pnl = sum(t.pnl_pct for t in last_20) / len(last_20)
        
        if win_rate > 0.75 and avg_pnl > 10:
            return MarketCycle.BULL
        elif win_rate < 0.45 or avg_pnl < -5:
            return MarketCycle.BEAR
        elif 0.5 <= win_rate <= 0.6 and abs(avg_pnl) < 3:
            return MarketCycle.CRAB
        else:
            return MarketCycle.RECOVERY
    
    def calculate_position_size(self, confidence: float) -> float:
        """
        EVOLUTION FEATURE #1: Dynamic position sizing
        Base: 0.6% of capital
        + Streak bonus: +15% per win streak
        + Confidence bonus: scales with score
        - Market penalty: reduced in bear markets
        """
        base = self.capital * self.dna.position_base_pct
        
        # Streak boost
        streak = self.performance['consecutive_wins']
        streak_mult = 1.0 + (min(streak, 5) * self.dna.streak_boost)
        
        # Confidence scale (0.8-1.2x)
        conf_mult = 0.8 + (confidence / 100) * 0.4
        
        # Market cycle adjustment
        cycle_mult = {
            MarketCycle.BULL: 1.2,
            MarketCycle.RECOVERY: 1.1,
            MarketCycle.CRAB: 1.0,
            MarketCycle.BEAR: 0.7
        }.get(self.market_cycle, 1.0)
        
        size = base * streak_mult * conf_mult * cycle_mult
        
        # Apply caps
        max_size = self.capital * self.dna.position_max_pct
        return min(size, max_size)
    
    def calculate_targets(self) -> Tuple[float, float, float]:
        """
        EVOLUTION FEATURE #2: Market-aware exit targets
        Adjust tier targets based on market cycle
        """
        cycle_mult = {
            MarketCycle.BULL: self.dna.bull_mult,
            MarketCycle.RECOVERY: 1.1,
            MarketCycle.CRAB: 1.0,
            MarketCycle.BEAR: self.dna.bear_mult
        }.get(self.market_cycle, 1.0)
        
        t1 = self.dna.target_tier1 * cycle_mult
        t2 = self.dna.target_tier2 * cycle_mult
        t3 = self.dna.target_tier3 * cycle_mult
        
        return t1, t2, t3
    
    def check_rug_risk(self, trade: Dict) -> Tuple[bool, float, str]:
        """
        EVOLUTION FEATURE #3: Dynamic rug detection
        Score 0-100, must pass threshold
        """
        deviation = trade.get('deviation', -0.08)
        age_hours = trade.get('age_hours', 6)
        grade = trade.get('grade', 'B')
        
        score = 70  # Base
        
        # Risk factors
        if deviation < -0.30: score -= 30  # Too deep
        if deviation > 0.20: score -= 25  # Already pumped
        if age_hours > 48: score -= 20      # Too old
        if grade in ['C', 'D']: score -= 35 # Low quality
        if trade.get('holders', 100) < 50: score -= 15  # Low holders
        
        # Safety factors
        if grade == 'A+': score += 25
        if grade == 'A': score += 15
        if trade.get('liquidity', 0) > 10000: score += 10
        
        passed = score >= self.dna.rug_threshold
        return passed, score, "RUG_CHECK_PASS" if passed else f"RUG_RISK_{score}"
    
    def evaluate_trade(self, trade: Dict) -> Tuple[bool, float, str, PatternSignature]:
        """
        EVOLUTION FEATURE #4: Confidence scoring with pattern
        Returns: (should_trade, confidence, reason, pattern)
        """
        grade = trade.get('grade', 'B')
        age_hours = trade.get('age_hours', 6)
        deviation = trade.get('deviation', -0.08)
        symbol = trade.get('token_symbol', 'UNKNOWN')
        cycle = trade.get('market_cycle', 'bull')
        
        # Rug check first
        rug_pass, rug_score, rug_reason = self.check_rug_risk(trade)
        if not rug_pass:
            return False, 0.0, rug_reason, None
        
        # Base score
        score = 40
        
        # Grade weight
        if grade == 'A+': score += 40
        elif grade == 'A': score += 30
        elif grade == 'B': score += 15
        else: score -= 10
        
        # Age (freshness)
        if age_hours < 4: score += 25
        elif age_hours < 8: score += 20
        elif age_hours < 16: score += 10
        else: score -= 5
        
        # Deviation (mean reversion)
        if -0.18 <= deviation <= -0.10: score += 20  # Perfect
        elif -0.25 <= deviation < -0.18: score += 10  # Deep
        elif deviation > 0: score -= 20  # Pumped
        
        # Narrative
        has_narrative = any(k in symbol for k in ['AI', 'MEME', 'AGENT', 'PEPE'])
        if has_narrative: score += 10
        
        # Pattern bonus
        pattern = PatternSignature(grade, age_hours, deviation, has_narrative, cycle)
        pattern_key = pattern.to_key()
        
        if pattern_key in self.patterns:
            p_data = self.patterns[pattern_key]
            if p_data.get('total', 0) >= 3:
                pattern_wr = p_data.get('wins', 0) / p_data.get('total', 1)
                if pattern_wr > 0.7:
                    score += 15  # Proven pattern
                elif pattern_wr < 0.4:
                    score -= 10  # Bad pattern
        
        # Market cycle boost
        cycle_boost = {
            MarketCycle.BULL: 10,
            MarketCycle.RECOVERY: 5,
            MarketCycle.CRAB: 0,
            MarketCycle.BEAR: -5
        }.get(self.market_cycle, 0)
        score += cycle_boost
        
        # Streak bonus
        if self.performance['consecutive_wins'] >= 3:
            score += 8
        
        final_score = min(100, score)
        approved = final_score >= 75 and grade in ['A', 'A+']
        
        reason = f"Grade {grade} | Score {final_score} | {pattern_key}"
        
        return approved, final_score, reason, pattern
    
    def record_pattern(self, pattern: PatternSignature, outcome: str):
        """Learn from outcomes"""
        key = pattern.to_key()
        if key not in self.patterns:
            self.patterns[key] = {'wins': 0, 'losses': 0, 'total': 0}
        
        self.patterns[key]['total'] += 1
        if outcome == 'win':
            self.patterns[key]['wins'] += 1
        else:
            self.patterns[key]['losses'] += 1
    
    def check_evolution(self):
        """
        EVOLUTION FEATURE #5: periodic self-improvement
        Adjust parameters based on performance
        """
        trades = self.performance['total']
        
        if trades % 50 == 0 and trades > 0:
            self.evolve_strategy()
    
    def evolve_strategy(self):
        """Self-mutation to improve performance"""
        win_rate = self.performance['wins'] / max(1, self.performance['total'])
        streak = self.performance['consecutive_wins']
        
        mutations = []
        
        # Adjust position sizing
        if win_rate > 0.75 and streak >= 3:
            self.dna.position_base_pct = min(0.008, self.dna.position_base_pct * 1.1)
            mutations.append(f"Position_base +10%")
        elif win_rate < 0.55:
            self.dna.position_base_pct = max(0.004, self.dna.position_base_pct * 0.9)
            mutations.append(f"Position_base -10%")
        
        # Adjust targets
        if self.market_cycle == MarketCycle.BULL and win_rate > 0.7:
            self.dna.bull_mult = min(1.35, self.dna.bull_mult + 0.05)
            mutations.append(f"Bull_mult +5%")
        elif self.market_cycle == MarketCycle.BEAR and win_rate < 0.5:
            self.dna.bear_mult = max(0.6, self.dna.bear_mult - 0.05)
            mutations.append(f"Bear_mult -5%")
        
        # Tighten/loosen rug threshold
        if self.performance['rugs'] > 0:
            self.dna.rug_threshold = min(60, self.dna.rug_threshold + 2)
            mutations.append(f"Rug_threshold +2")
        elif win_rate > 0.75:
            self.dna.rug_threshold = max(40, self.dna.rug_threshold - 1)
            mutations.append(f"Rug_threshold -1")
        
        # Log evolution
        self.dna.generation += 1
        self.dna.last_evolved = datetime.now()
        self.dna.mutations = mutations
        
        self.evolution_log.append({
            'generation': self.dna.generation,
            'timestamp': datetime.now().isoformat(),
            'win_rate': win_rate,
            'streak': streak,
            'capital': self.capital,
            'mutations': mutations
        })
        
        if mutations:
            print(f"   🔬 Gen {self.dna.generation}: {', '.join(mutations)}")
    
    def execute_trade(self, trade: Dict, confidence: float, pattern: PatternSignature) -> TradeOutcome:
        """Execute with evolved parameters"""
        
        position = self.calculate_position_size(confidence)
        t1, t2, t3 = self.calculate_targets()
        
        # Determine outcome
        pnl = trade.get('pnl_pct', 0)
        
        # Simulate realistic outcome based on confidence
        if pnl > 0:
            if pnl >= t3 * 0.8:
                realized = pnl * 0.95  # Trail captures most
                outcome = 'win'
            elif pnl >= t2:
                realized = pnl * 0.85
                outcome = 'win'
            elif pnl >= t1:
                realized = pnl * 0.90
                outcome = 'win'
            else:
                realized = pnl
                outcome = 'win'
        else:
            realized = max(-15, pnl)  # Rug protection
            if realized < -10:
                outcome = 'rug'
            else:
                outcome = 'loss'
        
        # Update capital
        profit = position * (realized / 100)
        self.capital += profit
        
        # Update stats
        self.performance['total'] += 1
        self.performance['wins'] += 1 if outcome == 'win' else 0
        self.performance['losses'] += 1 if outcome == 'loss' else 0
        self.performance['rugs'] += 1 if outcome == 'rug' else 0
        
        if outcome == 'win':
            self.performance['consecutive_wins'] += 1
            self.performance['consecutive_losses'] = 0
            self.performance['best_streak'] = max(
                self.performance['best_streak'],
                self.performance['consecutive_wins']
            )
        else:
            self.performance['consecutive_losses'] += 1
            self.performance['consecutive_wins'] = 0
            self.performance['worst_streak'] = max(
                self.performance['worst_streak'],
                self.performance['consecutive_losses']
            )
        
        # Learn
        self.record_pattern(pattern, outcome)
        
        return TradeOutcome(
            symbol=trade.get('token_symbol', 'UNKNOWN'),
            entry_capital=self.capital - profit,
            exit_capital=self.capital,
            pnl_pct=realized,
            outcome=outcome,
            pattern=pattern,
            duration_min=random.randint(10, 180),
            generation=self.dna.generation
        )
    
    def run_backtest(self) -> Dict:
        """Run 1-year evolved backtest"""
        
        print("=" * 80)
        print("🔥 LUXTRADER EVOLVED v3.1 - SELF-IMPROVING BACKTEST")
        print("=" * 80)
        print("\n🧬 Evolution Features:")
        print("   1. Streak-aware position sizing (+15%/win streak)")
        print("   2. Market cycle adaptation (bull/bear/crab)")
        print("   3. Pattern recognition (learn winning setups)")
        print("   4. Dynamic rug detection (adaptive threshold)")
        print("   5. Self-evolution (auto-adjusts every 50 trades)")
        
        trades = self.load_data()
        
        print(f"\n💰 Starting: {self.initial} SOL")
        print(f"📊 Trades: {len(trades)}")
        print(f"🧬 Initial DNA: Gen {self.dna.generation}")
        print("-" * 80)
        
        for i, trade in enumerate(trades):
            # Check for evolution
            self.check_evolution()
            
            if i % 100 == 0 and i > 0:
                print(f"   Trade {i} | Cap: {self.capital:.2f} | Gen: {self.dna.generation} | Cycle: {self.market_cycle.value}")
            
            # Detect market cycle
            if i % 50 == 0:
                self.market_cycle = self.detect_market_cycle(self.trades)
            
            # Evaluate
            should_trade, confidence, reason, pattern = self.evaluate_trade(trade)
            
            if should_trade:
                outcome = self.execute_trade(trade, confidence, pattern)
                self.trades.append(outcome)
        
        print("-" * 80)
        
        # Results
        total_pnl = self.capital - self.initial
        roi = (self.capital / self.initial - 1) * 100
        
        print(f"\n🔥 EVOLVED RESULTS:")
        print(f"=" * 80)
        print(f"\n💰 Performance:")
        print(f"   Start: {self.initial:.2f} SOL")
        print(f"   End: {self.capital:.2f} SOL")
        print(f"   P&L: {total_pnl:+.2f} SOL ({roi:+.1f}%)")
        print(f"   Multiplier: {self.capital/self.initial:.1f}x")
        
        print(f"\n📊 Stats:")
        print(f"   Trades: {self.performance['total']}")
        print(f"   Wins: {self.performance['wins']}")
        print(f"   Losses: {self.performance['losses']}")
        print(f"   Rugs: {self.performance['rugs']}")
        if self.performance['total'] > 0:
            print(f"   Win Rate: {self.performance['wins']/self.performance['total']*100:.1f}%")
        print(f"   Best Streak: {self.performance['best_streak']}")
        
        print(f"\n🧬 Final DNA (Gen {self.dna.generation}):")
        print(f"   Position base: {self.dna.position_base_pct:.2%}")
        print(f"   Bull mult: {self.dna.bull_mult:.2f}")
        print(f"   Bear mult: {self.dna.bear_mult:.2f}")
        print(f"   Rug threshold: {self.dna.rug_threshold}")
        
        print(f"\n📈 Evolutions: {len(self.evolution_log)}")
        for evo in self.evolution_log[-3:]:
            if evo['mutations']:
                print(f"   Gen {evo['generation']}: {', '.join(evo['mutations'])}")
        
        print(f"\n🎯 Top Patterns Learned:")
        sorted_patterns = sorted(self.patterns.items(), 
                                key=lambda x: x[1].get('wins', 0) / max(1, x[1].get('total', 1)),
                                reverse=True)
        for key, data in sorted_patterns[:5]:
            wr = data.get('wins', 0) / max(1, data.get('total', 1)) * 100
            if data.get('total', 0) >= 5:
                print(f"   {key}: {wr:.0f}% WR ({data['wins']}/{data['total']})")
        
        # Save results
        results = {
            'strategy': 'LuxTrader Evolved v3.1',
            'features': [
                'Dynamic position sizing',
                'Market cycle adaptation',
                'Pattern learning',
                'Rug detection',
                'Self-evolution'
            ],
            'final_dna': {
                'generation': self.dna.generation,
                'position_base': self.dna.position_base_pct,
                'bull_mult': self.dna.bull_mult,
                'bear_mult': self.dna.bear_mult,
                'rug_threshold': self.dna.rug_threshold
            },
            'performance': self.performance,
            'patterns_learned': len(self.patterns),
            'evolutions': len(self.evolution_log),
            'start_capital': self.initial,
            'end_capital': self.capital,
            'roi_pct': roi,
            'multiplier': self.capital / self.initial,
            'trades': [asdict(t) for t in self.trades[:100]]
        }
        
        output = WORKSPACE / "luxtrader_evolved_results.json"
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Saved to: {output}")
        print("=" * 80)
        
        return results


def main():
    lte = LuxTraderEvolved()
    lte.run_backtest()


if __name__ == "__main__":
    main()
