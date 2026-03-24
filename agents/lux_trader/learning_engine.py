#!/usr/bin/env python3
"""
LuxTrader Learning Engine v1.0
Extracts patterns from trade history and evolves strategy.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import statistics


class LearningEngine:
    """
    Analyzes trade outcomes and extracts actionable patterns.
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.trades_file = data_dir / "trades.json"
        self.learning_file = data_dir / "learning.json"
        self.strategy_file = data_dir / "strategy.json"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze all completed trades and extract patterns.
        Returns insights for strategy evolution.
        """
        if not self.trades_file.exists():
            return {'error': 'No trades to analyze'}
        
        with open(self.trades_file) as f:
            trades = json.load(f)
        
        # Filter to completed trades
        completed = [t for t in trades if t.get('status') != 'OPEN']
        
        if len(completed) < 3:
            return {'error': f'Need 3+ completed trades, have {len(completed)}'}
        
        print(f"\n🔬 Analyzing {len(completed)} completed trades...")
        
        # Basic stats
        wins = [t for t in completed if t.get('outcome') == 'win']
        losses = [t for t in completed if t.get('outcome') == 'loss']
        rugs = [t for t in completed if t.get('outcome') == 'rug']
        
        win_pnl = [t['pnl_pct'] for t in wins]
        loss_pnl = [t['pnl_pct'] for t in losses]
        
        stats = {
            'total': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'rugs': len(rugs),
            'win_rate': len(wins) / len(completed) * 100,
            'avg_win': statistics.mean(win_pnl) if win_pnl else 0,
            'avg_loss': statistics.mean(loss_pnl) if loss_pnl else 0,
            'best_trade': max(win_pnl) if win_pnl else None,
            'worst_trade': min(loss_pnl) if loss_pnl else None,
            'total_pnl': sum(t['pnl_pct'] for t in completed)
        }
        
        print(f"\n📊 Performance Summary:")
        print(f"  Win Rate: {stats['win_rate']:.1f}%")
        print(f"  Total P&L: {stats['total_pnl']:+.1f}%")
        print(f"  Avg Win: {stats['avg_win']:+.1f}%")
        print(f"  Avg Loss: {stats['avg_loss']:+.1f}%")
        
        # Extract patterns from exit reasons
        patterns = self._extract_exit_patterns(completed)
        
        # Extract timing patterns
        timing = self._extract_timing_patterns(completed)
        
        # Generate strategy recommendations
        recommendations = self._generate_recommendations(stats, patterns, timing)
        
        return {
            'stats': stats,
            'patterns': patterns,
            'timing': timing,
            'recommendations': recommendations
        }
    
    def _extract_exit_patterns(self, trades: List[Dict]) -> List[Dict]:
        """Analyze which exit reasons correlate with wins/losses"""
        by_exit = defaultdict(list)
        
        for t in trades:
            reason = t.get('exit_reason', 'unknown')
            by_exit[reason].append(t['pnl_pct'])
        
        patterns = []
        for reason, pnls in by_exit.items():
            avg = statistics.mean(pnls)
            win_count = sum(1 for p in pnls if p > 0)
            rate = win_count / len(pnls) * 100
            
            patterns.append({
                'type': 'exit_reason',
                'reason': reason,
                'count': len(pnls),
                'avg_pnl': f"{avg:+.1f}%",
                'win_rate': f"{rate:.1f}%",
                'insight': self._exit_insight(reason, rate, avg)
            })
        
        return patterns
    
    def _exit_insight(self, reason: str, win_rate: float, avg_pnl: float) -> str:
        """Generate insight from exit pattern"""
        if win_rate >= 70:
            return f"{reason.title()} exits are working well ({win_rate:.0f}% WR)"
        elif win_rate <= 40 and 'stop' in reason:
            return f"Stop losses too tight? Only {win_rate:.0f}% hit target first"
        elif 'rug' in reason:
            return "Rugs detected - consider stricter liquidity filter"
        return f"Monitor {reason} exits"
    
    def _extract_timing_patterns(self, trades: List[Dict]) -> Dict:
        """Analyze holding time vs outcome"""
        times = []
        for t in trades:
            try:
                entry = datetime.fromisoformat(t['entry_time'])
                exit_time = datetime.fromisoformat(t['exit_time'])
                duration = (exit_time - entry_time).total_seconds() / 60
                times.append({
                    'duration_min': duration,
                    'pnl': t['pnl_pct'],
                    'outcome': t['outcome']
                })
            except:
                pass
        
        if not times:
            return {}
        
        # Winners vs losers timing
        win_times = [t['duration_min'] for t in times if t['outcome'] == 'win']
        loss_times = [t['duration_min'] for t in times if t['outcome'] == 'loss']
        
        return {
            'avg_win_time': f"{statistics.mean(win_times):.0f}m" if win_times else "N/A",
            'avg_loss_time': f"{statistics.mean(loss_times):.0f}m" if loss_times else "N/A",
            'fastest_win': f"{min(win_times):.0f}m" if win_times else "N/A",
            'fastest_loss': f"{min(loss_times):.0f}m" if loss_times else "N/A",
            'insight': self._timing_insight(win_times, loss_times)
        }
    
    def _timing_insight(self, win_times: List[float], loss_times: List[float]) -> str:
        """Generate timing insight"""
        if not win_times or not loss_times:
            return "Need more timing data"
        
        avg_win = statistics.mean(win_times)
        avg_loss = statistics.mean(loss_times)
        
        if avg_loss < avg_win * 0.5:
            return "Losses happen fast - stops working well"
        elif avg_win < 30:
            return "Quick wins - consider tighter time stops"
        elif avg_win > 180:
            return "Wins take time - patience pays off"
        return "Timing distribution normal"
    
    def _generate_recommendations(self, stats: Dict, patterns: List, timing: Dict) -> List[str]:
        """Generate actionable strategy recommendations"""
        recs = []
        
        # TP/SL recommendations
        if stats['avg_win'] > 0.20:
            recs.append(f"Consider raising TP from 15% to {stats['avg_win']:.0%}")
        
        if stats['avg_loss'] < -0.10:
            recs.append(f"Losses deeper than -7% - consider looser stops or earlier time exits")
        
        if stats['win_rate'] < 50 and len([r for r in patterns if 'rug' in r['reason']]) > 0:
            recs.append("Increase minimum liquidity filter - too many rugs")
        
        if timing.get('avg_win_time', '').replace('m','').isdigit():
            mins = int(timing['avg_win_time'].replace('m',''))
            if mins < 30:
                recs.append("Wins come quick - reduce time stop from 4h")
            elif mins > 120:
                recs.append("Wins need time - increase time stop or be patient")
        
        if not recs:
            recs.append("Strategy performing well - continue current approach")
        
        return recs
    
    def evolve_strategy(self, analysis: Dict) -> bool:
        """
        Apply recommendations to strategy file.
        Returns True if strategy was updated.
        """
        if 'error' in analysis:
            print(f"❌ Cannot evolve: {analysis['error']}")
            return False
        
        if not self.strategy_file.exists():
            print("❌ No strategy file found")
            return False
        
        with open(self.strategy_file) as f:
            strategy = json.load(f)
        
        # Parse version (handle "0.3.1" -> 0.31 for incrementing)
        version_str = strategy.get('version', '0.1')
        try:
            current_version = float(version_str)
        except ValueError:
            # Handle semantic versioning like "0.3.1"
            parts = version_str.split('.')
            current_version = float(f"{parts[0]}.{''.join(parts[1:])}")
        
        # Apply recommendations
        recommendations = analysis.get('recommendations', [])
        updated = False
        
        for rec in recommendations:
            # Parse recommendation
            if 'TP' in rec and 'to' in rec:
                # Extract percentage
                try:
                    new_tp = float(rec.split('to')[-1].strip().replace('%', '')) / 100
                    strategy['target_profit'] = new_tp
                    updated = True
                    print(f"  ✏️  Updated target_profit to {new_tp:.0%}")
                except:
                    pass
            
            elif 'liquidity' in rec.lower():
                # Increase liquidity min
                current = strategy.get('min_liquidity', 5000)
                strategy['min_liquidity'] = current * 1.5
                updated = True
                print(f"  ✏️  Increased min_liquidity to ${strategy['min_liquidity']:,.0f}")
            
            elif 'time stop' in rec.lower():
                if 'reduce' in rec.lower():
                    strategy['time_stop_minutes'] = 120
                    updated = True
                    print(f"  ✏️  Reduced time_stop to 2 hours")
                elif 'increase' in rec.lower():
                    strategy['time_stop_minutes'] = 360
                    updated = True
                    print(f"  ✏️  Increased time_stop to 6 hours")
        
        if updated:
            strategy['version'] = f"{current_version + 0.1:.1f}"
            strategy['last_evolved'] = datetime.now().isoformat()
            strategy['evolution_note'] = f"Auto-evolved after {analysis['stats']['total']} trades"
            
            with open(self.strategy_file, 'w') as f:
                json.dump(strategy, f, indent=2)
            
            print(f"\n✅ Strategy updated to v{strategy['version']}")
            return True
        
        print("\nℹ️  No strategy changes needed")
        return False


def learn_and_evolve():
    """Run learning and evolution cycle"""
    data_dir = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
    
    print("=" * 60)
    print("🧠 LUXTRADER LEARNING ENGINE")
    print("=" * 60)
    
    engine = LearningEngine(data_dir)
    
    # Analyze trades
    analysis = engine.analyze()
    
    # Evolve strategy
    if 'error' not in analysis:
        print("\n🔄 Evolving strategy...")
        engine.evolve_strategy(analysis)
        
        # Show patterns
        print("\n📋 Patterns Discovered:")
        for p in analysis.get('patterns', []):
            print(f"  • {p['insight']}")
        
        # Show recommendations
        print("\n💡 Recommendations:")
        for r in analysis.get('recommendations', []):
            print(f"  • {r}")
    
    print("=" * 60)


if __name__ == "__main__":
    learn_and_evolve()
