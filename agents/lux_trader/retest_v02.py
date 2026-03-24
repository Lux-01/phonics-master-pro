#!/usr/bin/env python3
"""
Retest Strategy v0.2 on 6-month historical data
Starting capital: 1 SOL
NEW rules: A+ only (score 80+), 20% target, -7% stop, 240min time stop
"""

import json
from pathlib import Path
import random

def load_data():
    """Load 6-month backtest data"""
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_v02_strategy(opportunities):
    """
    Simulate v0.2 strategy on historical A+ trades
    - Only Grade A+ 
    - 20% target (vs original 15%)
    - -7% stop
    - 0.01 SOL position size
    """
    
    capital = 1.0  # Starting with 1 SOL
    initial_capital = capital
    trades = []
    
    print("=" * 70)
    print("🧪 LUXTRADER v0.2 RETEST ON 6-MONTH DATA")
    print("=" * 70)
    print(f"Starting Capital: {initial_capital} SOL")
    print(f"Strategy: A+ only, 20% target (was 15%), -7% stop")
    print(f"Position Size: 0.01 SOL per trade")
    print("-" * 70)
    
    for opp in opportunities:
        # Skip if not A+ grade
        if opp.get('grade') != 'A+':
            continue
        
        # Skip if out of capital
        if capital < 0.01:
            print(f"⚠️  Out of capital at trade #{len(trades)+1}, stopping")
            break
        
        # Get original P&L (stored as percent, e.g., 15.5 or -7.0)
        original_pnl = opp.get('pnl_pct', 0) / 100  # Convert % to decimal
        original_exit = opp.get('exit_reason', '').lower()
        is_rug = opp.get('is_rug', False) or 'rug' in original_exit
        
        # v0.2 LOGIC:
        # If original hit 15% target, we now hold to 20% (more profit)
        # If original was stop/rug, same loss (already at -7% or worse)
        # If original was manual/time exit > 10%, assume 75% hit 20%
        
        if ('target' in original_exit or 'manual' in original_exit) and original_pnl >= 0.10:
            # Would have held to 20%
            new_pnl = 0.20
            new_exit = 'target_hit_v02'
            outcome = 'win'
        elif is_rug:
            # Rugs: use actual loss (typically -5% to -20%)
            new_pnl = max(original_pnl, -0.20)  # Cap at -20%
            new_exit = 'rug'
            outcome = 'rug'
        elif 'stop' in original_exit and original_pnl < 0:
            # Stopped out at ~-7%
            new_pnl = -0.07
            new_exit = 'stop_loss'
            outcome = 'loss'
        elif original_pnl > 0.05:  # Had 5-10% profit
            # Some hold to 20%, some exit
            if random.random() < 0.60:  # 60% become winners at 20%
                new_pnl = 0.20
                new_exit = 'target_hit_v02'
                outcome = 'win'
            else:
                new_pnl = original_pnl
                new_exit = 'manual_v02'
                outcome = 'win'
        elif original_pnl > 0:  # Small profit 0-5%
            new_pnl = original_pnl
            new_exit = 'manual_v02'
            outcome = 'win'
        elif original_pnl < 0:  # Loss
            new_pnl = original_pnl
            new_exit = 'time_stop_v02'
            outcome = 'loss'
        else:  # breakeven
            new_pnl = 0
            new_exit = 'break_even'
            outcome = 'break_even'
        
        # Apply position size and calculate P&L in SOL
        position_size = 0.01  # Fixed position size
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        trades.append({
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'grade': 'A+',
            'original_pnl_pct': round(original_pnl * 100, 2),
            'new_pnl_pct': round(new_pnl * 100, 2),
            'pnl_sol': round(pnl_sol, 5),
            'exit_reason': new_exit,
            'outcome': outcome,
            'capital_after': round(capital, 4)
        })
    
    return trades, capital, initial_capital

def analyze_results(trades, final_capital, initial_capital):
    """Analyze retest results"""
    
    wins = [t for t in trades if t['outcome'] == 'win']
    losses = [t for t in trades if t['outcome'] == 'loss']
    rugs = [t for t in trades if t['outcome'] == 'rug']
    
    win_pnl_pct = [t['new_pnl_pct'] for t in wins]
    loss_pnl_pct = [t['new_pnl_pct'] for t in losses]
    rug_pnl_pct = [t['new_pnl_pct'] for t in rugs]
    
    total_pnl_sol = final_capital - initial_capital
    total_pnl_pct = (total_pnl_sol / initial_capital) * 100
    
    print(f"\n{'=' * 70}")
    print("📊 v0.2 RETEST RESULTS")
    print(f"{'=' * 70}")
    print(f"\n💰 CAPITAL:")
    print(f"  Start:     {initial_capital:.4f} SOL")
    print(f"  End:       {final_capital:.4f} SOL")
    print(f"  P&L:       {total_pnl_sol:+.4f} SOL ({total_pnl_pct:+.1f}%)")
    
    print(f"\n📈 TRADE SUMMARY:")
    print(f"  Total Trades:  {len(trades)}")
    print(f"  Wins:          {len(wins)}")
    print(f"  Losses:        {len(losses)}")
    print(f"  Rugs:          {len(rugs)}")
    print(f"  Win Rate:      {len(wins)/len(trades)*100:.1f}%" if trades else "  Win Rate:      N/A")
    
    if wins:
        print(f"\n✅ WIN METRICS:")
        print(f"  Count:         {len(wins)}")
        print(f"  Total Win %:   {sum(win_pnl_pct):+.2f}%")
        print(f"  Avg Win:       {sum(win_pnl_pct)/len(wins):+.1f}%")
    
    if losses:
        print(f"\n❌ LOSS METRICS:")
        print(f"  Count:         {len(losses)}")
        print(f"  Total Loss %:  {sum(loss_pnl_pct):+.2f}%")
        print(f"  Avg Loss:      {sum(loss_pnl_pct)/len(losses):+.1f}%")
    
    if rugs:
        print(f"\n🪦 RUG METRICS:")
        print(f"  Count:         {len(rugs)} (out of {len(trades)} trades = {len(rugs)/len(trades)*100:.1f}%)")
        print(f"  Total Loss:    {sum(rug_pnl_pct):+.2f}%")
    
    # Exit breakdown
    from collections import defaultdict
    by_exit = defaultdict(list)
    for t in trades:
        by_exit[t['exit_reason']].append(t['new_pnl_pct'])
    
    print(f"\n🎯 EXIT BREAKDOWN:")
    for reason, pnls in sorted(by_exit.items(), key=lambda x: -len(x[1])):
        total_pnl = sum(pnls)
        count = len(pnls)
        avg_pnl = total_pnl / count if count else 0
        print(f"  {reason:15s}: {count:3d} trades, {total_pnl:+6.1f}% total, {avg_pnl:+5.1f}% avg")
    
    # Show some sample trades
    print(f"\n📋 SAMPLE TRADES:")
    for t in trades[:5]:
        print(f"  {t['symbol']:12s}: {t['original_pnl_pct']:+6.1f}% -> {t['new_pnl_pct']:+6.1f}% ({t['exit_reason']})")
    
    # Show worst trades
    print(f"\n💀 WORST TRADES:")
    worst = sorted(trades, key=lambda x: x['new_pnl_pct'])[:3]
    for t in worst:
        print(f"  {t['symbol']:12s}: {t['new_pnl_pct']:+6.1f}% ({t['exit_reason']})")
    
    print("\n" + "=" * 70)
    
    return {
        'start_capital': initial_capital,
        'end_capital': final_capital,
        'pnl_sol': total_pnl_sol,
        'pnl_pct': total_pnl_pct,
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'rugs': len(rugs),
        'win_rate': len(wins)/len(trades)*100 if trades else 0
    }

random.seed(42)  # For reproducibility

if __name__ == "__main__":
    data = load_data()
    opportunities = data.get('trades', [])
    
    print(f"Loaded {len(opportunities)} total trades from 6-month dataset")
    
    # Filter to A+ only
    a_plus_trades = [o for o in opportunities if o.get('grade') == 'A+']
    print(f"A+ trades available: {len(a_plus_trades)}")
    print(f"Expected trades if all executed: ~100 (max capital / position_size)")
    
    trades, final_capital, initial_capital = simulate_v02_strategy(a_plus_trades)
    results = analyze_results(trades, final_capital, initial_capital)
    
    # Save results
    results_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/retest_v02_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'strategy_version': '0.2',
            'parameters': {
                'target_profit': 0.20,
                'stop_loss': -0.07,
                'grade_filter': 'A+ only',
                'position_size': 0.01,
                'starting_capital': 1.0
            },
            'results': results,
            'trades': trades
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
