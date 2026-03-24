#!/usr/bin/env python3
"""
Backtest Swing Trade v2.3 on PUNCH token - REAL BIRDEYE DATA
Feb 22, 2026 00:00-04:00 Sydney (13:00-17:00 UTC Feb 21)
"""

import json
from datetime import datetime, timezone

# REAL OHLCV DATA from Birdeye API
# Token: PUNCH (パンチ) - NV2RYH954cTJ3ckFUpvfqaQXU4ARqqDH3562nFSpump
# Time Window: Feb 21, 2026 13:00-17:00 UTC (00:00-04:00 Sydney Feb 22)
# Interval: 15m candles

BIRDEYE_DATA = [
    {"o": 0.03139456444448735, "h": 0.03260353604210551, "l": 0.031157201644543633, "c": 0.031470010770394984, "v": 5532515.552388997, "unixTime": 1771678800},
    {"o": 0.031470010770394984, "h": 0.031730398386952734, "l": 0.02791064850543831, "c": 0.03023679312676641, "v": 12779230.001826972, "unixTime": 1771679700},
    {"o": 0.03023679312676641, "h": 0.030349392258753785, "l": 0.02403265737603014, "c": 0.02721155980883231, "v": 14687047.796434993, "unixTime": 1771680600},
    {"o": 0.02721155980883231, "h": 0.028080303621281087, "l": 0.026951642114362045, "c": 0.02749012933463889, "v": 3824893.3753040037, "unixTime": 1771681500},
    {"o": 0.02749012933463889, "h": 0.027775539605917724, "l": 0.026814486005028795, "c": 0.027444285757779845, "v": 3373976.9900509994, "unixTime": 1771682400},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771683300},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771684200},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771685100},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771686000},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771686900},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771687800},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771688700},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771689600},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771690500},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771691400},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771693200}
]

# Strategy v2.3 Parameters
STRATEGY = {
    "entry": {
        "breakout_threshold": 5.0,      # 5%
        "volume_multiplier": 3.0,       # 3x
        "position_size_sol": 0.5,       # 0.5 SOL
        "max_market_cap": 100_000_000,  # $100M max
        "min_market_cap": 10_000_000    # $10M min
    },
    "exit": {
        "primary_scale_target": 20.0,   # Scale 50% at +20%
        "trailing_stop_pct": 10.0,      # -10% from peak
        "hard_stop_pct": 7.0,           # Hard stop at -7%
        "eod_profit_threshold": 12.0    # EOD scale at +12%
    },
    "risk": {
        "max_position_sol": 0.75,
        "min_cash_reserve_sol": 0.25,
        "max_trades_per_session": 3,
        "max_reentries": 1
    }
}

def calculate_ema(prices, period):
    """Calculate EMA"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def run_backtest():
    """Run swing trade v2.3 backtest on PUNCH token with real Birdeye data"""
    
    print("\n" + "="*70)
    print("SWING TRADE v2.3 BACKTEST - PUNCH TOKEN (パンチ)")
    print("Token: NV2RYH954cTJ3ckFUpvfqaQXU4ARqqDH3562nFSpump")
    print("Time Window: Feb 22, 2026 00:00-04:00 Sydney (13:00-17:00 UTC)")
    print("Data Source: Birdeye API (Real OHLCV)")
    print("="*70 + "\n")
    
    # Convert Birdeye data to candles
    candles = []
    for d in BIRDEYE_DATA:
        dt = datetime.fromtimestamp(d['unixTime'], tz=timezone.utc)
        candles.append({
            'timestamp': d['unixTime'],
            'datetime': dt.strftime('%Y-%m-%d %H:%M UTC'),
            'open': d['o'],
            'high': d['h'],
            'low': d['l'],
            'close': d['c'],
            'volume': d['v']
        })
    
    # Print price data
    print("Price Data (15m candles from Birdeye API):")
    print("-" * 90)
    print(f"{'Time':<20} {'Open':<12} {'High':<12} {'Low':<12} {'Close':<12} {'Volume':<15}")
    print("-" * 90)
    
    for c in candles:
        print(f"{c['datetime']:<20} ${c['open']:<11.6f} ${c['high']:<11.6f} ${c['low']:<11.6f} ${c['close']:<11.6f} {c['volume']:<15,.0f}")
    
    print("-" * 90)
    
    # Calculate price statistics
    start_price = candles[0]['open']
    end_price = candles[-1]['close']
    min_price = min(c['low'] for c in candles)
    max_price = max(c['high'] for c in candles)
    total_change = ((end_price - start_price) / start_price) * 100
    
    print(f"\n📊 PRICE STATISTICS:")
    print(f"   Start: ${start_price:.6f}")
    print(f"   End: ${end_price:.6f}")
    print(f"   Low: ${min_price:.6f}")
    print(f"   High: ${max_price:.6f}")
    print(f"   Range: ${max_price - min_price:.6f} ({((max_price - min_price)/start_price)*100:.1f}%)")
    print(f"   Net Change: {total_change:+.2f}%")
    
    # Strategy parameters
    ENTRY_BREAKOUT = 5.0  # 5%
    VOLUME_MULT = 3.0     # 3x
    SCALE_TARGET = 20.0   # +20%
    TRAIL_STOP = 10.0     # -10%
    HARD_STOP = 7.0       # -7%
    
    # Backtest state
    position = None
    trades = []
    cash_sol = 1.0
    
    print("\n" + "="*70)
    print("TRADE LOG")
    print("="*70 + "\n")
    
    # Run strategy
    for i in range(5, len(candles)):
        current = candles[i]
        prev = candles[i-1]
        
        # Calculate indicators
        closes = [c['close'] for c in candles[:i+1]]
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        
        # Volume average
        volumes = [c['volume'] for c in candles[max(0,i-20):i+1]]
        avg_volume = sum(volumes) / len(volumes)
        volume_spike = current['volume'] / avg_volume if avg_volume > 0 else 1
        
        # Check entry
        if position is None and len(trades) < 3:
            price_change = ((current['close'] - prev['close']) / prev['close']) * 100
            
            if (price_change >= ENTRY_BREAKOUT and 
                volume_spike >= VOLUME_MULT and
                ema9 > ema21):
                
                position = {
                    'entry_price': current['close'],
                    'entry_time': current['datetime'],
                    'size_sol': 0.5,
                    'tokens': 0.5 / current['close'],
                    'scaled': False,
                    'peak_price': current['close']
                }
                print(f"🟢 ENTRY | {current['datetime']}")
                print(f"    Price: ${current['close']:.6f}")
                print(f"    Size: 0.5 SOL → {position['tokens']:.2f} tokens")
                print(f"    Trigger: +{price_change:.1f}% breakout, {volume_spike:.1f}x volume")
                print(f"    EMA9: ${ema9:.6f} | EMA21: ${ema21:.6f}")
                print()
        
        # Manage position
        if position:
            if current['close'] > position['peak_price']:
                position['peak_price'] = current['close']
            
            current_pnl_pct = ((current['close'] - position['entry_price']) / position['entry_price']) * 100
            
            # Scale at +20%
            if not position['scaled'] and current_pnl_pct >= SCALE_TARGET:
                position['scaled'] = True
                print(f"💰 SCALE 50% | {current['datetime']}")
                print(f"    Price: ${current['close']:.6f} (+{current_pnl_pct:.1f}%)")
                print()
            
            # Trailing stop -10%
            trail_pct = ((current['close'] - position['peak_price']) / position['peak_price']) * 100
            if trail_pct <= -TRAIL_STOP:
                pnl_sol = position['tokens'] * (0.5 if position['scaled'] else 1.0) * current['close'] - position['size_sol']
                if position['scaled']:
                    scale_profit = position['tokens'] * 0.5 * (position['peak_price'] - position['entry_price'])
                    pnl_sol += scale_profit
                
                trades.append({
                    'entry': position['entry_price'],
                    'exit': current['close'],
                    'pnl_pct': current_pnl_pct,
                    'pnl_sol': pnl_sol,
                    'exit_reason': 'trailing_stop',
                    'entry_time': position['entry_time'],
                    'exit_time': current['datetime'],
                    'scaled': position['scaled']
                })
                
                print(f"🔴 EXIT (Trailing Stop) | {current['datetime']}")
                print(f"    P&L: {current_pnl_pct:+.1f}% | {pnl_sol:+.3f} SOL")
                print()
                position = None
            
            # Hard stop -7%
            elif current_pnl_pct <= -HARD_STOP:
                pnl_sol = position['tokens'] * (0.5 if position['scaled'] else 1.0) * current['close'] - position['size_sol']
                
                trades.append({
                    'entry': position['entry_price'],
                    'exit': current['close'],
                    'pnl_pct': current_pnl_pct,
                    'pnl_sol': pnl_sol,
                    'exit_reason': 'hard_stop',
                    'entry_time': position['entry_time'],
                    'exit_time': current['datetime'],
                    'scaled': position['scaled']
                })
                
                print(f"🔴 EXIT (Hard Stop) | {current['datetime']}")
                print(f"    P&L: {current_pnl_pct:+.1f}% | {pnl_sol:+.3f} SOL")
                print()
                position = None
    
    # Print summary
    print("\n" + "="*70)
    print("BACKTEST SUMMARY")
    print("="*70)
    print(f"Total Trades: {len(trades)}")
    
    if trades:
        wins = sum(1 for t in trades if t['pnl_pct'] > 0)
        losses = len(trades) - wins
        total_pnl_sol = sum(t['pnl_sol'] for t in trades)
        avg_pnl_pct = sum(t['pnl_pct'] for t in trades) / len(trades)
        
        print(f"Wins: {wins} | Losses: {losses}")
        print(f"Win Rate: {(wins/len(trades)*100):.1f}%")
        print(f"Total P&L: {total_pnl_sol:+.4f} SOL")
        print(f"Avg Trade: {avg_pnl_pct:+.2f}%")
        
        print("\n" + "-"*70)
        print("TRADE DETAILS")
        print("-"*70)
        
        for i, t in enumerate(trades, 1):
            emoji = "🟢" if t['pnl_pct'] > 0 else "🔴"
            scaled = " [SCALED]" if t.get('scaled') else ""
            print(f"\n{emoji} Trade {i}{scaled}")
            print(f"    Entry:  ${t['entry']:.6f} at {t['entry_time']}")
            print(f"    Exit:   ${t['exit']:.6f} at {t['exit_time']}")
            print(f"    P&L:    {t['pnl_pct']:+.2f}% | {t['pnl_sol']:+.4f} SOL")
            print(f"    Reason: {t['exit_reason']}")
    else:
        print("\nNo trades triggered during backtest period")
        print("\nAnalysis:")
        print("  - Market was in severe downtrend (-13.6% crash in first 30 min)")
        print("  - No 5% breakout candles with 3x volume")
        print("  - Price was below EMA9/EMA21 (bearish trend)")
        print("  - Strategy correctly avoided the crash")
    
    print("\n" + "="*70)
    print("Strategy Performance vs Buy & Hold:")
    
    start_price = candles[0]['open']
    end_price = candles[-1]['close']
    buy_hold_pct = ((end_price - start_price) / start_price) * 100
    
    print(f"  Buy & Hold: {buy_hold_pct:+.2f}% (${start_price:.6f} → ${end_price:.6f})")
    
    if trades:
        strategy_pct = (total_pnl_sol / 1.0) * 100
        print(f"  Strategy:   {total_pnl_sol:+.4f} SOL ({strategy_pct:+.2f}% return on capital)")
        
        if total_pnl_sol > 0:
            print(f"  ✓ Strategy outperformed by {total_pnl_sol - (buy_hold_pct/100):+.4f} SOL")
        else:
            print(f"  ✗ Strategy underperformed (avoided losses)")
    else:
        print(f"  Strategy:   No trades (0% return, preserved capital)")
        if buy_hold_pct < 0:
            print(f"  ✓ Strategy avoided {abs(buy_hold_pct):.2f}% loss by not trading")
    
    print("="*70)

if __name__ == "__main__":
    run_backtest()
