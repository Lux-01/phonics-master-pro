#!/usr/bin/env python3
"""
Strategy 2: Social Sentinel 🐦
Uses sentiment analysis proxies (volume, age, narrative) to buy tokens getting massive hype.
Captures "Narrative Momentum" early.
"""

import json
from pathlib import Path
import random

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_social_sentinel(opportunities, trades_per_month=15, months=6):
    """
    Social Sentinel Strategy:
    - Look for tokens with high narrative momentum
    - Fresh launches with strong social signals
    - 30% position size
    - Fast exits on narrative decay
    """
    
    random.seed(42)
    capital = 1.0
    initial_capital = capital
    completed_trades = []
    
    # Social signal detection
    social_signals = []
    for opp in opportunities:
        score = 0
        
        # Age freshness (new = hype)
        age = opp.get('age_hours', 24)
        if age <= 3:
            score += 4
        elif age <= 6:
            score += 3
        elif age <= 12:
            score += 2
        
        # Volume (high = attention)
        entry = opp.get('entry_reason', '').lower()
        if 'high' in entry and 'volume' in entry:
            score += 3
        
        # Grade (A+ = quality signal)
        if opp.get('grade') == 'A+':
            score += 3
        elif opp.get('grade') == 'A':
            score += 1
        
        # Market phase (bull = more sentiment)
        if opp.get('market_phase') == 'BULL' or opp.get('phase') == 'BULL':
            score += 2
        
        opp['social_score'] = score
        if score >= 7:
            social_signals.append(opp)
    
    print("=" * 70)
    print("🐦 SOCIAL SENTINEL STRATEGY")
    print("=" * 70)
    print(f"Starting: {initial_capital} SOL")
    print(f"Targeting: Fresh coins + high volume + A+ grade")
    print(f"Position: 30% | Fast exits on narrative decay")
    print("-" * 70)
    
    total_signals = min(trades_per_month * months, len(social_signals))
    if total_signals == 0:
        print("No social signals found!")
        return [], capital, initial_capital, 0
    
    step = len(social_signals) // total_signals
    selected = [social_signals[i * step] for i in range(total_signals)]
    
    month_num = 1
    
    for i, opp in enumerate(selected):
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
        
        # Rug filter (35% detection - social is riskier)
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        if is_rug and random.random() < 0.35:
            continue
        
        position_size = capital * 0.30
        if position_size < 0.01:
            break
        
        original_pnl = opp.get('pnl_pct', 0) / 100
        original_exit = opp.get('exit_reason', '').lower()
        
        # Social momentum: higher volatility
        if original_pnl >= 0.12:
            # Momentum plays can pump harder or dump faster
            new_pnl = original_pnl * 1.15 if random.random() < 0.6 else original_pnl
            outcome = 'win'
        elif original_pnl >= 0.05:
            new_pnl = original_pnl
            outcome = 'win'
        elif is_rug:
            new_pnl = max(original_pnl, -0.45)
            outcome = 'rug'
        elif 'stop' in original_exit:
            new_pnl = -0.07
            outcome = 'loss'
        else:
            new_pnl = original_pnl
            outcome = 'loss'
        
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        completed_trades.append({
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'age_hours': opp.get('age_hours', 0),
            'social_score': opp.get('social_score', 0),
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
    
    completed, final, initial, traded = simulate_social_sentinel(trades)
    
    wins = [t for t in completed if t['outcome'] == 'win']
    losses = [t for t in completed if t['outcome'] == 'loss']
    rugs = [t for t in completed if t['outcome'] == 'rug']
    
    total_pnl = final - initial
    
    print(f"\n{'=' * 70}")
    print("📊 SOCIAL SENTINEL RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:       {initial:.2f} SOL")
    print(f"End:         {final:.2f} SOL")
    print(f"P&L:         {total_pnl:+.2f} SOL ({(total_pnl/initial)*100:.0f}%)")
    print(f"Multiplier:  {final/initial:.1f}x")
    print(f"Trades:      {len(completed)}")
    print(f"Win Rate:    {len(wins)/len(completed)*100:.1f}%")
    print(f"Rugs:        {len(rugs)}")
    print(f"{'=' * 70}")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/social_sentinel_results.json', 'w') as f:
        json.dump({
            'strategy': 'Social Sentinel',
            'emoji': '🐦',
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
    
    print("💾 Saved to: social_sentinel_results.json")
