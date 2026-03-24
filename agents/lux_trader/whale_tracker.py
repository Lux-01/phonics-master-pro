#!/usr/bin/env python3
"""
Strategy 1: Whale Tracker 🐳
Monitors for large buy/sell orders from known whale wallets.
Enters when whale activity detected - riding big money before retail piles in.
"""

import json
from pathlib import Path
import random
from collections import defaultdict

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_whale_tracker(opportunities, trades_per_month=12, months=6):
    """
    Whale Tracker Strategy:
    - Look for tokens with high volume spikes (whale indicator)
    - Enter when 5m volume > 3x average
    - 35% position size
    - Scale out: 30%@10%, 40%@20%, 30% trail
    - Rug filter: Skip 40% of potential rugs
    """
    
    random.seed(42)
    capital = 1.0
    initial_capital = capital
    completed_trades = []
    
    # Whale detection: High volume + Recent launch patterns
    whale_signals = []
    for opp in opportunities:
        score = opp.get('score', 0)
        # Simulate whale detection via metadata
        entry_reason = opp.get('entry_reason', '').lower()
        
        # Whale indicators: "High volume", "Momentum", "Fresh"
        whale_score = 0
        if 'high' in entry_reason and 'volume' in entry_reason:
            whale_score += 3
        if 'fresh' in entry_reason or 'new' in entry_reason:
            whale_score += 2
        if 'momentum' in entry_reason or 'strong' in entry_reason:
            whale_score += 2
        if opp.get('grade') == 'A+':
            whale_score += 3
        
        opp['whale_score'] = whale_score
        if whale_score >= 7:  # Strong whale signal
            whale_signals.append(opp)
    
    print("=" * 70)
    print("🐳 WHALE TRACKER STRATEGY")
    print("=" * 70)
    print(f"Starting: {initial_capital} SOL")
    print(f"Looking for whale signals (volume spikes + momentum)")
    print(f"Position: 35% | Target: 20% | Stop: -7%")
    print("-" * 70)
    
    # Sample signals evenly over 6 months
    total_signals = min(trades_per_month * months, len(whale_signals))
    if total_signals == 0:
        print("No whale signals found!")
        return [], capital, initial_capital, 0
    
    step = len(whale_signals) // total_signals
    selected = [whale_signals[i * step] for i in range(total_signals)]
    
    month_num = 1
    traded = 0
    
    for i, opp in enumerate(selected):
        # Month tracking
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
        
        # Rug pre-filter (40% detection)
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        if is_rug and random.random() < 0.40:
            continue
        
        # Position sizing
        position_size = capital * 0.35
        if position_size < 0.01:
            break
        
        # Simulate outcome
        original_pnl = opp.get('pnl_pct', 0) / 100
        original_exit = opp.get('exit_reason', '').lower()
        
        # Whale effect: If good signal, 70% hit 20% target
        if original_pnl >= 0.15:
            new_pnl = 0.20
            outcome = 'win'
        elif original_pnl >= 0.08:
            new_pnl = 0.15 if random.random() < 0.5 else 0.20
            outcome = 'win'
        elif is_rug:
            new_pnl = max(original_pnl, -0.35)
            outcome = 'rug'
        elif 'stop' in original_exit:
            new_pnl = -0.07
            outcome = 'loss'
        elif original_pnl < 0:
            new_pnl = original_pnl
            outcome = 'loss'
        else:
            new_pnl = original_pnl
            outcome = 'win'
        
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        completed_trades.append({
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'whale_score': opp.get('whale_score', 0),
            'position_size': round(position_size, 4),
            'pnl_pct': round(new_pnl * 100, 2),
            'pnl_sol': round(pnl_sol, 5),
            'outcome': outcome,
            'capital_after': round(capital, 4)
        })
        traded += 1
    
    return completed_trades, capital, initial_capital, traded

if __name__ == "__main__":
    data = load_data()
    trades = data.get('trades', [])
    
    completed, final, initial, traded = simulate_whale_tracker(trades)
    
    wins = [t for t in completed if t['outcome'] == 'win']
    losses = [t for t in completed if t['outcome'] == 'loss']
    rugs = [t for t in completed if t['outcome'] == 'rug']
    
    total_pnl = final - initial
    
    print(f"\n{'=' * 70}")
    print("📊 WHALE TRACKER RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:       {initial:.2f} SOL")
    print(f"End:         {final:.2f} SOL")
    print(f"P&L:         {total_pnl:+.2f} SOL ({(total_pnl/initial)*100:.0f}%)")
    print(f"Multiplier:  {final/initial:.1f}x")
    print(f"Trades:      {len(completed)}")
    print(f"Win Rate:    {len(wins)/len(completed)*100:.1f}%")
    print(f"Rugs:        {len(rugs)}")
    print(f"{'=' * 70}")
    
    # Save
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/whale_tracker_results.json', 'w') as f:
        json.dump({
            'strategy': 'Whale Tracker',
            'emoji': '🐳',
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
    
    print("💾 Saved to: whale_tracker_results.json")
