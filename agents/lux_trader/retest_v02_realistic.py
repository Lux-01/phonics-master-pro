#!/usr/bin/env python3
"""
Realistic LuxTrader v0.2 Simulation
Limits: 15 trades/month (realistic signal frequency)
Starting: 1 SOL
"""

import json
from pathlib import Path
import random

def load_data():
    """Load 6-month backtest data"""
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

def simulate_realistic(opportunities, trades_per_month=15, months=6, max_positions=3):
    """
    Simulate realistic trading:
    - Only 15 trades per month (not all A+ signals)
    - Spread evenly across 6 months
    - Still use 30% position size with compounding
    """
    
    capital = 1.0
    initial_capital = capital
    positions = []
    completed_trades = []
    peak_capital = capital
    
    total_available = len(opportunities)
    trades_to_simulate = min(trades_per_month * months, total_available)
    
    # Sample trades evenly from the dataset
    step = total_available // trades_to_simulate
    selected_trades = [opportunities[i * step] for i in range(trades_to_simulate)]
    
    print("=" * 70)
    print("🧪 REALISTIC LUXTRADER v0.2 SIMULATION")
    print("=" * 70)
    print(f"Starting Capital: {initial_capital} SOL")
    print(f"Trade Limit: {trades_per_month} per month x {months} months = {trades_to_simulate} trades")
    print(f"Position Size: 30% of capital")
    print(f"Max Positions: {max_positions}")
    print("-" * 70)
    
    month_num = 1
    trades_this_month = 0
    
    for i, opp in enumerate(selected_trades):
        # Track month
        if i > 0 and i % trades_per_month == 0:
            month_num += 1
            trades_this_month = 0
            print(f"\n📅 Month {month_num}: Capital = {capital:.3f} SOL")
        
        # Skip if not A+ grade
        if opp.get('grade') != 'A+':
            continue
        
        # Calculate position size
        position_size = capital * 0.30
        if position_size < 0.01:
            print(f"⚠️  Insufficient capital ({capital:.3f} SOL), stopping")
            break
        
        # Check max positions
        if len(positions) >= max_positions:
            closed = positions.pop(0)
            capital += closed['position_size'] + closed['pnl_sol']
            completed_trades.append(closed)
            peak_capital = max(peak_capital, capital)
        
        # Recalculate position size
        position_size = min(capital * 0.30, capital - 0.01)
        if position_size < 0.01:
            break
        
        # Simulate outcome
        original_pnl = opp.get('pnl_pct', 0) / 100
        original_exit = opp.get('exit_reason', '').lower()
        is_rug = opp.get('is_rug', False) or 'rug' in original_exit
        
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
        
        pnl_sol = position_size * new_pnl
        
        position = {
            'trade_num': len(completed_trades) + len(positions) + 1,
            'month': month_num,
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'position_size': round(position_size, 4),
            'pnl_pct': round(new_pnl * 100, 2),
            'pnl_sol': round(pnl_sol, 5),
            'exit_reason': new_exit,
            'outcome': outcome
        }
        
        positions.append(position)
        capital -= position_size
        trades_this_month += 1
    
    # Close remaining
    for pos in positions:
        capital += pos['position_size'] + pos['pnl_sol']
        completed_trades.append(pos)
        peak_capital = max(peak_capital, capital)
    
    return completed_trades, capital, initial_capital, peak_capital

def analyze_results(trades, final_capital, initial_capital, peak_capital):
    """Analyze results"""
    
    wins = [t for t in trades if t['outcome'] == 'win']
    losses = [t for t in trades if t['outcome'] == 'loss']
    rugs = [t for t in trades if t['outcome'] == 'rug']
    
    win_pnl = [t['pnl_sol'] for t in wins]
    loss_pnl = [t['pnl_sol'] for t in losses]
    rug_pnl = [t['pnl_sol'] for t in rugs]
    
    total_pnl = final_capital - initial_capital
    
    print(f"\n{'=' * 70}")
    print("📊 REALISTIC RESULTS")
    print(f"{'=' * 70}")
    print(f"\n💰 CAPITAL:")
    print(f"  Start:        {initial_capital:.4f} SOL")
    print(f"  End:          {final_capital:.4f} SOL")
    print(f"  Peak:         {peak_capital:.4f} SOL")
    print(f"  P&L:          {total_pnl:+.4f} SOL ({(total_pnl/initial_capital)*100:+.0f}%)")
    print(f"  Multiplier:   {final_capital/initial_capital:.2f}x")
    
    print(f"\n📈 TRADE SUMMARY:")
    print(f"  Total:        {len(trades)} trades")
    print(f"  Wins:         {len(wins)}")
    print(f"  Losses:       {len(losses)}")
    print(f"  Rugs:         {len(rugs)}")
    print(f"  Win Rate:     {len(wins)/len(trades)*100:.1f}%")
    
    # By month
    by_month = {}
    for t in trades:
        m = t.get('month', 1)
        if m not in by_month:
            by_month[m] = []
        by_month[m].append(t)
    
    print(f"\n📅 MONTHLY BREAKDOWN:")
    running = initial_capital
    for month in sorted(by_month.keys()):
        m_trades = by_month[month]
        m_pnl = sum(t['pnl_sol'] for t in m_trades)
        running += m_pnl
        m_wins = len([t for t in m_trades if t['outcome'] == 'win'])
        print(f"  Month {month}: {len(m_trades):2d} trades, {m_wins} wins, {m_pnl:+6.3f} SOL, Cap: {running:.3f}")
    
    if wins:
        print(f"\n✅ WIN METRICS:")
        print(f"  Total Profit: {sum(win_pnl):+.3f} SOL")
        print(f"  Avg Profit:   {sum(win_pnl)/len(win_pnl):+.3f} SOL")
    
    if losses or rugs:
        total_loss = sum(loss_pnl) + sum(rug_pnl)
        print(f"\n❌ LOSS METRICS:")
        print(f"  Total Loss:   {total_loss:.3f} SOL")
    
    print(f"\n💡 SCENARIOS:")
    print(f"  1.0 SOL start → {final_capital:.2f} SOL ({final_capital:.1f}x)")
    print(f"  5.0 SOL start → {final_capital*5:.2f} SOL")
    print(f"  10.0 SOL start → {final_capital*10:.2f} SOL")
    
    print("\n" + "=" * 70)
    
    return {
        'start': initial_capital,
        'end': final_capital,
        'peak': peak_capital,
        'pnl': total_pnl,
        'multiplier': final_capital/initial_capital,
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
    
    # Filter to A+ only
    a_plus = [t for t in trades_data if t.get('grade') == 'A+']
    
    print(f"Total A+ trades in dataset: {len(a_plus)}")
    print(f"Selecting realistic subset...\n")
    
    # Run simulation
    completed, final, initial, peak = simulate_realistic(a_plus, trades_per_month=15, months=6)
    results = analyze_results(completed, final, initial, peak)
    
    # Save
    results_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/retest_v02_realistic.json")
    with open(results_file, 'w') as f:
        json.dump({
            'strategy': 'v0.2 realistic (15 trades/month)',
            'parameters': {
                'trades_per_month': 15,
                'months': 6,
                'position_size_pct': 0.30,
                'max_positions': 3
            },
            'results': results,
            'trades': completed
        }, f, indent=2, default=str)
    
    print(f"\n💾 Saved to: {results_file}")
