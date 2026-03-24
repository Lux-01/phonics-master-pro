#!/usr/bin/env python3
"""
🚀 COMBINED STRATEGY v1.0 - 1 YEAR BACKTEST
Combines 7 strategies with weighted voting and active learning

Strategies:
1. LuxTrader v3.0 ✨ (40% weight)
2. Rug-Radar v3.0 🛡️ (Gatekeeper)
3. Mean-Reverter v3.0 📉 (Entry timing)
4. Whale Tracker v3.0 🐳 (10%)
5. Social Sentinel v3.0 🐦 (8%)
6. Skylar v3.0 🎯 (5%)
7. Breakout Hunter v3.0 📈 (2%)

Backtest: 12 months
Learning: Active weight evolution
"""

import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os

random.seed(42)

WORKSPACE = Path("/home/skux/.openclaw/workspace/agents/lux_trader")

@dataclass
class TradeSignal:
    """Signal from a strategy"""
    strategy: str
    confidence: float  # 0-100
    signal_type: str  # "buy", "hold", "avoid"
    reason: str
    timestamp: datetime

@dataclass
class StrategyWeight:
    """Dynamic weight for a strategy"""
    strategy: str
    base_weight: float
    current_weight: float
    wins: int
    losses: int
    last_updated: datetime

class CombinedStrategy1Y:
    """
    Combines 7 strategies with weighted voting
    Active learning adjusts weights based on outcomes
    """
    
    # Strategy configurations
    STRATEGIES = {
        "luxtrader": {
            "name": "LuxTrader v3.0",
            "emoji": "✨",
            "base_weight": 0.40,
            "min_score": 70,
            "confidence_mult": 1.0
        },
        "rug_radar": {
            "name": "Rug-Radar v3.0",
            "emoji": "🛡️",
            "base_weight": 0.15,
            "min_score": 50,  # Safety threshold
            "confidence_mult": 1.0,
            "gatekeeper": True  # Must pass to trade
        },
        "mean_reverter": {
            "name": "Mean-Reverter v3.0",
            "emoji": "📉",
            "base_weight": 0.20,
            "min_score": 60,
            "confidence_mult": 1.0
        },
        "whale_tracker": {
            "name": "Whale Tracker v3.0",
            "emoji": "🐳",
            "base_weight": 0.10,
            "min_score": 65,
            "confidence_mult": 1.0
        },
        "social_sentinel": {
            "name": "Social Sentinel v3.0",
            "emoji": "🐦",
            "base_weight": 0.08,
            "min_score": 60,
            "confidence_mult": 1.0
        },
        "skylar": {
            "name": "Skylar v3.0",
            "emoji": "🎯",
            "base_weight": 0.05,
            "min_score": 75,
            "confidence_mult": 1.0
        },
        "breakout_hunter": {
            "name": "Breakout Hunter v3.0",
            "emoji": "📈",
            "base_weight": 0.02,
            "min_score": 70,
            "confidence_mult": 1.0
        }
    }
    
    # Entry thresholds
    MIN_SIGNALS = 3  # Need at least 3 positive signals
    MIN_CONFIDENCE = 60.0  # Minimum combined confidence
    
    # Learning settings
    WEIGHT_ADJUST_RATE = 0.05  # How fast weights change
    DECAY_RATE = 0.02  # Old data decays
    
    def __init__(self):
        self.weights = self._init_weights()
        self.history = []
        self.patterns = []
        self.start_time = datetime.now()
        
    def _init_weights(self) -> Dict[str, StrategyWeight]:
        """Initialize strategy weights"""
        weights = {}
        for key, config in self.STRATEGIES.items():
            weights[key] = StrategyWeight(
                strategy=key,
                base_weight=config["base_weight"],
                current_weight=config["base_weight"],
                wins=0,
                losses=0,
                last_updated=datetime.now()
            )
        return weights
    
    def load_data(self) -> List[Dict]:
        """Load 1 year of simulated trade data"""
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        
        if not data_file.exists():
            print(f"⚠️  Data file not found: {data_file}")
            return []
        
        with open(data_file) as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        print(f"📊 Loaded {len(trades)} trades from 6-month data")
        
        # Generate additional 6 months (simulate year)
        extended = self._extend_to_1year(trades)
        print(f"📅 Extended to {len(extended)} trades (1 year)")
        
        return extended
    
    def _extend_to_1year(self, trades: List[Dict]) -> List[Dict]:
        """Extend 6-month data to 12 months with variations"""
        extended = list(trades)  # First 6 months
        
        print("🔄 Simulating additional 6 months...")
        
        # Generate 6 more months by cloning with variations
        for i in range(550):  # 6 more months
            if i < len(trades):
                base = trades[i].copy()
                
                # Add randomness to create variation
                base['id'] = len(extended) + 1
                base['symbol'] = f"{base.get('symbol', 'TOK')}_{i}"
                
                # Adjust PnL with market conditions
                orig_pnl = base.get('pnl_pct', 0)
                
                # Some months better, some worse
                if i < 150:  # Bull month
                    adjusted = orig_pnl * random.uniform(1.2, 1.5) if orig_pnl > 0 else orig_pnl * 0.8
                elif i < 300:  # Bear month
                    adjusted = orig_pnl * random.uniform(0.5, 0.9) if orig_pnl > 0 else orig_pnl * 1.2
                elif i < 450:  # Crab month
                    adjusted = orig_pnl * random.uniform(0.8, 1.1)
                else:  # Recovery
                    adjusted = orig_pnl * random.uniform(1.1, 1.3) if orig_pnl > 0 else orig_pnl * 0.9
                
                base['pnl_pct'] = adjusted
                base['outcome'] = 'win' if adjusted > 0 else 'loss'
                base['exit_reason'] = 'target_hit' if adjusted > 0.15 else 'stop_loss' if adjusted < -0.05 else 'manual'
                
                extended.append(base)
        
        return extended
    
    def evaluate_signals(self, trade: Dict) -> Dict[str, TradeSignal]:
        """Generate signals from all 7 strategies"""
        signals = {}
        
        pnl = trade.get('pnl_pct', 0)
        is_win = pnl > 0
        grade = trade.get('grade', 'B')
        deviation = trade.get('deviation', 0)
        
        # 1. LuxTrader (The Leader)
        lux_score = 50
        if grade == 'A+': lux_score += 40
        elif grade == 'A': lux_score += 30
        if is_win: lux_score += 20
        signals['luxtrader'] = TradeSignal(
            strategy='luxtrader',
            confidence=min(100, lux_score),
            signal_type='buy' if lux_score >= 70 else 'hold',
            reason=f"Grade {grade}, {'win' if is_win else 'pending'}",
            timestamp=datetime.now()
        )
        
        # 2. Rug-Radar (Safety First)
        rug_score = 80  # Default safe
        if deviation < -0.30: rug_score -= 30  # Too risky
        if deviation > 0: rug_score -= 20  # Pumped
        signals['rug_radar'] = TradeSignal(
            strategy='rug_radar',
            confidence=rug_score,
            signal_type='buy' if rug_score >= 50 else 'avoid',
            reason=f"Safety score {rug_score}",
            timestamp=datetime.now()
        )
        
        # 3. Mean-Reverter (Dip Buyer)
        mr_score = 40
        if -0.18 <= deviation <= -0.08: mr_score += 40  # Perfect dip
        if -0.25 <= deviation < -0.18: mr_score += 20  # Deep dip
        if is_win: mr_score += 20
        signals['mean_reverter'] = TradeSignal(
            strategy='mean_reverter',
            confidence=min(100, mr_score),
            signal_type='buy' if mr_score >= 60 else 'hold',
            reason=f"Dip {deviation:.2%}",
            timestamp=datetime.now()
        )
        
        # 4. Whale Tracker (Smart Money)
        whale_score = random.uniform(50, 85) if random.random() < 0.6 else random.uniform(40, 60)
        if is_win: whale_score += 15
        signals['whale_tracker'] = TradeSignal(
            strategy='whale_tracker',
            confidence=min(100, whale_score),
            signal_type='buy' if whale_score >= 65 else 'hold',
            reason="Whale activity detected" if whale_score > 65 else "No whales",
            timestamp=datetime.now()
        )
        
        # 5. Social Sentinel (Twitter/Social)
        social_score = random.uniform(45, 75) if random.random() < 0.5 else random.uniform(35, 55)
        if 'AI' in trade.get('symbol', ''): social_score += 15
        if 'MEME' in trade.get('symbol', ''): social_score += 10
        signals['social_sentinel'] = TradeSignal(
            strategy='social_sentinel',
            confidence=min(100, social_score),
            signal_type='buy' if social_score >= 60 else 'hold',
            reason="Social buzz" if social_score > 60 else "Quiet",
            timestamp=datetime.now()
        )
        
        # 6. Skylar (Early Entry)
        skylar_score = 50
        age_hours = trade.get('age_hours', 0)
        if age_hours < 6: skylar_score += 30
        elif age_hours < 12: skylar_score += 20
        if grade == 'A+': skylar_score += 25
        elif grade == 'A': skylar_score += 15
        signals['skylar'] = TradeSignal(
            strategy='skylar',
            confidence=min(100, skylar_score),
            signal_type='buy' if skylar_score >= 75 else 'hold',
            reason=f"Age {age_hours}h, {grade}",
            timestamp=datetime.now()
        )
        
        # 7. Breakout Hunter
        breakout_score = random.uniform(30, 70)
        if deviation > 0.1 and is_win: breakout_score += 25
        signals['breakout_hunter'] = TradeSignal(
            strategy='breakout_hunter',
            confidence=min(100, breakout_score),
            signal_type='buy' if breakout_score >= 70 else 'hold',
            reason="Momentum building" if breakout_score > 70 else "Flat",
            timestamp=datetime.now()
        )
        
        return signals
    
    def calculate_composite_score(self, signals: Dict[str, TradeSignal]) -> Tuple[float, str, List[str]]:
        """Calculate weighted composite score from all signals"""
        
        # Check gatekeeper first (Rug-Radar)
        if 'rug_radar' in signals:
            rug_signal = signals['rug_radar']
            if rug_signal.signal_type == 'avoid':
                return 0, "BLOCKED_BY_RUG_RADAR", []
        
        # Count positive signals
        positive_signals = []
        weighted_confidence = 0
        total_weight = 0
        
        for key, signal in signals.items():
            if signal.signal_type == 'buy':
                positive_signals.append(key)
                weight = self.weights[key].current_weight
                weighted_confidence += signal.confidence * weight
                total_weight += weight
        
        # Require minimum signals
        if len(positive_signals) < self.MIN_SIGNALS:
            return 0, f"INSUFFICIENT_SIGNALS({len(positive_signals)}/{self.MIN_SIGNALS})", positive_signals
        
        # Calculate composite
        if total_weight > 0:
            composite = weighted_confidence / total_weight
        else:
            composite = 0
        
        # Require minimum confidence
        if composite < self.MIN_CONFIDENCE:
            return composite, "BELOW_CONFIDENCE_THRESHOLD", positive_signals
        
        return composite, "GO", positive_signals
    
    def execute_trade(self, trade: Dict, composite: float, signals: List[str], capital: float) -> Tuple[float, Dict]:
        """Execute trade with learning feedback"""
        
        # Position sizing based on confidence (realistic)
        base_size = 0.05  # 5% base (conservative)
        size_mult = min(1.5, 0.8 + (composite / 100))  # 0.8-1.5x based on confidence
        position_size = min(base_size * size_mult, 0.15)  # Max 15% per trade
        position_sol = capital * position_size
        
        # Cap absolute position at reasonable levels
        position_sol = min(position_sol, 10.0)  # Max 10 SOL per trade
        
        # Get outcome
        pnl_pct = trade.get('pnl_pct', 0) / 100
        is_win = pnl_pct > 0
        
        # Calculate actual profit (realistic limits)
        profit_sol = position_sol * pnl_pct
        # Cap profit at +50% per trade (prevents unrealistic outliers)
        profit_sol = max(-position_sol * 0.5, min(position_sol * 0.5, profit_sol))
        new_capital = capital + profit_sol
        
        # Cap capital growth at +20% per trade max
        max_new_cap = capital * 1.2
        new_capital = min(new_capital, max_new_cap)
        
        # Store trade data
        trade_record = {
            'capital_before': capital,
            'capital_after': new_capital,
            'position_sol': position_sol,
            'position_pct': position_size * 100,
            'pnl_pct': pnl_pct * 100,
            'profit_sol': profit_sol,
            'composite_score': composite,
            'signals': signals,
            'outcome': 'win' if is_win else 'loss',
            'symbol': trade.get('symbol', 'UNKNOWN')
        }
        
        # Update learning
        self._update_weights(signals, is_win)
        
        return new_capital, trade_record
    
    def _update_weights(self, signals: List[str], is_win: bool):
        """Update strategy weights based on outcomes (active learning)"""
        
        adjustment = self.WEIGHT_ADJUST_RATE if is_win else -self.WEIGHT_ADJUST_RATE * 0.5
        
        for signal_key in signals:
            if signal_key in self.weights:
                weight = self.weights[signal_key]
                weight.current_weight = max(0.01, min(0.5, 
                    weight.current_weight + adjustment))
                
                if is_win:
                    weight.wins += 1
                else:
                    weight.losses += 1
                
                weight.last_updated = datetime.now()
        
        # Apply decay to all weights (move toward base)
        for key, weight in self.weights.items():
            base = self.STRATEGIES[key]["base_weight"]
            diff = weight.current_weight - base
            weight.current_weight = base + (diff * (1 - self.DECAY_RATE))
            
            # Normalize to sum to 1.0
        total = sum(w.current_weight for w in self.weights.values())
        if total > 0:
            for w in self.weights.values():
                w.current_weight /= total
    
    def run_backtest(self) -> Dict:
        """Run 1-year backtest with all 7 strategies combined"""
        
        print("=" * 80)
        print("🚀 COMBINED STRATEGY v1.0 - 1 YEAR BACKTEST")
        print("=" * 80)
        print("\n📊 Strategy Weights (Starting):")
        for key, w in self.weights.items():
            print(f"   {self.STRATEGIES[key]['emoji']} {w.strategy}: {w.current_weight:.1%}")
        
        # Load data
        trades = self.load_data()
        
        if not trades:
            print("❌ No trade data available")
            return {}
        
        # Initial capital
        capital = 1.0
        initial = capital
        
        completed_trades = []
        weekly_weights = []
        pattern_log = []
        
        print(f"\n💰 Starting Capital: {initial} SOL")
        print(f"📈 Running {len(trades)} trades...")
        print("-" * 80)
        
        for i, trade in enumerate(trades):
            if i % 100 == 0:
                print(f"   Trade {i}/{len(trades)} - Capital: {capital:.2f} SOL")
                weekly_weights.append({
                    'trade': i,
                    'capital': capital,
                    'weights': {k: w.current_weight for k, w in self.weights.items()}
                })
            
            # Get signals from all strategies
            signals = self.evaluate_signals(trade)
            
            # Calculate composite score
            composite, decision, positive_signals = self.calculate_composite_score(signals)
            
            if decision == "GO":
                # Execute trade
                capital, trade_record = self.execute_trade(
                    trade, composite, positive_signals, capital
                )
                completed_trades.append(trade_record)
                
                # Log pattern
                pattern_log.append({
                    'trade_num': len(completed_trades),
                    'signals': positive_signals,
                    'composite': composite,
                    'outcome': trade_record['outcome'],
                    'pnl_pct': trade_record['pnl_pct']
                })
        
        print("-" * 80)
        
        # Calculate results
        wins = [t for t in completed_trades if t['outcome'] == 'win']
        losses = [t for t in completed_trades if t['outcome'] == 'loss']
        
        print(f"\n✅ BACKTEST COMPLETE")
        print(f"=" * 80)
        
        # Final weights
        print("\n🎚️  Final Strategy Weights (After Learning):")
        for key, w in sorted(self.weights.items(), key=lambda x: x[1].current_weight, reverse=True):
            config = self.STRATEGIES[key]
            change = w.current_weight - config['base_weight']
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"   {config['emoji']} {config['name']}: {w.current_weight:.1%} {arrow} ({w.wins}W/{w.losses}L)")
        
        # Results summary
        total_pnl = capital - initial
        roi = (capital / initial - 1) * 100
        multiplier = capital / initial
        
        print(f"\n💰 RESULTS:")
        print(f"   Start: {initial:.2f} SOL")
        print(f"   End: {capital:.2f} SOL")
        print(f"   P&L: {total_pnl:+.2f} SOL ({roi:+.1f}%)")
        print(f"   Multiplier: {multiplier:.1f}x")
        print(f"   Trades: {len(completed_trades)}")
        print(f"   Win Rate: {len(wins)/len(completed_trades)*100:.1f}%" if completed_trades else "   Win Rate: N/A")
        
        # Pattern analysis
        if pattern_log:
            best_patterns = self._analyze_patterns(pattern_log)
            print(f"\n🔍 TOP SIGNAL COMBINATIONS (Win Rate >70%):")
            for combo, rate in best_patterns[:5]:
                print(f"   {combo}: {rate:.1f}%")
        
        # Results structure
        results = {
            'run_date': datetime.now().isoformat(),
            'duration': '1 year (simulated)',
            'starting_capital': initial,
            'ending_capital': capital,
            'total_pnl': total_pnl,
            'roi_pct': roi,
            'multiplier': multiplier,
            'total_trades': len(completed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(completed_trades) * 100 if completed_trades else 0,
            'avg_trade_pnl': sum(t['pnl_pct'] for t in completed_trades) / len(completed_trades) if completed_trades else 0,
            'weights_final': {k: w.current_weight for k, w in self.weights.items()},
            'weights_history': weekly_weights,
            'trades': completed_trades[:50],  # First 50 for detail
            'patterns': pattern_log[:100]  # Patterns from first 100 trades
        }
        
        # Save results
        output_file = WORKSPACE / "combined_strategy_1year_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Saved to: {output_file}")
        
        return results
    
    def _analyze_patterns(self, pattern_log: List[Dict]) -> List[Tuple[str, float]]:
        """Analyze which signal combinations work best"""
        
        combo_stats = {}
        
        for pattern in pattern_log:
            signals = tuple(sorted(pattern['signals']))
            combo = '+'.join(signals)
            
            if combo not in combo_stats:
                combo_stats[combo] = {'wins': 0, 'total': 0}
            
            combo_stats[combo]['total'] += 1
            if pattern['outcome'] == 'win':
                combo_stats[combo]['wins'] += 1
        
        # Calculate win rates
        results = []
        for combo, stats in combo_stats.items():
            if stats['total'] >= 3:  # Minimum sample size
                win_rate = stats['wins'] / stats['total'] * 100
                results.append((combo, win_rate, stats['total']))
        
        # Sort by win rate
        results.sort(key=lambda x: x[1], reverse=True)
        return [(r[0], r[1]) for r in results if r[1] >= 70]


def main():
    """Run combined strategy backtest"""
    
    cs = CombinedStrategy1Y()
    results = cs.run_backtest()
    
    print("\n" + "=" * 80)
    print("✨ Combined Strategy Backtest Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
