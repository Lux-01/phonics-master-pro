#!/usr/bin/env python3
"""
Smart Swing v2.1 Strategy Backtest
Token: 67 (9AvytnUKsLxPxFHFqS6VLxaxt5p6BhYNr53SD2Chpump)
"""

import json
from datetime import datetime

# Token data from DexScreener
TOKEN = {
    "name": "67",
    "symbol": "67",
    "ca": "9AvytnUKsLxPxFHFqS6VLxaxt5p6BhYNr53SD2Chpump",
    "current_price": 0.002951,
    "mcap": 2949988,
    "volume_24h": 265780,
    "priceChange_h24": 24.84,
    "priceChange_h6": 6.63,
    "priceChange_h1": -2.56
}

# Generate realistic price action based on actual 24h +24% pump
# Started around $0.00237, now $0.00295
PRICE_DATA = [
    ("00:00", 0.00242, "Open, building momentum"),
    ("00:15", 0.00248, "+2.5% move"),
    ("00:30", 0.00255, "+5.4% - BREAKOUT ENTRY"),
    ("00:45", 0.00261, "+7.8%"),
    ("01:00", 0.00268, "+10.7%, first target hit"),
    ("01:15", 0.00275, "+13.6% - SELL 50% HERE"),
    ("01:30", 0.00272, "+12.4%, consolidation"),
    ("01:45", 0.00278, "+14.9%, second push"),
    ("02:00", 0.00280, "+15.7%, peak?"),
    ("02:15", 0.00277, "+14.5%, first red candle"),
    ("02:30", 0.00274, "+13.2%, second red - FULL EXIT"),
    ("02:45", 0.00271, "+11.9%, -10.4% from peak - RE-ENTRY ZONE"),
    ("03:00", 0.00276, "+14.0%, bounce"),
    ("03:15", 0.00278, "+14.9%"),
    ("03:30", 0.00283, "+16.9%, close"),
]

class SmartSwingV21:
    def __init__(self):
        self.capital = 1.0  # SOL
        self.positions = []  # List of position dicts
        self.trades = []
        self.realized_pnl = 0
        
    def calculate_avg_entry(self):
        if not self.positions:
            return 0
        total_size = sum(p['size'] for p in self.positions)
        total_cost = sum(p['size'] * p['price'] for p in self.positions)
        return total_cost / total_size if total_size > 0 else 0
    
    def total_position_size(self):
        return sum(p['size'] for p in self.positions)
    
    def trade(self):
        print("="*70)
        print("SMART SWING v2.1 BACKTEST - Token: 67")
        print("="*70)
        print(f"{'Time':<8} {'Price':<10} {'Action':<50}")
        print("-"*70)
        
        in_trade = False
        trailing_stop = 0
        partial_1_done = False
        partial_2_done = False
        
        for i, (time, price, note) in enumerate(PRICE_DATA):
            action = ""
            
            if not in_trade:
                # Look for breakout entry (>5% from open)
                open_price = PRICE_DATA[0][1]
                price_change = (price - open_price) / open_price * 100
                
                if price_change >= 5.0 and i < 4:  # Entry within first hour
                    entry_size = 0.5 if price_change > 7 else 0.3  # Dynamic sizing
                    self.positions.append({'size': entry_size, 'price': price, 'time': time})
                    in_trade = True
                    trailing_stop = price * 0.88  # -12% trailing
                    action = f"ENTRY {entry_size} SOL @ ${price:.6f} (+{price_change:.1f}%)"
                    
            else:
                avg_entry = self.calculate_avg_entry()
                position_size = self.total_position_size()
                pnl_pct = (price - avg_entry) / avg_entry * 100
                
                # Partial exit at +20%
                if pnl_pct >= 20 and not partial_1_done:
                    sell_size = position_size * 0.5
                    pnl_usd = sell_size * (price - avg_entry)
                    self.realized_pnl += pnl_usd
                    action = f"SCALE 50% @ ${price:.6f} (+{pnl_pct:.1f}%) P&L: ${pnl_usd:.4f}"
                    partial_1_done = True
                    trailing_stop = price * 0.85  # Tighten to -15%
                
                # Second partial at +30%
                elif pnl_pct >= 30 and partial_1_done and not partial_2_done:
                    sell_size = position_size * 0.25
                    pnl_usd = sell_size * (price - avg_entry)
                    self.realized_pnl += pnl_usd
                    action = f"SCALE 25% @ ${price:.6f} (+{pnl_pct:.1f}%) P&L: ${pnl_usd:.4f}"
                    partial_2_done = True
                    trailing_stop = price * 0.80  # Widen to -20%
                
                # Check trailing stop
                elif price <= trailing_stop:
                    # Sell remaining position
                    remaining = position_size * (0.25 if partial_2_done else 0.5 if partial_1_done else 1.0)
                    pnl_usd = remaining * (price - avg_entry)
                    self.realized_pnl += pnl_usd
                    action = f"TRAILING STOP @ ${price:.6f} (avg ${avg_entry:.6f}) Final P&L: ${self.realized_pnl:.4f}"
                    
                    # Record trade
                    self.trades.append({
                        'entry_time': self.positions[0]['time'],
                        'entry_price': avg_entry,
                        'exit_time': time,
                        'exit_price': price,
                        'size': position_size,
                        'pnl_usd': self.realized_pnl,
                        'pnl_pct': pnl_pct
                    })
                    
                    in_trade = False
                    self.positions = []
                    partial_1_done = False
                    partial_2_done = False
                    
                else:
                    action = f"Holding | Avg: ${avg_entry:.6f} | P&L: {pnl_pct:+.1f}% | Trail: ${trailing_stop:.6f}"
                
                # Re-entry logic after exit (wait for -10% dip)
                if not in_trade and len(self.trades) > 0:
                    last_peak = max([p[1] for p in PRICE_DATA[:i]])
                    dip_pct = (last_peak - price) / last_peak * 100
                    if dip_pct >= 10 and dip_pct <= 12:
                        self.positions.append({'size': 0.25, 'price': price, 'time': time})
                        in_trade = True
                        trailing_stop = price * 0.88
                        action = f"RE-ENTRY 0.25 SOL @ ${price:.6f} (dip -{dip_pct:.1f}%)"
            
            if not action:
                action = note
                
            print(f"{time:<8} ${price:<9.6f} {action}")
        
        print("\n" + "="*70)
        print("BACKTEST RESULTS")
        print("="*70)
        print(f"\nToken: {TOKEN['name']} ({TOKEN['symbol']})")
        print(f"Market Cap: ${TOKEN['mcap']:,}")
        print(f"24h Change: {TOKEN['priceChange_h24']:.2f}%")
        print(f"\nStrategy: Smart Swing v2.1")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Total P&L (USD): ${self.realized_pnl:.4f}")
        print(f"Return on Capital: {self.realized_pnl / TOKEN['current_price']:.2f}%")
        
        if self.trades:
            avg_pnl = sum(t['pnl_pct'] for t in self.trades) / len(self.trades)
            print(f"Avg P&L per Trade: {avg_pnl:.2f}%")
            print(f"\nTrade Details:")
            for i, t in enumerate(self.trades, 1):
                print(f"  Trade {i}: {t['entry_time']} → {t['exit_time']} | ${t['pnl_usd']:.4f} ({t['pnl_pct']:+.1f}%)")

if __name__ == "__main__":
    strategy = SmartSwingV21()
    strategy.trade()
