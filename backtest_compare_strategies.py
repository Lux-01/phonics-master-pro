#!/usr/bin/env python3
"""
Backtest Comparison: BREAKOUT vs DIP Strategy
Tests both strategies on same PUNCH token data
Starting capital: 1 SOL each
"""

import json
from datetime import datetime, timezone

# REAL OHLCV DATA from Birdeye API (Feb 22, 00:00-04:00 Sydney)
BIRDEYE_DATA = [
    {"o": 0.03139456444448735, "h": 0.03260353604210551, "l": 0.031157201644543633, "c": 0.031470010770394984, "v": 5532515.552388997, "unixTime": 1771678800},
    {"o": 0.031470010770394984, "h": 0.031730398386952734, "l": 0.02791064850543831, "c": 0.03023679312676641, "v": 12779230.001826972, "unixTime": 1771679700},
    {"o": 0.03023679312676641, "h": 0.030349392258753785, "l": 0.02403265737603014, "c": 0.02721155980883231, "v": 14687047.796434993, "unixTime": 1771680600},
    {"o": 0.02721155980883231, "h": 0.028080303621281087, "l": 0.026951642114362045, "c": 0.02749012933463889, "v": 3824893.3753040037, "unixTime": 1771681500},
    {"o": 0.02749012933463889, "h": 0.027775539605917724, "l": 0.026814486005028795, "c": 0.027444285757779845, "v": 3373976.9900509994, "unixTime": 1771682400},
    {"o": 0.027444285757779845, "h": 0.027444285757779845, "l": 0.027444285757779845, "c": 0.027444285757779845, "v": 0, "unixTime": 1771683300},
]

class BacktestStrategy:
    def __init__(self, name, mode, initial_capital=1.0):
        self.name = name
        self.mode = mode  # 'breakout' or 'dip'
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.position = None
        self.trades = []
        self.total_pnl = 0
        
    def calculate_ema(self, prices, period):
        if len(prices) < period:
            return sum(prices) / len(prices)
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def check_breakout_signal(self, candle, prev_candle, candles, i):
        """BREAKOUT: Buy when price up >= 5%"""
        if i < 5:
            return False, 0
        
        price_change = ((candle['c'] - prev_candle['c']) / prev_candle['c']) * 100
        
        # Calculate EMA
        closes = [c['c'] for c in candles[:i+1]]
        ema9 = self.calculate_ema(closes, 9)
        ema21 = self.calculate_ema(closes, 21)
        
        # Check breakout
        if price_change >= 5.0 and ema9 > ema21:
            # Score it
            score = 0
            if price_change >= 10: score += 3
            elif price_change >= 5: score += 2
            return True, score
        
        return False, 0
    
    def check_dip_signal(self, candle, candles, i):
        """DIP: Buy when price down >= 8% (but not more than 15%)"""
        if i < 1:
            return False, 0
        
        # Calculate 6h price change
        if i >= 4:
            price_6h_ago = candles[i-4]['c']
        else:
            price_6h_ago = candles[0]['c']
        
        price_change = ((candle['c'] - price_6h_ago) / price_6h_ago) * 100
        
        # Check dip (down 8-15%)
        if -15 <= price_change <= -8:
            # Score it
            dip_depth = abs(price_change)
            score = 0
            if 15 <= dip_depth <= 20: score += 4
            elif 10 <= dip_depth < 15: score += 3
            elif 8 <= dip_depth < 10: score += 2
            return True, score
        
        return False, 0
    
    def run(self, candles):
        """Run backtest simulation"""
        print(f"\n{'='*70}")
        print(f"{self.name} STRATEGY")
        print(f"{'='*70}")
        print(f"Mode: {self.mode.upper()}")
        print(f"Initial Capital: {self.initial_capital} SOL")
        print(f"{'='*70}\n")
        
        for i in range(1, len(candles)):
            current = candles[i]
            prev = candles[i-1]
            dt = datetime.fromtimestamp(current['unixTime'], tz=timezone.utc)
            
            # Manage position if have one
            if self.position:
                self.manage_position(current, prev, i)
                continue
            
            # Check for entry signal
            signal = False
            score = 0
            
            if self.mode == 'breakout':
                signal, score = self.check_breakout_signal(current, prev, candles, i)
            else:  # dip mode
                signal, score = self.check_dip_signal(current, candles, i)
            
            # Enter if signal and no position
            if signal and not self.position:
                entry_price = current['c']
                tokens = self.capital / entry_price
                
                self.position = {
                    'entry_price': entry_price,
                    'tokens': tokens,
                    'entry_time': dt,
                    'scaled': False,
                    'peak_price': entry_price,
                    'be_triggered': False,
                    'be_stop': 0
                }
                
                print(f"🟢 ENTRY | {dt.strftime('%H:%M')} UTC")
                print(f"    Price: ${entry_price:.6f}")
                print(f"    {self.mode.upper()} SIGNAL: Score {score}")
                print(f"    Bought: {tokens:.2f} tokens")
                print()
        
        # Close any open position at end
        if self.position:
            final_price = candles[-1]['c']
            pnl = ((final_price - self.position['entry_price']) / self.position['entry_price']) * 100
            sol_pnl = self.position['tokens'] * final_price - self.capital
            
            self.trades.append({
                'entry': self.position['entry_price'],
                'exit': final_price,
                'pnl_pct': pnl,
                'pnl_sol': sol_pnl,
                'exit_reason': 'end_of_session'
            })
            
            print(f"🔴 FORCE EXIT (End of Session)")
            print(f"    Exit: ${final_price:.6f}")
            print(f"    P&L: {pnl:.1f}% | {sol_pnl:.4f} SOL\n")
            
            self.total_pnl = sol_pnl
        
        return self.get_results()
    
    def manage_position(self, current, prev, i):
        """Manage open position with stops and scaling"""
        pos = self.position
        current_price = current['c']
        entry_price = pos['entry_price']
        dt = datetime.fromtimestamp(current['unixTime'], tz=timezone.utc)
        
        # Update peak
        if current_price > pos['peak_price']:
            pos['peak_price'] = current_price
        
        # Calculate P&L
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Scale at +20%
        if not pos['scaled'] and pnl_pct >= 20:
            pos['scaled'] = True
            print(f"💰 SCALE 50% | {dt.strftime('%H:%M')} UTC")
            print(f"    Price: ${current_price:.6f} (+{pnl_pct:.1f}%)")
            print(f"    Sold 50% for profit\n")
            return
        
        # Break-even stop (triggered at +10%)
        if not pos['be_triggered'] and not pos['scaled'] and pnl_pct >= 10:
            pos['be_triggered'] = True
            pos['be_stop'] = entry_price * 1.005  # +0.5%
            print(f"🛡️ BREAK-EVEN ACTIVATED at +{pnl_pct:.1f}%")
            print(f"    Stop moved to: ${pos['be_stop']:.6f} (+0.5%)\n")
        
        # Check trailing stop (-10% from peak)
        from_peak = ((current_price - pos['peak_price']) / pos['peak_price']) * 100
        if from_peak <= -10:
            sol_pnl = pos['tokens'] * (0.5 if pos['scaled'] else 1.0) * current_price - self.capital
            if pos['scaled']:
                scale_profit = pos['tokens'] * 0.5 * (pos['peak_price'] - entry_price)
                sol_pnl += scale_profit
            
            self.trades.append({
                'entry': entry_price,
                'exit': current_price,
                'pnl_pct': pnl_pct,
                'pnl_sol': sol_pnl,
                'exit_reason': 'trailing_stop'
            })
            
            print(f"🛑 TRAILING STOP | {dt.strftime('%H:%M')} UTC")
            print(f"    From Peak: {from_peak:.1f}%")
            print(f"    P&L: {pnl_pct:.1f}% | {sol_pnl:.4f} SOL\n")
            
            self.total_pnl = sol_pnl
            self.position = None
            return
        
        # Check hard stop
        stop_price = pos['be_stop'] if pos['be_triggered'] else entry_price * 0.93
        if current_price <= stop_price:
            sol_pnl = pos['tokens'] * (0.5 if pos['scaled'] else 1.0) * current_price - self.capital
            if pos['scaled']:
                scale_profit = pos['tokens'] * 0.5 * (pos['peak_price'] - entry_price)
                sol_pnl += scale_profit
            
            stop_type = 'BREAK-EVEN' if pos['be_triggered'] else 'HARD'
            
            self.trades.append({
                'entry': entry_price,
                'exit': current_price,
                'pnl_pct': pnl_pct,
                'pnl_sol': sol_pnl,
                'exit_reason': stop_type.lower()
            })
            
            print(f"🛑 {stop_type} STOP | {dt.strftime('%H:%M')} UTC")
            print(f"    P&L: {pnl_pct:.1f}% | {sol_pnl:.4f} SOL\n")
            
            self.total_pnl = sol_pnl
            self.position = None
    
    def get_results(self):
        """Get final results"""
        final_capital = self.initial_capital + self.total_pnl
        
        return {
            'strategy': self.name,
            'mode': self.mode,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_pnl_sol': self.total_pnl,
            'total_pnl_pct': (self.total_pnl / self.initial_capital) * 100,
            'trades': len(self.trades),
            'wins': sum(1 for t in self.trades if t['pnl_pct'] > 0),
            'losses': sum(1 for t in self.trades if t['pnl_pct'] < 0)
        }

def run_comparison():
    """Run both strategies and compare"""
    print("\n" + "="*70)
    print("STRATEGY COMPARISON BACKTEST")
    print("PUNCH Token - Feb 22, 00:00-04:00 Sydney")
    print("Starting Capital: 1.0 SOL each")
    print("="*70)
    
    # Run BREAKOUT strategy
    breakout = BacktestStrategy("BREAKOUT", "breakout", initial_capital=1.0)
    breakout_results = breakout.run(BIRDEYE_DATA)
    
    # Run DIP strategy
    dip = BacktestStrategy("DIP BUYING", "dip", initial_capital=1.0)
    dip_results = dip.run(BIRDEYE_DATA)
    
    # Compare results
    print("\n" + "="*70)
    print("FINAL COMPARISON")
    print("="*70)
    print(f"\n{'Strategy':<20} {'Final SOL':<12} {'P&L (SOL)':<12} {'P&L (%)':<12} {'Trades':<10}")
    print("-"*70)
    
    b = breakout_results
    d = dip_results
    
    print(f"{b['strategy']:<20} {b['final_capital']:<12.4f} {b['total_pnl_sol']:<12.4f} {b['total_pnl_pct']:<12.2f} {b['trades']:<10}")
    print(f"{d['strategy']:<20} {d['final_capital']:<12.4f} {d['total_pnl_sol']:<12.4f} {d['total_pnl_pct']:<12.2f} {d['trades']:<10}")
    
    # Determine winner
    print("\n" + "="*70)
    if breakout_results['total_pnl_sol'] > dip_results['total_pnl_sol']:
        diff = breakout_results['total_pnl_sol'] - dip_results['total_pnl_sol']
        print(f"🏆 WINNER: BREAKOUT Strategy (+{diff:.4f} SOL better)")
        print(f"   Made {breakout_results['total_pnl_sol']:.4f} SOL vs {dip_results['total_pnl_sol']:.4f} SOL")
    elif dip_results['total_pnl_sol'] > breakout_results['total_pnl_sol']:
        diff = dip_results['total_pnl_sol'] - breakout_results['total_pnl_sol']
        print(f"🏆 WINNER: DIP BUYING Strategy (+{diff:.4f} SOL better)")
        print(f"   Made {dip_results['total_pnl_sol']:.4f} SOL vs {breakout_results['total_pnl_sol']:.4f} SOL")
    else:
        print("🤝 TIE: Both strategies performed equally")
    
    # Buy & Hold baseline
    start = BIRDEYE_DATA[0]['o']
    end = BIRDEYE_DATA[-1]['c']
    buy_hold_pct = ((end - start) / start) * 100
    buy_hold_sol = buy_hold_pct / 100  # On 1 SOL
    
    print(f"\n📊 Buy & Hold: {buy_hold_sol:.4f} SOL ({buy_hold_pct:+.2f}%)")
    
    # Recommendations
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    if breakout_results['trades'] == 0 and dip_results['trades'] == 0:
        print("\n📉 Market was in severe downtrend (-12.58%)")
        print("   Breakout: No momentum signals, stayed out ✓")
        print("   Dip: Price crashed below -15% threshold, avoided dead coin ✓")
        print("\n✅ Both strategies correctly preserved capital during crash")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    run_comparison()
