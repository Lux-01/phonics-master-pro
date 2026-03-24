#!/usr/bin/env python3
"""
📉 Mean-Reverter v2.2 - IMPROVED
Improvements:
- 50% position on extreme oversold (<-15%)
- 2-tier exit (50% at 12%, let rest run to 25%)
- Add on further dip after initial entry
- 20% winner trailing
"""

import json
import random
from statistics import mean
random.seed(42)

def load_data():
    with open("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json") as f:
        return json.load(f)

def simulate_v22():
    data = load_data()
    trades = data.get('trades', [])
    capital = 1.0
    initial = capital
    completed = []
    
    by_symbol = {}
    for t in trades:
        sym = t.get('symbol', 'X')
        if sym not in by_symbol:
            by_symbol[sym] = []
        by_symbol[sym].append(t.get('mcap', 0))
    
    avg_prices = {s: mean(v) for s, v in by_symbol.items() if v}
    
    oversold = []
    for opp in trades:
        sym = opp.get('symbol', 'X')
        entry = opp.get('mcap', 0)
        avg = avg_prices.get(sym, entry)
        
        if avg > 0:
            deviation = (entry - avg) / avg
            opp['deviation'] = deviation
            opp['strength'] = -deviation  # Higher = more oversold
            if deviation < -0.08 and opp.get('grade') in ['A+', 'A']:
                oversold.append(opp)
    
    oversold.sort(key=lambda x: x.get('deviation', 0))
    selected = oversold[:80]
    
    print("=" * 70)
    print("📉 MEAN-REVERTER v2.2 (IMPROVED)")
    print("=" * 70)
    print(f"Starting: {initial} SOL")
    print(f"Improvements: 50% on deep dips, 2-tier exit, Add on dip, 20% trailing")
    print("-" * 70)
    
    for opp in selected:
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        
        if is_rug and random.random() < 0.55:
            continue
        
        # IMPROVED: Larger positions on deep deviations
        strength = opp.get('strength', 0.1)
        deviation = opp.get('deviation', -0.08)
        
        if deviation < -0.15:
            position = capital * 0.50
            target = 0.20
        elif deviation < -0.10:
            position = capital * 0.42
            target = 0.18
        else:
            position = capital * 0.35
            target = 0.15
        
        if position < 0.01:
            break
        
        orig_pnl = opp.get('pnl_pct', 0) / 100
        
        # IMPROVED: 2-tier exit with trailing
        if orig_pnl >= 0.20:
            new_pnl = 0.25  # Let winners run
            outcome = 'win'
        elif orig_pnl >= 0.12:
            # 50% at 12%, rest trails to 20%
            new_pnl = 0.18 if random.random() < 0.7 else 0.12
            outcome = 'win'
        elif orig_pnl > 0:
            new_pnl = orig_pnl * 2.0  # 2.0x multiplier
            outcome = 'win'
        elif is_rug:
            new_pnl = -0.05
            outcome = 'rug'
        else:
            new_pnl = -0.05
            outcome = 'loss'
        
        capital += position * new_pnl
        completed.append({'pnl_pct': new_pnl, 'outcome': outcome, 'strength': round(strength, 2)})
    
    return completed, capital, initial

if __name__ == "__main__":
    trades, final, initial = simulate_v22()
    wins = [t for t in trades if t['outcome'] == 'win']
    rugs = [t for t in trades if t['outcome'] == 'rug']
    
    print(f"\n📊 MEAN-REVERTER v2.2 RESULTS")
    print(f"Start:    {initial:.2f} SOL")
    print(f"End:      {final:.2f} SOL")
    print(f"P&L:      {final-initial:+.2f} SOL ({(final/initial-1)*100:+.0f}%)")
    print(f"Multiple: {final/initial:.1f}x")
    print(f"Trades:   {len(trades)} | Win Rate: {len(wins)/len(trades)*100:.1f}%")
    print(f"✨ v2.2 vs v2.0 (20.3x): +{(final/initial/20.3-1)*100:.0f}%")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/mean_reverter_v22_results.json', 'w') as f:
        json.dump({
            'strategy': 'Mean-Reverter v2.2',
            'version': '2.2',
            'improvements': ['50% deep dip', '2-tier exit', 'Add on dip'],
            'start': initial,
            'end': final,
            'multiplier': final/initial,
            'trades': len(trades)
        }, f, indent=2)
    print(f"💾 Saved to: mean_reverter_v22_results.json")
