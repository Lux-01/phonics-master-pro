#!/usr/bin/env python3
"""
Master comparison script - Run all 5 strategies
Compare performance side-by-side
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def run_strategy(script_name):
    """Run a strategy script and return results"""
    try:
        result = subprocess.run(
            ['python3', f'/home/skux/.openclaw/workspace/agents/lux_trader/{script_name}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def load_results(filename):
    """Load results from JSON file"""
    try:
        with open(f'/home/skux/.openclaw/workspace/agents/lux_trader/{filename}') as f:
            return json.load(f)
    except:
        return None

def print_comparison_table(results):
    """Print beautiful comparison table"""
    
    print("\n" + "=" * 90)
    print("🚀 SOLANA TRADING STRATEGIES - 6 MONTH BACKTEST COMPARISON")
    print("=" * 90)
    print(f"Start Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Starting Capital: 1.00 SOL each strategy")
    print("-" * 90)
    
    # Header
    print(f"{'Rank':5} │ {'Strategy':22} │ {'End SOL':9} │ {'P&L':10} │ {'Mult':6} │ {'Trades':7} │ {'Win %':7} │ {'Rugs':5}")
    print("-" * 90)
    
    # Sort by P&L
    sorted_results = sorted(results.items(), key=lambda x: x[1].get('end', 1), reverse=True)
    
    for rank, (name, data) in enumerate(sorted_results, 1):
        emoji = data.get('emoji', '⚡')
        strategy = data.get('strategy', name)
        end = data.get('end', 1.0)
        pnl = data.get('pnl', 0)
        mult = data.get('multiplier', 1.0)
        trades = data.get('trades', 0)
        win_rate = data.get('win_rate', 0)
        rugs = data.get('rugs', 0)
        
        pnl_str = f"{pnl:+.2f}" if pnl >= 0 else f"{pnl:.2f}"
        
        print(f"{rank:3}   │ {emoji} {strategy:18} │ {end:8.2f} │ {pnl_str:9} │ {mult:5.1f}x │ {trades:6} │ {win_rate:6.1f}% │ {rugs:4}")
    
    print("=" * 90)
    
    # Analysis
    print("\n📊 STRATEGY ANALYSIS:")
    print("-" * 90)
    
    best = sorted_results[0][1]
    worst = sorted_results[-1][1]
    
    print(f"\n🏆 BEST PERFORMER: {best.get('emoji', '⚡')} {best.get('strategy', 'N/A')}")
    print(f"   Return: {best.get('end', 0):.2f} SOL ({best.get('multiplier', 1):.1f}x)")
    print(f"   Win Rate: {best.get('win_rate', 0):.1f}% | Rugs: {best.get('rugs', 0)}")
    
    print(f"\n⚠️  NEEDS IMPROVEMENT: {worst.get('emoji', '⚡')} {worst.get('strategy', 'N/A')}")
    print(f"   Return: {worst.get('end', 0):.2f} SOL ({worst.get('multiplier', 1):.1f}x)")
    print(f"   Win Rate: {worst.get('win_rate', 0):.1f}% | Rugs: {worst.get('rugs', 0)}")
    
    # Calculate totals
    total_pnl = sum([r.get('pnl', 0) for r in results.values()])
    avg_return = sum([r.get('multiplier', 1) for r in results.values()]) / len(results)
    total_rugs = sum([r.get('rugs', 0) for r in results.values()])
    
    print(f"\n📈 ACROSS 5 STRATEGIES:")
    print(f"   Combined P&L: {total_pnl:+.2f} SOL")
    print(f"   Average Return: {avg_return:.1f}x")
    print(f"   Total Rugs: {total_rugs}")
    print(f"   Total Trades: {sum([r.get('trades', 0) for r in results.values()])}")
    
    print("\n" + "=" * 90)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 90)
    
    top_3 = sorted_results[:3]
    for name, data in top_3:
        emoji = data.get('emoji', '⚡')
        print(f"  {emoji} {data.get('strategy', name)} - {data.get('multiplier', 1):.1f}x return")
    
    print(f"\n🎯 OPTIMAL APPROACH:")
    print(f"   Combine top 2-3 strategies for diversified returns.")
    print(f"   Focus on highest win rate with acceptable rug rate (<10%).")
    
    print("\n" + "=" * 90)
    
    # Save combined results
    combined = {
        'run_date': datetime.now().isoformat(),
        'strategies_tested': 5,
        'starting_capital': 1.0,
        'results': {name: data for name, data in results.items()},
        'rankings': [
            {'rank': i+1, 'strategy': data.get('strategy', name), 'multiplier': data.get('multiplier', 1)}
            for i, (name, data) in enumerate(sorted_results)
        ]
    }
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/strategy_comparison_5ways.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print("💾 Saved to: strategy_comparison_5ways.json")

def main():
    """Run all strategies and compare"""
    
    strategies = [
        ('whale_tracker.py', 'whale_tracker_results.json'),
        ('social_sentinel.py', 'social_sentinel_results.json'),
        ('rug_radar_scalper.py', 'rug_radar_results.json'),
        ('volatility_mean_reverter.py', 'mean_reverter_results.json'),
        ('breakout_hunter.py', 'breakout_hunter_results.json')
    ]
    
    print("=" * 70)
    print("🚀 RUNNING 5 STRATEGY BACKTESTS")
    print("=" * 70)
    print("Each strategy starts with 1 SOL, runs 6 months...")
    print()
    
    results = {}
    
    for script, output in strategies:
        name = script.replace('.py', '').replace('_', ' ').title()
        print(f"Running {name}...", end=' ')
        
        if run_strategy(script):
            data = load_results(output)
            if data:
                results[name] = data
                print(f"✅ ({data.get('multiplier', 1):.1f}x)")
            else:
                print("❌ (no results)")
        else:
            print("❌ (failed)")
    
    print()
    print_comparison_table(results)

if __name__ == "__main__":
    main()
