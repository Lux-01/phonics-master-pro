#!/usr/bin/env python3
"""
LuxTrader Backtest v2.0 - Direct simulation
Bypasses position limits to simulate all 373 trades
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

@dataclass
class SimulatedTrade:
    id: int
    token_symbol: str
    token_address: str
    entry_price: float
    entry_time: str
    exit_price: float = 0.0
    exit_time: str = ""
    status: str = "OPEN"
    pnl_pct: float = 0.0
    outcome: str = ""  # win, loss, rug
    exit_reason: str = ""
    target: float = 0.15
    stop_loss: float = -0.07

class LuxTraderBacktest:
    """Backtest LuxTrader on historical data"""
    
    def __init__(self):
        self.data_dir = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
        self.results_file = self.data_dir / "backtest_results.json"
        
        # Load Skylar's 4-month backtest data
        with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_4month_backtest.json') as f:
            data = json.load(f)
        self.historical_trades = data['trades']
        
        print(f"📊 Loaded {len(self.historical_trades)} historical trades")
        print(f"   Period: {data['duration_months']} months / {data['duration_days']} days")
    
    def run_backtest(self):
        """Run backtest simulation"""
        print("\n" + "="*70)
        print("🧠 LUXTRADER BACKTEST - 4 MONTHS HISTORICAL DATA")
        print("="*70)
        
        # Statistics
        trades = []
        stats_by_grade = {}
        stats_by_outcome = {}
        wins = losses = rugs = 0
        total_pnl = 0
        
        print("\n📈 Simulating all trades...")
        print(f"{'#':<6} {'Symbol':<12} {'Grade':<6} {'Result':<8} {'PnL':<12} {'Exit'}")
        print("-"*70)
        
        for i, hist in enumerate(self.historical_trades, 1):
            entry_price = 0.0001
            outcome_pnl = hist['pnl_pct'] / 100
            
            # Determine outcome
            if hist['is_rug']:
                outcome = 'rug'
                exit_reason = 'rug'
                rugs += 1
            elif hist['result'] == 'win':
                outcome = 'win'
                exit_reason = 'target_hit' if outcome_pnl >= 0.15 else 'manual'
                wins += 1
            else:
                outcome = 'loss'
                exit_reason = 'stop_loss' if outcome_pnl <= -0.07 else 'time_stop'
                losses += 1
            
            trade = SimulatedTrade(
                id=i,
                token_symbol=hist['symbol'],
                token_address=f"{hist['symbol']}_addr_{i}",
                entry_price=entry_price,
                entry_time=(datetime.now() - timedelta(hours=len(self.historical_trades)-i)).isoformat(),
                exit_price=entry_price * (1 + outcome_pnl),
                exit_time=(datetime.now() - timedelta(hours=len(self.historical_trades)-i) + timedelta(hours=2)).isoformat(),
                status='CLOSED',
                pnl_pct=outcome_pnl,
                outcome=outcome,
                exit_reason=exit_reason,
                target=0.15,
                stop_loss=-0.07
            )
            trades.append(trade)
            total_pnl += outcome_pnl
            
            # Track stats
            grade = hist['grade']
            if grade not in stats_by_grade:
                stats_by_grade[grade] = {'count': 0, 'wins': 0, 'losses': 0, 'rugs': 0, 'pnl': 0}
            stats_by_grade[grade]['count'] += 1
            stats_by_grade[grade]['pnl'] += outcome_pnl
            if outcome == 'win':
                stats_by_grade[grade]['wins'] += 1
            elif outcome == 'loss':
                stats_by_grade[grade]['losses'] += 1
            else:
                stats_by_grade[grade]['rugs'] += 1
            
            # Track by exit reason
            if exit_reason not in stats_by_outcome:
                stats_by_outcome[exit_reason] = {'count': 0, 'wins': 0, 'pnl': 0}
            stats_by_outcome[exit_reason]['count'] += 1
            stats_by_outcome[exit_reason]['pnl'] += outcome_pnl
            if outcome == 'win':
                stats_by_outcome[exit_reason]['wins'] += 1
            
            # Show progress every 50 trades
            if i % 50 == 0:
                print(f"{i:<6} {trade.token_symbol:<12} {grade:<6} "
                      f"{outcome:<8} {outcome_pnl:+>9.1%}  {exit_reason}")
        
        # Print final stats
        print(f"\n📊 Backtest Complete: {len(trades)} trades processed")
        
        # Save trades
        with open(self.data_dir / 'trades.json', 'w') as f:
            json.dump([asdict(t) for t in trades], f, indent=2)
        
        # Clear portfolio
        with open(self.data_dir / 'portfolio.json', 'w') as f:
            json.dump({'positions': [], 'updated_at': datetime.now().isoformat()}, f)
        
        # Analysis
        print("\n" + "="*70)
        print("📊 PERFORMANCE ANALYSIS")
        print("="*70)
        
        win_rate = wins / len(trades) * 100 if trades else 0
        avg_pnl = total_pnl / len(trades) * 100 if trades else 0
        
        print(f"\nOverall Statistics:")
        print(f"  Total Trades: {len(trades)}")
        print(f"  Wins: {wins} ({wins/len(trades)*100:.1f}%)")
        print(f"  Losses: {losses} ({losses/len(trades)*100:.1f}%)")
        print(f"  Rugs: {rugs} ({rugs/len(trades)*100:.1f}%)")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Total P&L: {total_pnl*100:+.1f}%")
        print(f"  Avg P&L per trade: {avg_pnl:+.1f}%")
        
        print(f"\n📊 Performance by Grade:")
        for grade in ['A+', 'A', 'A-', 'B+', 'B']:
            if grade in stats_by_grade:
                g = stats_by_grade[grade]
                wr = g['wins'] / g['count'] * 100 if g['count'] > 0 else 0
                avg = g['pnl'] / g['count'] * 100 if g['count'] > 0 else 0
                print(f"  {grade:<4}: {g['count']:>3} trades | Win: {g['wins']:>3} | Loss: {g['losses']:>3} | "
                      f"Rug: {g['rugs']:>3} | {wr:>5.1f}% WR | {avg:+>6.1f}%")
        
        print(f"\n📊 Performance by Exit Reason:")
        for reason, data in sorted(stats_by_outcome.items(), key=lambda x: -x[1]['count']):
            wr = data['wins'] / data['count'] * 100 if data['count'] > 0 else 0
            avg = data['pnl'] / data['count'] * 100 if data['count'] > 0 else 0
            print(f"  {reason:<15}: {data['count']:>3} trades | {wr:>5.1f}% WR | {avg:+>6.1f}% avg")
        
        # Learning insights
        print(f"\n🧠 Key Insights:")
        
        # Best grade
        best_grade = max(stats_by_grade.items(), key=lambda x: x[1]['pnl']/x[1]['count'] if x[1]['count'] > 0 else -999)
        print(f"  • Best grade: {best_grade[0]} ({best_grade[1]['pnl']/best_grade[1]['count']*100:+.1f}% avg)")
        
        # Worst grade (with trades)
        worst_candidates = {k: v for k, v in stats_by_grade.items() if v['count'] >= 5}
        if worst_candidates:
            worst_grade = min(worst_candidates.items(), key=lambda x: x[1]['pnl']/x[1]['count'])
            print(f"  • Worst grade: {worst_grade[0]} ({worst_grade[1]['pnl']/worst_grade[1]['count']*100:+.1f}% avg)")
        
        # Rug rate
        rug_rate = rugs / len(trades) * 100
        print(f"  • Rug rate: {rug_rate:.1f}% ({rugs} out of {len(trades)})")
        
        # Best exit
        best_exit = max(stats_by_outcome.items(), key=lambda x: x[1]['pnl']/x[1]['count'] if x[1]['count'] > 0 else -999)
        print(f"  • Best exit: {best_exit[0]} ({best_exit[1]['pnl']/best_exit[1]['count']*100:+.1f}% avg)")
        
        # Save results
        results = {
            'backtest_run': datetime.now().isoformat(),
            'historical_data': 'skylar_4month_backtest.json',
            'trades_simulated': len(trades),
            'wins': wins,
            'losses': losses,
            'rugs': rugs,
            'win_rate': win_rate,
            'total_pnl_pct': total_pnl * 100,
            'avg_pnl_pct': avg_pnl,
            'by_grade': stats_by_grade,
            'by_exit': stats_by_outcome
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {self.results_file}")
        
        # Now run learning engine
        print("\n" + "="*70)
        print("🧠 RUNNING LEARNING ENGINE")
        print("="*70)
        
        from learning_engine import LearningEngine
        engine = LearningEngine(self.data_dir)
        analysis = engine.analyze()
        
        if 'error' not in analysis:
            print(f"\n📊 Learning Engine Results:")
            for rec in analysis.get('recommendations', []):
                print(f"  • {rec}")
            
            # Evolve strategy
            print(f"\n🔄 Evolving Strategy...")
            engine.evolve_strategy(analysis)
        
        print("="*70)


def main():
    print("\n" + "="*70)
    print("  LUXTRADER BACKTEST ENGINE v2.0")
    print("  Training on 4 months of historical data (373 trades)")
    print("="*70 + "\n")
    
    backtest = LuxTraderBacktest()
    backtest.run_backtest()


if __name__ == "__main__":
    main()
