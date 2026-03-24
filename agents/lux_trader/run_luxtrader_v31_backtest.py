#!/usr/bin/env python3
"""
🔥 LUXTRADER V3.1 COMPREHENSIVE BACKTEST
6 Month vs 1 Year Comparison
"""

import json
import random
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple
from pathlib import Path
import copy

random.seed(42)

WORKSPACE = Path("/home/skux/.openclaw/workspace/agents/lux_trader")

class LuxTraderBacktester:
    """Comprehensive backtest for LuxTrader v3.1"""
    
    def __init__(self):
        self.results_6mo = {}
        self.results_1yr = {}
        
    def load_6month_data(self) -> List[Dict]:
        """Load original 6-month backtest data"""
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        with open(data_file) as f:
            data = json.load(f)
        return data.get('trades', []), data.get('trades', [])
    
    def synthesize_12_months(self, base_trades: List[Dict]) -> List[Dict]:
        """Extend to 12 months with market cycles"""
        # First 6 months: original data
        extended = list(base_trades[:550])
        
        # Next 6 months: simulated cycles
        cycles = [
            ('bull', 1.25, 0.9),
            ('bull', 1.30, 0.88),
            ('bear', 0.70, 0.55),
            ('bear', 0.65, 0.50),
            ('crab', 0.95, 0.62),
            ('recovery', 1.15, 0.75),
        ]
        
        # Add additional 550 trades (months 7-12)
        for i in range(550, 1100):
            base = copy.deepcopy(base_trades[i % len(base_trades)])
            cycle_idx = min((i - 550) // 92, len(cycles) - 1)
            cycle_name, mult, win_rate = cycles[cycle_idx]
            
            base['id'] = i + 1
            base['market_cycle'] = cycle_name
            base['symbol'] = f"{base.get('symbol', 'TOK')}_Y2_{i}"
            
            # Adjust PnL by cycle
            orig_pnl = base.get('pnl_pct', 0)
            noise = random.uniform(0.9, 1.1)
            adjusted = orig_pnl * mult * noise
            adjusted = max(-25, min(60, adjusted))
            
            base['pnl_pct'] = adjusted
            base['outcome'] = 'win' if adjusted > 0 else 'loss'
            
            extended.append(base)
        
        return extended
    
    def run_6month_backtest(self) -> Dict:
        """Run 6-month backtest with LuxTrader v3.1 logic"""
        print("\n" + "="*80)
        print("📅 6 MONTH BACKTEST - LUXTRADER V3.1")
        print("="*80)
        
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        with open(data_file) as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        # Initialize
        capital = 1.0
        initial = 1.0
        total_trades = 0
        wins = 0
        losses = 0
        rugs = 0
        
        # Evolved parameters
        position_base = 0.006  # 0.6%
        streak = 0
        best_streak = 0
        
        # Track by condition
        grade_perf = {'A+': {'wins': 0, 'total': 0}, 'A': {'wins': 0, 'total': 0}}
        cycle_perf = {'bull': 0, 'bear': 0, 'crab': 0, 'recovery': 0}
        
        for trade in trades:
            # Basic evaluation (simplified v3.1)
            grade = trade.get('grade', 'B')
            deviation = trade.get('deviation', -0.08)
            age_hours = trade.get('age_hours', 6)
            cycle = trade.get('market_cycle', 'bull')
            
            # Evolved entry criteria
            score = 40
            if grade == 'A+': score += 40
            elif grade == 'A': score += 30
            elif grade == 'B': score += 15
            else: score -= 10
            
            if age_hours < 4: score += 25
            elif age_hours < 8: score += 20
            elif age_hours < 16: score += 10
            else: score -= 5
            
            if -0.18 <= deviation <= -0.10: score += 15
            if deviation > 0: score -= 20
            
            # Streak bonus
            if streak >= 3: score += 8
            
            # Evolved position
            position_size = position_base
            streak_boost = min(streak, 5) * 0.15
            position_size *= (1 + streak_boost)
            
            # Market cycle
            if cycle == 'bull':
                position_size *= 1.2
                score += 10
            elif cycle == 'bear':
                position_size *= 0.7
                score -= 5
            elif cycle == 'recovery':
                position_size *= 1.1
                score += 5
            
            approved = score >= 75 and grade in ['A', 'A+']
            
            if approved:
                position_sol = capital * position_size
                pnl = trade.get('pnl_pct', 0)
                
                profit = position_sol * (pnl / 100)
                profit = max(-position_sol * 0.5, min(position_sol * 0.5, profit))
                
                capital += profit
                total_trades += 1
                
                if profit > 0:
                    wins += 1
                    streak += 1
                    best_streak = max(best_streak, streak)
                else:
                    losses += 1
                    if profit < -10:
                        rugs += 1
                    streak = 0
                
                # Track grade performance
                if grade in grade_perf:
                    grade_perf[grade]['total'] += 1
                    if profit > 0:
                        grade_perf[grade]['wins'] += 1
        
        results = {
            'period': '6_months',
            'start_capital': initial,
            'end_capital': capital,
            'roi_pct': (capital / initial - 1) * 100,
            'multiplier': capital / initial,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'rugs': rugs,
            'win_rate': wins / total_trades * 100 if total_trades > 0 else 0,
            'best_streak': best_streak,
            'grade_performance': grade_perf,
            'cycles_tested': cycle_perf
        }
        
        self.results_6mo = results
        self._print_results(results, "6 MONTHS")
        return results
    
    def run_1year_backtest(self) -> Dict:
        """Run 12-month backtest"""
        print("\n" + "="*80)
        print("📅 12 MONTH BACKTEST - LUXTRADER V3.1")
        print("="*80)
        
        # Load and extend data
        data_file = WORKSPACE / "skylar_6month_backtest.json"
        with open(data_file) as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        trades_12mo = self.synthesize_12_months(trades)
        
        print(f"   Total trades: 1,100 (6mo real + 6mo simulated)")
        
        # Initialize
        capital = 1.0
        initial = 1.0
        total_trades = 0
        wins = 0
        losses = 0
        rugs = 0
        
        position_base = 0.006
        streak = 0
        best_streak = 0
        
        # Track by period
        period_perf = {
            'months_1_6': {'trades': 0, 'wins': 0, 'capital_end': 0},
            'months_7_12': {'trades': 0, 'wins': 0, 'capital_end': 0}
        }
        
        month_6_capital = 0
        
        for i, trade in enumerate(trades_12mo):
            grade = trade.get('grade', 'B')
            deviation = trade.get('deviation', -0.08)
            age_hours = trade.get('age_hours', 6)
            cycle = trade.get('market_cycle', 'bull')
            
            # Scoring (same as 6mo)
            score = 40
            if grade == 'A+': score += 40
            elif grade == 'A': score += 30
            elif grade == 'B': score += 15
            else: score -= 10
            
            if age_hours < 4: score += 25
            elif age_hours < 8: score += 20
            elif age_hours < 16: score += 10
            else: score -= 5
            
            if -0.18 <= deviation <= -0.10: score += 15
            if deviation > 0: score -= 20
            
            if streak >= 3: score += 8
            
            # Dynamic position
            position_size = position_base
            streak_boost = min(streak, 5) * 0.15
            position_size *= (1 + streak_boost)
            
            if cycle == 'bull':
                position_size *= 1.2
                score += 10
            elif cycle == 'bear':
                position_size *= 0.7
                score -= 5
            elif cycle == 'recovery':
                position_size *= 1.1
                score += 5
            
            approved = score >= 75 and grade in ['A', 'A+']
            
            if approved:
                position_sol = capital * position_size
                pnl = trade.get('pnl_pct', 0)
                
                profit = position_sol * (pnl / 100)
                profit = max(-position_sol * 0.5, min(position_sol * 0.5, profit))
                
                capital += profit
                total_trades += 1
                
                # Track by period
                if i < 550:
                    period_perf['months_1_6']['trades'] += 1
                    period_perf['months_1_6']['wins'] += 1 if profit > 0 else 0
                    if i == 549:
                        period_perf['months_1_6']['capital_end'] = capital
                        month_6_capital = capital
                else:
                    period_perf['months_7_12']['trades'] += 1
                    period_perf['months_7_12']['wins'] += 1 if profit > 0 else 0
                
                if profit > 0:
                    wins += 1
                    streak += 1
                    best_streak = max(best_streak, streak)
                else:
                    losses += 1
                    if profit < -10:
                        rugs += 1
                    streak = 0
        
        period_perf['months_7_12']['capital_end'] = capital
        
        results = {
            'period': '12_months',
            'start_capital': initial,
            'end_capital': capital,
            'roi_pct': (capital / initial - 1) * 100,
            'multiplier': capital / initial,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'rugs': rugs,
            'win_rate': wins / total_trades * 100 if total_trades > 0 else 0,
            'best_streak': best_streak,
            'month_6_capital': month_6_capital,
            'month_6_roi': (month_6_capital / initial - 1) * 100,
            'month_6_12_roi': (capital / month_6_capital - 1) * 100 if month_6_capital > 0 else 0,
            'period_performance': period_perf
        }
        
        self.results_1yr = results
        self._print_results(results, "12 MONTHS")
        return results
    
    def _print_results(self, results: Dict, label: str):
        """Print formatted results"""
        print(f"\n📊 {label} RESULTS:")
        print("-" * 40)
        print(f"   💰 Capital: {results['start_capital']:.2f} → {results['end_capital']:.2f} SOL")
        print(f"   📈 ROI: {results['roi_pct']:+.1f}%")
        print(f"   🚀 Multiplier: {results['multiplier']:.1f}x")
        print(f"   📊 Trades: {results['total_trades']:,}")
        print(f"   ✅ Wins: {results['wins']}")
        print(f"   ❌ Losses: {results['losses']}")
        print(f"   💀 Rugs: {results['rugs']}")
        print(f"   🎯 Win Rate: {results['win_rate']:.1f}%")
        print(f"   🔥 Best Streak: {results['best_streak']}")
    
    def generate_comparison_report(self):
        """Generate detailed comparison"""
        print("\n" + "="*80)
        print("🔬 6 MONTH vs 12 MONTH COMPARISON")
        print("="*80)
        
        if not self.results_6mo or not self.results_1yr:
            print("   ⚠️ Run both backtests first!")
            return
        
        results_6 = self.results_6mo
        results_12 = self.results_1yr
        
        print("\n📊 SIDE-BY-SIDE:")
        print("-" * 80)
        print(f"{'Metric':20} | {'6 Months':20} | {'12 Months':20} | {'Change'}")
        print("-" * 80)
        
        metrics = [
            ('Start Capital', f"{results_6['start_capital']:.2f} SOL", f"{results_12['start_capital']:.2f} SOL", "="),
            ('End Capital', f"{results_6['end_capital']:.2f} SOL", f"{results_12['end_capital']:.2f} SOL", 
             f"{(results_12['end_capital'] - results_6['end_capital']):+.2f}"),
            ('ROI', f"{results_6['roi_pct']:+.1f}%", f"{results_12['roi_pct']:+.1f}%", 
             f"{(results_12['roi_pct'] - results_6['roi_pct']):+.1f}%"),
            ('Multiplier', f"{results_6['multiplier']:.1f}x", f"{results_12['multiplier']:.1f}x", 
             f"{(results_12['multiplier'] - results_6['multiplier']):+.1f}x"),
            ('Total Trades', f"{results_6['total_trades']}", f"{results_12['total_trades']}", 
             f"+{results_12['total_trades'] - results_6['total_trades']}"),
            ('Win Rate', f"{results_6['win_rate']:.1f}%", f"{results_12['win_rate']:.1f}%", 
             f"{(results_12['win_rate'] - results_6['win_rate']):+.1f}%"),
            ('Best Streak', f"{results_6['best_streak']}", f"{results_12['best_streak']}", 
             f"{results_12['best_streak'] - results_6['best_streak']}"),
        ]
        
        for metric, m6, m12, change in metrics:
            print(f"{metric:<20} | {m6:>20} | {m12:>20} | {change}")
        
        # Period analysis
        print("\n\n📅 PERIOD PERFORMANCE (12 Month):")
        print("-" * 80)
        print(f"   Months 1-6:   {results_12['period_performance']['months_1_6']['trades']} trades")
        print(f"                  ROI: {results_12['month_6_roi']:.1f}%")
        print(f"   Months 7-12:  {results_12['period_performance']['months_7_12']['trades']} trades")
        print(f"                  ROI: {results_12['month_6_12_roi']:.1f}%")
        
        # Annualized comparison
        mo6_annualized = results_6['multiplier'] ** 2
        mo12_actual = results_12['multiplier']
        
        print(f"\n\n📊 ANNUALIZED COMPARISON:")
        print("-" * 80)
        print(f"   6-Month (annualized): {mo6_annualized:.1f}x")
        print(f"   12-Month (actual):    {mo12_actual:.1f}x")
        print(f"   Difference:           {(mo12_actual - mo6_annualized):+.1f}x")
        
        if mo12_actual > mo6_annualized * 0.9:
            print(f"\n   ✅ 12-month maintained annualized rate! Consistent performance.")
        else:
            print(f"\n   ⚠️ 12-month underperformed annualized projection. Market degradation.")
        
        # Save combined report
        report = {
            'strategy': 'LuxTrader v3.1',
            'generated_at': datetime.now().isoformat(),
            'comparison': {
                '6_months': results_6,
                '12_months': results_12,
                'annualized_projection': mo6_annualized,
                'performance_ratio': mo12_actual / mo6_annualized if mo6_annualized > 0 else 0
            }
        }
        
        output = WORKSPACE / "luxtrader_v31_comparison.json"
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n\n💾 Saved to: {output}")
        print("="*80)


def main():
    backtester = LuxTraderBacktester()
    
    # Run 6-month
    backtester.run_6month_backtest()
    
    # Run 12-month
    backtester.run_1year_backtest()
    
    # Generate comparison
    backtester.generate_comparison_report()
    
    print("\n✅ BACKTEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
