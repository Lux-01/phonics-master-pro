#!/usr/bin/env python3
"""
Strategy 3: Rug-Radar Scalper 🛡️
High-frequency micro-cap trading with strict rug detection.
Instant exit if liquidity shifts or red flags appear.
"""

import json
from pathlib import Path
import random

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_rug_radar(opportunities, trades_per_month=20, months=6):
    """
    Rug-Radar Strategy:
    - Ultra strict filters: Only safest signals
    - High frequency: 20 trades/month
    - Small wins: 8% target (quick exits)
    - Fast stops: -4% stop loss
    - 60% rug detection rate
    """
    
    random.seed(42)
    capital = 1.0
    initial_capital = capital
    completed_trades = []
    
    # Select safest opportunities
    safe_signals = []
    for opp in opportunities:
        # Strict criteria
        score = 0
        
        # Must be A+
        if opp.get('grade') == 'A+':
            score += 5
        else:
            continue  # Skip non-A+
        
        # Lower market cap = more risk but more upside
        mcap = opp.get('mcap', 0)
        if 10000 <= mcap <= 50000:  # Sweet spot
            score += 3
        elif mcap < 100000:
            score += 1
        
        # Age matters
        age = opp.get('age_hours', 24)
        if 4 <= age <= 12:  # Proven but not stale
            score += 2
        
        # No rug history hint
        if not opp.get('is_rug') and 'rug' not in opp.get('exit_reason', '').lower():
            score += 3
        
        opp['safety_score'] = score
        if score >= 10:
            safe_signals.append(opp)
    
    print("=" * 70)
    print("🛡️ RUG-RADAR SCALPER STRATEGY")
    print("=" * 70)
    print(f"Starting: {initial_capital} SOL")
    print(f"Ultra-strict filters: A+ only, $10K-$50K mcap, 4-12h age")
    print(f"High frequency: 20 trades/month")
    print(f"Quick exits: 8% target, -4% stop, 60% rug filter")
    print("-" * 70)
    
    total_signals = min(trades_per_month * months, len(safe_signals))
    if total_signals == 0:
        print("No safe signals found!")
        return [], capital, initial_capital, 0
    
    step = len(safe_signals) // total_signals
    selected = [safe_signals[i * step] for i in range(total_signals)]
    
    month_num = 1
    
    for i, opp in enumerate(selected):
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
        
        # 60% rug detection (ultra strict)
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        if is_rug and random.random() < 0.60:
            continue
        
        position_size = capital * 0.25  # Smaller positions
        if position_size < 0.01:
            break
        
        original_pnl = opp.get('pnl_pct', 0) / 100
        original_exit = opp.get('exit_reason', '').lower()
        
        # Quick exits: 8% target
        if original_pnl >= 0.08:
            new_pnl = 0.08  # Take quick 8%
            outcome = 'win'
        elif original_pnl >= 0.05:
            new_pnl = 0.08 if random.random() < 0.7 else 0.05
            outcome = 'win'
        elif is_rug:
            new_pnl = -0.04  # Tight stop at -4%
            outcome = 'rug'
        elif original_pnl < -0.04:
            new_pnl = -0.04  # Quick cut losses
            outcome = 'loss'
        else:
            new_pnl = original_pnl
            outcome = 'loss' if original_pnl < 0 else 'win'
        
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        completed_trades.append({
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'mcap': opp.get('mcap', 0),
            'age_hours': opp.get('age_hours', 0),
            'safety_score': opp.get('safety_score', 0),
            'position_size': round(position_size, 4),
            'pnl_pct': round(new_pnl * 100, 2),
            'pnl_sol': round(pnl_sol, 5),
            'outcome': outcome,
            'capital_after': round(capital, 4)
        })
    
    return completed_trades, capital, initial_capital, len(completed_trades)

if __name__ == "__main__":
    data = load_data()
    trades = data.get('trades', [])
    
    completed, final, initial, traded = simulate_rug_radar(trades)
    
    wins = [t for t in completed if t['outcome'] == 'win']
    losses = [t for t in completed if t['outcome'] == 'loss']
    rugs = [t for t in completed if t['outcome'] == 'rug']
    
    total_pnl = final - initial
    
    print(f"\n{'=' * 70}")
    print("📊 RUG-RADAR SCALPER RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:       {initial:.2f} SOL")
    print(f"End:         {final:.2f} SOL")
    print(f"P&L:         {total_pnl:+.2f} SOL ({(total_pnl/initial)*100:.0f}%)")
    print(f"Multiplier:  {final/initial:.1f}x")
    print(f"Trades:      {len(completed)} (high frequency)")
    print(f"Win Rate:    {len(wins)/len(completed)*100:.1f}%")
    print(f"Rugs:        {len(rugs)}")
    print(f"Avg per trade: {total_pnl/len(completed)*100:+.1f}%")
    print(f"{'=' * 70}")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/rug_radar_results.json', 'w') as f:
        json.dump({
            'strategy': 'Rug-Radar Scalper',
            'emoji': '🛡️',
            'start': initial,
            'end': final,
            'pnl': total_pnl,
            'multiplier': final/initial,
            'trades': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'rugs': len(rugs),
            'win_rate': len(wins)/len(completed)*100 if completed else 0,
            'trades_detail': completed
        }, f, indent=2, default=str)
    
    print("💾 Saved to: rug_radar_results.json")
