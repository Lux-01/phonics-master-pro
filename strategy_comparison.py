#!/usr/bin/env python3
"""
Strategy Comparison Script
Runs all 5 trading strategies and compares results side-by-side
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

# Strategy configurations
STRATEGIES = [
    {
        'name': 'Whale Tracker',
        'file': 'whale_tracker.py',
        'output': 'whale_tracker_results.json',
        'description': 'Monitors large wallet buy patterns'
    },
    {
        'name': 'Social Sentinel',
        'file': 'social_sentinel.py',
        'output': 'social_sentinel_results.json',
        'description': 'Uses sentiment/social indicators'
    },
    {
        'name': 'Rug-Radar Scalper',
        'file': 'rug_radar_scalper.py',
        'output': 'rug_radar_scalper_results.json',
        'description': 'HF micro-cap with rug filters'
    },
    {
        'name': 'Volatility Mean-Reverter',
        'file': 'volatility_mean_reverter.py',
        'output': 'volatility_mean_reverter_results.json',
        'description': 'Buy oversold, sell on bounce'
    },
    {
        'name': 'Breakout Hunter',
        'file': 'breakout_hunter.py',
        'output': 'breakout_hunter_results.json',
        'description': 'Enter on new highs + volume'
    }
]

def run_strategy(script_file: str) -> bool:
    """Run a strategy script"""
    print(f"\n{'='*60}")
    print(f"Running {script_file}...")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, f'/home/skux/.openclaw/workspace/{script_file}'],
            capture_output=False,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {script_file} timed out")
        return False
    except Exception as e:
        print(f"❌ Error running {script_file}: {e}")
        return False

def load_results(output_file: str) -> Dict:
    """Load strategy results from JSON"""
    try:
        with open(f'/home/skux/.openclaw/workspace/{output_file}', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {output_file}: {e}")
        return None

def format_table_row(cols: List[str], widths: List[int]) -> str:
    """Format a table row"""
    formatted = []
    for col, width in zip(cols, widths):
        formatted.append(f"{col:<{width}}")
    return " | ".join(formatted)

def print_comparison_table(results: List[Dict]):
    """Print side-by-side comparison"""
    print("\n" + "="*100)
    print("📊 STRATEGY COMPARISON RESULTS")
    print("="*100)
    
    # Column widths
    widths = [20, 12, 12, 10, 12, 12, 12]
    headers = ['Strategy', 'Final SOL', 'Return %', 'Trades', 'Win Rate %', 'Avg PnL %', 'Sharpe*']
    
    # Print header
    print("\n" + format_table_row(headers, widths))
    print("-" * 100)
    
    # Sort by return
    sorted_results = sorted(results, key=lambda x: x.get('total_return_pct', 0), reverse=True)
    
    for r in sorted_results:
        # Calculate Sharpe-like ratio (return / |avg pnl| with sign preservation)
        avg_pnl = r.get('avg_trade_return_pct', 0)
        if abs(avg_pnl) > 0.01:
            sharpe_like = r.get('total_return_pct', 0) / abs(avg_pnl)
        else:
            sharpe_like = 0
        
        row = [
            r['strategy'][:18],
            f"{r.get('final_balance', 0):.4f}",
            f"{r.get('total_return_pct', 0):+.2f}%",
            str(r.get('total_trades', 0)),
            f"{r.get('win_rate_pct', 0):.1f}%",
            f"{avg_pnl:+.2f}%",
            f"{sharpe_like:.2f}"
        ]
        print(format_table_row(row, widths))
    
    print("-" * 100)

def print_detailed_analysis(results: List[Dict]):
    """Print detailed analysis for each strategy"""
    print("\n" + "="*100)
    print("📈 DETAILED STRATEGY ANALYSIS")
    print("="*100)
    
    for r in results:
        print(f"\n{r['strategy']}")
        print(f"  Description: {r.get('description', 'N/A')}")
        print(f"  Initial Balance: 1.0 SOL")
        print(f"  Final Balance: {r.get('final_balance', 0):.6f} SOL")
        print(f"  Total Return: {r.get('total_return_pct', 0):+.2f}%")
        print(f"  Total Trades: {r.get('total_trades', 0)}")
        print(f"  Wins: {r.get('wins', 0)} | Losses: {r.get('losses', 0)}")
        print(f"  Win Rate: {r.get('win_rate_pct', 0):.2f}%")
        print(f"  Avg Trade Return: {r.get('avg_trade_return_pct', 0):+.2f}%")
        
        # Strategy-specific metrics
        if 'sentiment_correlation' in r:
            print(f"  Sentiment Correlation: {r['sentiment_correlation']:.4f}")
        if 'rugs_avoided' in r:
            print(f"  Rugs Avoided: {r['rugs_avoided']}")
            print(f"  Avg Risk Score: {r.get('avg_risk_score', 0):.3f}")
        if 'reversion_success_rate' in r:
            print(f"  Reversion Success: {r['reversion_success_rate']:.1f}%")
            print(f"  Avg Entry Deviation: {r.get('avg_entry_deviation', 0):.4f}")
        if 'avg_breakout_strength' in r:
            print(f"  Avg Breakout Strength: {r.get('avg_breakout_strength', 0):.3f}")
            print(f"  Volume Win Rate: {r.get('high_volume_win_rate', 0):.1f}%")
        
        # Learning progress
        if 'learning_history' in r and r['learning_history']:
            final = r['learning_history'][-1]
            print(f"  Final Win Rate: {final.get('win_rate', 0)*100:.1f}%")

def print_leaderboard(results: List[Dict]):
    """Print ranked leaderboard"""
    print("\n" + "="*100)
    print("🏆 STRATEGY LEADERBOARD")
    print("="*100)
    
    # Sort by different metrics
    by_return = sorted(results, key=lambda x: x.get('total_return_pct', 0), reverse=True)
    by_winrate = sorted(results, key=lambda x: x.get('win_rate_pct', 0), reverse=True)
    by_trades = sorted(results, key=lambda x: x.get('total_trades', 0), reverse=True)
    
    print("\n🥇 BEST RETURNS:")
    for i, r in enumerate(by_return[:3], 1):
        emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '  ')
        print(f"   {emoji} {i}. {r['strategy']}: {r.get('total_return_pct', 0):+.2f}%")
    
    print("\n🎯 BEST WIN RATE:")
    for i, r in enumerate(by_winrate[:3], 1):
        emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '  ')
        print(f"   {emoji} {i}. {r['strategy']}: {r.get('win_rate_pct', 0):.1f}%")
    
    print("\n📊 MOST ACTIVE:")
    for i, r in enumerate(by_trades[:3], 1):
        emoji = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '  ')
        print(f"   {emoji} {i}. {r['strategy']}: {r.get('total_trades', 0)} trades")
    
    # Overall winner (composite score)
    print("\n🏆 OVERALL CHAMPION:")
    for r in results:
        r['_composite'] = (
            r.get('total_return_pct', 0) * 0.5 +
            r.get('win_rate_pct', 0) * 0.3 +
            min(r.get('total_trades', 0), 50) * 0.2  # Cap trades at 50 for scoring
        )
    
    champion = max(results, key=lambda x: x['_composite'])
    print(f"   🏆 {champion['strategy']}!")
    print(f"      Return: {champion.get('total_return_pct', 0):+.2f}%")
    print(f"      Win Rate: {champion.get('win_rate_pct', 0):.1f}%")
    print(f"      Trades: {champion.get('total_trades', 0)}")

def save_comprehensive_results(all_results: List[Dict]):
    """Save combined results"""
    output = {
        'timestamp': datetime.now().isoformat(),
        'data_source': '/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json',
        'duration_months': 6,
        'initial_capital': 1.0,
        'strategies': all_results,
        'rankings': {
            'by_return': [r['strategy'] for r in sorted(all_results, key=lambda x: x.get('total_return_pct', 0), reverse=True)],
            'by_winrate': [r['strategy'] for r in sorted(all_results, key=lambda x: x.get('win_rate_pct', 0), reverse=True)],
            'by_trades': [r['strategy'] for r in sorted(all_results, key=lambda x: x.get('total_trades', 0), reverse=True)]
        }
    }
    
    output_path = '/home/skux/.openclaw/workspace/strategy_comparison_results.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Comprehensive results saved to: {output_path}")
    return output_path

def main():
    print("🚀 SOLANA TRADING STRATEGY BACKTEST COMPARISON")
    print("="*60)
    print(f"Data: 6 months of Solana trading data")
    print(f"Initial Capital: 1.0 SOL per strategy")
    print(f"Strategies: 5 independent approaches")
    print("="*60)
    
    # Run all strategies
    print("\n🔥 RUNNING ALL STRATEGIES...")
    
    success_count = 0
    for strat in STRATEGIES:
        if run_strategy(strat['file']):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(STRATEGIES)} strategies completed successfully")
    
    # Load results
    print("\n📥 Loading results...")
    all_results = []
    for strat in STRATEGIES:
        results = load_results(strat['output'])
        if results:
            all_results.append(results)
            print(f"  ✓ {strat['name']}")
        else:
            print(f"  ✗ {strat['name']} - failed to load")
    
    if not all_results:
        print("❌ No results loaded. Exiting.")
        return
    
    # Display comparisons
    print_comparison_table(all_results)
    print_leaderboard(all_results)
    print_detailed_analysis(all_results)
    
    # Save combined results
    output_path = save_comprehensive_results(all_results)
    
    # Summary
    print("\n" + "="*100)
    print("📋 SUMMARY")
    print("="*100)
    print(f"Total strategies tested: {len(all_results)}")
    print(f"Data period: 6 months")
    print(f"Initial capital per strategy: 1.0 SOL")
    
    total_final = sum(r.get('final_balance', 0) for r in all_results)
    avg_return = sum(r.get('total_return_pct', 0) for r in all_results) / len(all_results)
    total_trades = sum(r.get('total_trades', 0) for r in all_results)
    avg_winrate = sum(r.get('win_rate_pct', 0) for r in all_results) / len(all_results)
    
    print(f"\nCombined portfolio value: {total_final:.4f} SOL")
    print(f"Average return: {avg_return:+.2f}%")
    print(f"Total trades across all strategies: {total_trades}")
    print(f"Average win rate: {avg_winrate:.1f}%")
    print(f"\nResults saved to individual JSON files and {output_path}")
    
    print("\n" + "="*100)
    print("Done! 🎉")
    print("="*100)

if __name__ == '__main__':
    main()
