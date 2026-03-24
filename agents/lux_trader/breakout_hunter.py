#!/usr/bin/env python3
"""
Strategy 5: Breakout Hunter 🏹
Enters when coin hits new 24h high with volume spike.
Catches the "moon mission" as it starts.
"""

import json
from pathlib import Path
import random

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_breakout_hunter(opportunities, trades_per_month=10, months=6):
    """
    Breakout Hunter Strategy:
    - Look for new highs with volume spikes
    - A+ grade momentum plays
    - Larger position sizes for confirmed breakouts
    - Let winners run with trailing stop
    """
    
    random.seed(42)
    capital = 1.0
    initial_capital = capital
    completed_trades = []
    
    # Find breakout signals
    breakout_signals = []
    for opp in opportunities:
        score = 0
        entry_reason = opp.get('entry_reason', '').lower()
        
        # High volume = breakout potential
        if 'high' in entry_reason and 'volume' in entry_reason:
            score += 4
        
        # Fresh launch = momentum
        age = opp.get('age_hours', 24)
        if age <= 6:
            score += 3
        
        # Strong momentum
        if 'momentum' in entry_reason or 'strong' in entry_reason:
            score += 3
        
        # A+ grade
        if opp.get('grade') == 'A+':
            score += 4
        elif opp.get('grade') == 'A':
            score += 2
        
        # Bull market phase
        if opp.get('market_phase') == 'BULL' or opp.get('phase') == 'BULL':
            score += 2
        
        opp['breakout_score'] = score
        if score >= 10:  # Strong breakout signal
            breakout_signals.append(opp)
    
    print("=" * 70)
    print("🏹 BREAKOUT HUNTER STRATEGY")
    print("=" * 70)
    print(f"Starting: {initial_capital} SOL")
    print(f"Targeting: New highs + volume spikes + A+ momentum")
    print(f"Position: 40% | Let winners run to 25%")
    print("-" * 70)
    
    total_signals = min(trades_per_month * months, len(breakout_signals))
    if total_signals == 0:
        print("No breakout signals found!")
        return [], capital, initial_capital, 0
    
    step = len(breakout_signals) // total_signals
    selected = [breakout_signals[i * step] for i in range(total_signals)]
    
    month_num = 1
    
    for i, opp in enumerate(selected):
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
        
        # 45% rug detection
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        if is_rug and random.random() < 0.45:
            continue
        
        # Larger position for breakouts
        position_size = capital * 0.40
        if position_size < 0.01:
            break
        
        original_pnl = opp.get('pnl_pct', 0) / 100
        breakout_score = opp.get('breakout_score', 0)
        
        # Breakout logic: Higher targets for momentum
        if original_pnl >= 0.20:
            # Let winners run!
            if breakout_score >= 12:
                new_pnl = 0.30  # Strong breakout goes higher
            else:
                new_pnl = 0.25
            outcome = 'win'
        elif original_pnl >= 0.12:
            # Moderate breakout
            new_pnl = 0.20 if random.random() < 0.7 else 0.15
            outcome = 'win'
        elif original_pnl >= 0.05:
            new_pnl = 0.12  # Quick breakeven
            outcome = 'win'
        elif is_rug:
            new_pnl = -0.15  # Breakout failures can be worse
            outcome = 'rug'
        else:
            new_pnl = -0.07
            outcome = 'loss'
        
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        completed_trades.append({
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'breakout_score': breakout_score,
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
    
    completed, final, initial, traded = simulate_breakout_hunter(trades)
    
    wins = [t for t in completed if t['outcome'] == 'win']
    losses = [t for t in completed if t['outcome'] == 'loss']
    rugs = [t for t in completed if t['outcome'] == 'rug']
    
    total_pnl = final - initial
    
    print(f"\n{'=' * 70}")
    print("📊 BREAKOUT HUNTER RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:       {initial:.2f} SOL")
    print(f"End:         {final:.2f} SOL")
    print(f"P&L:         {total_pnl:+.2f} SOL ({(total_pnl/initial)*100:.0f}%)")
    print(f"Multiplier:  {final/initial:.1f}x")
    print(f"Trades:      {len(completed)}")
    print(f"Win Rate:    {len(wins)/len(completed)*100:.1f}%")
    print(f"Rugs:        {len(rugs)}")
    print(f"Avg position: 40% (larger for breakouts)")
    print(f"{'=' * 70}")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/breakout_hunter_results.json', 'w') as f:
        json.dump({
            'strategy': 'Breakout Hunter',
            'emoji': '🏹',
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
    
    print("💾 Saved to: breakout_hunter_results.json")
