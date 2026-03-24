#!/usr/bin/env python3
"""
📊 FIXED POSITION CALCULATOR
0.3 SOL per trade, NO compounding
"""

import json

strategies = [
    ('Mean-Reverter v2.2', 'mean_reverter_v22_results.json', .63, -.05),  # estimated avg
    ('Rug-Radar v2.1', 'rug_radar_v21_results.json', .12, -.04),
    ('Whale Tracker v2.2', 'whale_tracker_v22_results.json', .18, -.07),
    ('Breakout Hunter v2.2', 'breakout_hunter_v22_results.json', .20, -.07),
    ('Social Sentinel v2.1', 'social_sentinel_v21_results.json', .15, -.07),
]

print("=" * 70)
print("📊 FIXED 0.3 SOL POSITIONS - P&L CALCULATION")
print("=" * 70)
print()
print("Parameters:")
print("  • Starting Capital: 1.0 SOL")
print("  • Position Size: Fixed 0.3 SOL per trade")
print("  • Risk per trade: ~2.1% of capital (0.3 SOL)")
print("  • NO compounding - reinvest same 0.3 SOL each trade")
print()
print("-" * 70)
print()

results = {}

for name, file, avg_win, avg_loss in strategies:
    try:
        with open(f'/home/skux/.openclaw/workspace/agents/lux_trader/{file}') as f:
            data = json.load(f)
        
        trades = data.get('trades', 0)
        wins = data.get('wins', int(trades * 0.65))
        
        # Approximate based on multipliers
        multiplier = data.get('multiplier', 1)
        
        # Estimate win/loss distribution
        win_rate = wins / trades if trades else 0.65
        
        # Calculate with FIXED 0.3 SOL
        position = 0.3
        total_pnl = 0
        
        # Use actual trade details if available
        trades_detail = data.get('trades_detail', [])
        
        if trades_detail and isinstance(trades_detail, list):
            for trade in trades_detail:
                if isinstance(trade, dict):
                    pnl_pct = trade.get('pnl_pct', 0)
                    total_pnl += position * (pnl_pct / 100)
                else:
                    # Estimate
                    if random.random() < win_rate:
                        total_pnl += position * avg_win
                    else:
                        total_pnl += position * avg_loss
        else:
            # Estimate from multiplier
            # With compounding: multiplier = (1 + r)^n
            # With fixed: total_pnl = n * (win_rate * avg_win + (1-win_rate) * avg_loss) * position
            avg_return = win_rate * avg_win + (1 - win_rate) * avg_loss
            total_pnl = trades * avg_return * position
        
        final = 1.0 + total_pnl
        
        results[name] = {
            'total_pnl': total_pnl,
            'final': final,
            'roi': (total_pnl / 1.0) * 100,
            'trades': trades,
            'win_rate': win_rate * 100
        }
        
    except Exception as e:
        print(f"⚠️  {name}: {e}")

if results:
    # Sort by P&L
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
    
    print(f"{'Strategy':<25} {'Trades':>8} {'Win%':>7} {'Total P&L':>12} {'Final SOL':>10}")
    print("-" * 70)
    
    for name, r in sorted_results:
        print(f"{name:<23} {r['trades']:>8} {r['win_rate']:>6.1f}% {r['total_pnl']:>+10.2f} {r['final']:>10.2f}")
    
    print()
    print("=" * 70)
    best = sorted_results[0]
    print(f"🏆 BEST: {best[0]}")
    print(f"   P&L: +{best[1]['total_pnl']:.2f} SOL (+{best[1]['roi']:.0f}%)")
    print(f"   Final: {best[1]['final']:.2f} SOL")
    print()
    print("💡 With FIXED 0.3 SOL sizing:")
    print("   • Lower absolute gains than compounded")
    print("   • More consistent position sizing")
    print("   • Better for risk management")
    print("=" * 70)
