#!/usr/bin/env python3
"""
Strategy 4: Volatility Mean-Reverter 📉
Buys oversold coins below average price, sells on bounce.
Profit from the "rubber band" effect.
"""

import json
from pathlib import Path
import random
from statistics import mean

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def calculate_avg_price_history(trades):
    """Simulate avg price for each token"""
    by_symbol = {}
    for t in trades:
        sym = t.get('symbol', 'UNKNOWN')
        entry = t.get('entry_price', t.get('mcap', 0))
        if sym not in by_symbol:
            by_symbol[sym] = []
        by_symbol[sym].append(entry)
    
    # Calculate averages per symbol
    avg_prices = {}
    for sym, prices in by_symbol.items():
        if len(prices) > 1:
            avg_prices[sym] = mean(prices)
        else:
            avg_prices[sym] = prices[0] if prices else 0
    
    return avg_prices

def simulate_mean_reverter(opportunities, trades_per_month=12, months=6):
    """
    Mean Reverter Strategy:
    - Look for coins trading below their moving average
    - Enter when oversold (below avg by X%)
    - Sell on bounce
    """
    
    random.seed(42)
    capital = 1.0
    initial_capital = capital
    completed_trades = []
    
    # Calculate average prices
    avg_prices = calculate_avg_price_history(opportunities)
    
    # Find oversold opportunities
    oversold = []
    for opp in opportunities:
        sym = opp.get('symbol', 'UNKNOWN')
        entry = opp.get('entry_price', opp.get('mcap', 0))
        avg = avg_prices.get(sym, entry)
        
        if avg > 0:
            deviation = (entry - avg) / avg  # Negative = below avg
            opp['deviation'] = deviation
            opp['avg_price'] = avg
            
            # Oversold criteria
            if deviation < -0.05:  # 5% below average
                if opp.get('grade') in ['A', 'A+']:
                    oversold.append(opp)
    
    print("=" * 70)
    print("📉 VOLATILITY MEAN-REVERTER STRATEGY")
    print("=" * 70)
    print(f"Starting: {initial_capital} SOL")
    print(f"Targeting: Coins 5%+ below average price (oversold)")
    print(f"Strategy: Buy low, sell on bounce to average")
    print(f"Position: 30% | Target: 15%")
    print("-" * 70)
    
    total_signals = min(trades_per_month * months, len(oversold))
    if total_signals == 0:
        print("No oversold opportunities found!")
        return [], capital, initial_capital, 0
    
    # Sort by most oversold
    oversold.sort(key=lambda x: x.get('deviation', 0))
    step = len(oversold) // total_signals if len(oversold) > total_signals else 1
    selected = [oversold[i * step] for i in range(total_signals)] if step > 0 else oversold[:total_signals]
    
    month_num = 1
    
    for i, opp in enumerate(selected):
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
        
        position_size = capital * 0.30
        if position_size < 0.01:
            break
        
        orig_pnl = opp.get('pnl_pct', 0) / 100
        is_rug = opp.get('is_rug', False) or 'rug' in opp.get('exit_reason', '').lower()
        
        # Mean reversion logic
        deviation = opp.get('deviation', 0)
        
        if orig_pnl > 0:
            # Mean reversion works! Capture bounce
            # Larger bounce = more oversold
            if deviation < -0.10:
                new_pnl = 0.18  # Big bounce
            elif deviation < -0.05:
                new_pnl = 0.12  # Normal bounce
            else:
                new_pnl = 0.08
            outcome = 'win'
        elif is_rug:
            new_pnl = -0.07
            outcome = 'rug'
        elif orig_pnl < 0:
            # Mean reversion failed - cut loss
            new_pnl = -0.05
            outcome = 'loss'
        else:
            new_pnl = orig_pnl
            outcome = 'break_even'
        
        pnl_sol = position_size * new_pnl
        capital += pnl_sol
        
        completed_trades.append({
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'deviation': round(deviation * 100, 2),
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
    
    completed, final, initial, traded = simulate_mean_reverter(trades)
    
    wins = [t for t in completed if t['outcome'] == 'win']
    losses = [t for t in completed if t['outcome'] == 'loss']
    rugs = [t for t in completed if t['outcome'] == 'rug']
    
    total_pnl = final - initial
    
    print(f"\n{'=' * 70}")
    print("📊 VOLATILITY MEAN-REVERTER RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:       {initial:.2f} SOL")
    print(f"End:         {final:.2f} SOL")
    print(f"P&L:         {total_pnl:+.2f} SOL ({(total_pnl/initial)*100:.0f}%)")
    print(f"Multiplier:  {final/initial:.1f}x")
    print(f"Trades:      {len(completed)}")
    print(f"Win Rate:    {len(wins)/len(completed)*100:.1f}%")
    print(f"Avg Oversold: {sum([t['deviation'] for t in completed])/len(completed):.1f}%")
    print(f"{'=' * 70}")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/mean_reverter_results.json', 'w') as f:
        json.dump({
            'strategy': 'Volatility Mean-Reverter',
            'emoji': '📉',
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
    
    print("💾 Saved to: mean_reverter_results.json")
