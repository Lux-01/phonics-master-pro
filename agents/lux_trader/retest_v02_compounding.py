#!/usr/bin/env python3
"""
Retest Strategy v0.2 with compounding
Starting capital: 1 SOL
Position size: 30% of available capital per trade (0.3 SOL initially)
"""

import json
from pathlib import Path
import random

def load_data():
    """Load 6-month backtest data"""
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_compounding(opportunities, max_positions=3):
    """
    Simulate with compounding:
    - Use 30% of current capital per trade
    - Reinvest all profits  
    - Max 3 simultaneous positions
    """
    
    capital = 1.0  # Starting with 1 SOL
    initial_capital = capital
    positions = []  # Active positions
    completed_trades = []
    trade_num = 0
    peak_capital = capital
    
    print("=" * 70)
    print("🧪 LUXTRADER v0.2 WITH COMPOUNDING")
    print("=" * 70)
    print(f"Starting Capital: {initial_capital} SOL")
    print(f"Strategy: A+ only, 20% target, -7% stop, 30% position size")
    print(f"Max Positions: {max_positions}")
    print(f"Mode: Full compounding (reinvest all profits)")
    print("-" * 70)
    
    for opp in opportunities:
        # Skip if not A+ grade
        if opp.get('grade') != 'A+':
            continue
        
        # Calculate position size: 30% of current capital
        position_size = capital * 0.30
        
        # Need minimum 0.01 SOL
        if position_size < 0.01:
            break
            
        # Check if we can open new position
        if len(positions) >= max_positions:
            # Close oldest position first (FIFO)
            closed = positions.pop(0)
            capital += closed['position_size'] + closed['pnl_sol']
            completed_trades.append(closed)
            
            # Track peak
            peak_capital = max(peak_capital, capital)
            
            # Progress
            if len(completed_trades) % 25 == 0:
                print(f"  Trade {len(completed_trades):3d}: Capital = {capital:.3f} SOL ({capital/initial_capital:.2f}x)")
        
        # Calculate position size again (may have changed)
        position_size = min(capital * 0.30, capital - 0.01)  # Keep 0.01 buffer
        if position_size < 0.01:
            break
        
        # Simulate trade outcome
        original_pnl = opp.get('pnl_pct', 0) / 100
        original_exit = opp.get('exit_reason', '').lower()
        is_rug = opp.get('is_rug', False) or 'rug' in original_exit
        
        # Determine outcome with v0.2 rules
        if ('target' in original_exit or 'manual' in original_exit) and original_pnl >= 0.10:
            new_pnl = 0.20
            new_exit = 'target_hit'
            outcome = 'win'
        elif is_rug:
            new_pnl = max(original_pnl, -0.50)
            new_exit = 'rug'
            outcome = 'rug'
        elif 'stop' in original_exit and original_pnl < 0:
            new_pnl = -0.07
            new_exit = 'stop_loss'
            outcome = 'loss'
        elif original_pnl > 0.05:
            if random.random() < 0.60:
                new_pnl = 0.20
                new_exit = 'target_hit'
                outcome = 'win'
            else:
                new_pnl = original_pnl
                new_exit = 'manual_exit'
                outcome = 'win'
        elif original_pnl > 0:
            new_pnl = original_pnl
            new_exit = 'manual_exit'
            outcome = 'win'
        elif original_pnl < 0:
            new_pnl = original_pnl
            new_exit = 'time_stop'
            outcome = 'loss'
        else:
            new_pnl = 0
            new_exit = 'break_even'
            outcome = 'break_even'
        
        # Calculate P&L in SOL
        pnl_sol = position_size * new_pnl
        
        position = {
            'trade_num': len(completed_trades) + len(positions) + 1,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'position_size': round(position_size, 4),
            'pnl_pct': round(new_pnl * 100, 2),
            'pnl_sol': round(pnl_sol, 5),
            'exit_reason': new_exit,
            'outcome': outcome
        }
        
        positions.append(position)
        capital -= position_size  # Lock up capital
        trade_num += 1
    
    # Close all remaining positions
    for pos in positions:
        capital += pos['position_size'] + pos['pnl_sol']
        completed_trades.append(pos)
        peak_capital = max(peak_capital, capital)
    
    return completed_trades, capital, initial_capital, peak_capital

def analyze_results(trades, final_capital, initial_capital, peak_capital):
    """Analyze compounding results"""
    
    wins = [t for t in trades if t['outcome'] == 'win']
    losses = [t for t in trades if t['outcome'] == 'loss']
    rugs = [t for t in trades if t['outcome'] == 'rug']
    
    win_pnl = [t['pnl_sol'] for t in wins]
    loss_pnl = [t['pnl_sol'] for t in losses]
    rug_pnl = [t['pnl_sol'] for t in rugs]
    
    total_pnl_sol = final_capital - initial_capital
    total_return_multiple = final_capital / initial_capital
    
    print(f"\n{'=' * 70}")
    print("📊 COMPOUNDING RESULTS")
    print(f"{'=' * 70}")
    print(f"\n💰 CAPITAL:")
    print(f"  Start:        {initial_capital:.4f} SOL")
    print(f"  End:          {final_capital:.4f} SOL")
    print(f"  Peak:         {peak_capital:.4f} SOL")
    print(f"  P&L SOL:      {total_pnl_sol:+.4f}")
    print(f"  Return:       {total_return_multiple:.2f}x ({(total_return_multiple-1)*100:+.0f}%)")
    
    print(f"\n📈 TRADE SUMMARY:")
    print(f"  Total Trades: {len(trades)}")
    print(f"  Wins:         {len(wins)}")
    print(f"  Losses:       {len(losses)}")
    print(f"  Rugs:         {len(rugs)}")
    print(f"  Win Rate:     {len(wins)/len(trades)*100:.1f}%")
    
    if wins:
        print(f"\n✅ WIN METRICS:")
        print(f"  Total Profit: {sum(win_pnl):+.4f} SOL")
        print(f"  Avg Profit:   {sum(win_pnl)/len(win_pnl):+.4f} SOL")
    
    if losses:
        print(f"\n❌ LOSS METRICS:")
        print(f"  Total Loss:   {sum(loss_pnl):+.4f} SOL")
        print(f"  Avg Loss:     {sum(loss_pnl)/len(loss_pnl):+.4f} SOL")
    
    if rugs:
        print(f"\n🪦 RUG METRICS:")
        print(f"  Count:        {len(rugs)} ({len(rugs)/len(trades)*100:.1f}%)")
        print(f"  Total Loss:   {sum(rug_pnl):+.4f} SOL")
        print(f"  Avg Loss:     {sum(rug_pnl)/len(rug_pnl):+.4f} SOL")
    
    # Exit breakdown
    from collections import defaultdict
    by_exit = defaultdict(list)
    for t in trades:
        by_exit[t['exit_reason']].append(t['pnl_sol'])
    
    print(f"\n🎯 EXIT BREAKDOWN:")
    for reason, pnls in sorted(by_exit.items(), key=lambda x: -sum(x[1])):
        total = sum(pnls)
        count = len(pnls)
        avg = total / count if count else 0
        print(f"  {reason:15s}: {count:3d} trades, {total:+7.3f} SOL, {avg:+7.4f} avg")
    
    print(f"\n📊 PERFORMANCE:")
    print(f"  Max Drawdown: {peak_capital - final_capital:.4f} SOL ({(1 - final_capital/peak_capital)*100:.1f}%)")
    print(f"  Profit Factor: {abs(sum(win_pnl))/abs(sum(loss_pnl + rug_pnl)):.2f}" if (losses or rugs) else "  N/A")
    
    print("\n" + "=" * 70)
    
    return {
        'start_capital': initial_capital,
        'end_capital': final_capital,
        'peak_capital': peak_capital,
        'pnl_sol': total_pnl_sol,
        'return_multiple': total_return_multiple,
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'rugs': len(rugs),
        'win_rate': len(wins)/len(trades)*100 if trades else 0
    }

random.seed(42)

if __name__ == "__main__":
    data = load_data()
    trades_data = data.get('trades', [])
    
    print(f"Loaded {len(trades_data)} total trades")
    
    # Filter to A+ only
    a_plus_trades = [t for t in trades_data if t.get('grade') == 'A+']
    print(f"A+ trades: {len(a_plus_trades)}")
    
    # Run simulation
    completed_trades, final_capital, initial_capital, peak = simulate_compounding(a_plus_trades)
    results = analyze_results(completed_trades, final_capital, initial_capital, peak)
    
    # Save results
    results_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/retest_v02_compound.json")
    with open(results_file, 'w') as f:
        json.dump({
            'strategy': 'v0.2 with compounding',
            'parameters': {
                'starting_capital': 1.0,
                'position_size_pct': 0.30,
                'compounding': True,
                'max_positions': 3
            },
            'results': results,
            'trades': completed_trades
        }, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
