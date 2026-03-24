#!/usr/bin/env python3
"""
Multi-Token Strategy Comparison: BREAKOUT vs DIP
Tests both strategies on 4 popular meme tokens
Starting capital: 1.0 SOL per strategy per token
"""

from datetime import datetime, timezone
import json

# REAL DATA from Birdeye + estimated for comparison
TOKEN_DATA = {
    "PUNCH": {
        "name": "PUNCH (パンチ)",
        "data": [
            {"o": 0.0313945644, "h": 0.0326035360, "l": 0.0311572016, "c": 0.0314700108, "v": 5532515, "unixTime": 1771678800},
            {"o": 0.0314700108, "h": 0.0317303984, "l": 0.0279106485, "c": 0.0302367931, "v": 12779230, "unixTime": 1771679700},
            {"o": 0.0302367931, "h": 0.0303493923, "l": 0.0240326574, "c": 0.0272115598, "v": 14687047, "unixTime": 1771680600},
            {"o": 0.0272115598, "h": 0.0280803036, "l": 0.0269516421, "c": 0.0274901293, "v": 3824893, "unixTime": 1771681500},
            {"o": 0.0274901293, "h": 0.0277755396, "l": 0.0268144860, "c": 0.0274442858, "v": 3373977, "unixTime": 1771682400},
            {"o": 0.0274442858, "h": 0.0274442858, "l": 0.0274442858, "c": 0.0274442858, "v": 0, "unixTime": 1771683300},
        ]
    },
    "BONK": {
        "name": "BONK",
        "data": [
            {"o": 0.000006411, "h": 0.000006426, "l": 0.000006402, "c": 0.000006413, "v": 865180494, "unixTime": 1771678800},
            {"o": 0.000006413, "h": 0.000006422, "l": 0.000006402, "c": 0.000006414, "v": 3122731582, "unixTime": 1771679700},
            {"o": 0.000006414, "h": 0.000006427, "l": 0.000006401, "c": 0.000006412, "v": 1607224565, "unixTime": 1771680600},
            {"o": 0.000006412, "h": 0.000006453, "l": 0.000006406, "c": 0.000006450, "v": 3394335526, "unixTime": 1771681500},
            {"o": 0.000006450, "h": 0.000006450, "l": 0.000006386, "c": 0.000006429, "v": 1975965193, "unixTime": 1771682400},
            {"o": 0.000006429, "h": 0.000006488, "l": 0.000006416, "c": 0.000006447, "v": 4922217948, "unixTime": 1771683300},
        ]
    },
    "WIF": {
        "name": "dogwifhat",
        "data": [
            {"o": 0.85, "h": 0.87, "l": 0.84, "c": 0.86, "v": 2500000, "unixTime": 1771678800},
            {"o": 0.86, "h": 0.92, "l": 0.85, "c": 0.91, "v": 4500000, "unixTime": 1771679700},
            {"o": 0.91, "h": 0.94, "l": 0.89, "c": 0.93, "v": 5100000, "unixTime": 1771680600},
            {"o": 0.93, "h": 0.95, "l": 0.91, "c": 0.94, "v": 4300000, "unixTime": 1771681500},
            {"o": 0.94, "h": 0.96, "l": 0.92, "c": 0.95, "v": 3800000, "unixTime": 1771682400},
            {"o": 0.95, "h": 0.97, "l": 0.93, "c": 0.96, "v": 4200000, "unixTime": 1771683300},
        ]
    },
    "POPCAT": {
        "name": "POPCAT",
        "data": [
            {"o": 0.52, "h": 0.53, "l": 0.51, "c": 0.52, "v": 1800000, "unixTime": 1771678800},
            {"o": 0.52, "h": 0.52, "l": 0.49, "c": 0.50, "v": 2200000, "unixTime": 1771679700},
            {"o": 0.50, "h": 0.51, "l": 0.48, "c": 0.49, "v": 1900000, "unixTime": 1771680600},
            {"o": 0.49, "h": 0.50, "l": 0.48, "c": 0.485, "v": 2100000, "unixTime": 1771681500},
            {"o": 0.485, "h": 0.495, "l": 0.475, "c": 0.48, "v": 2300000, "unixTime": 1771682400},
            {"o": 0.48, "h": 0.485, "l": 0.47, "c": 0.475, "v": 2000000, "unixTime": 1771683300},
        ]
    },
}

class StrategyBacktest:
    def __init__(self, token_name, token_data, initial_capital=1.0):
        self.token_name = token_name
        self.data = token_data
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.position = None
        self.trades = 0
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0
        
    def calculate_ema(self, prices, period):
        if len(prices) < period:
            return sum(prices) / len(prices)
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def run_breakout(self):
        """BREAKOUT: Buy when price up >= 5%"""
        candles = self.data
        for i in range(5, len(candles)):
            current = candles[i]
            prev = candles[i-1]
            
            if self.position:
                self.manage_position(current)
                continue
            
            price_change = ((current['c'] - prev['c']) / prev['c']) * 100
            closes = [c['c'] for c in candles[:i+1]]
            ema9 = self.calculate_ema(closes, 9)
            ema21 = self.calculate_ema(closes, 21)
            
            if price_change >= 5.0 and ema9 > ema21:
                # Enter
                self.position = {
                    'entry': current['c'],
                    'tokens': self.capital / current['c'],
                    'peak': current['c'],
                    'be_set': False
                }
        
        if self.position:
            self.exit_position(candles[-1]['c'], 'end_of_session')
        
        return self.get_results('BREAKOUT')
    
    def run_dip(self):
        """DIP: Buy when price down 8-15%"""
        candles = self.data
        for i in range(4, len(candles)):
            current = candles[i]
            
            if self.position:
                self.manage_position(current)
                continue
            
            # Calculate 6h change
            price_6h_ago = candles[i-4]['c']
            change = ((current['c'] - price_6h_ago) / price_6h_ago) * 100
            
            if -15 <= change <= -8:
                # Enter
                self.position = {
                    'entry': current['c'],
                    'tokens': self.capital / current['c'],
                    'peak': current['c'],
                    'be_set': False
                }
        
        if self.position:
            self.exit_position(candles[-1]['c'], 'end_of_session')
        
        return self.get_results('DIP')
    
    def manage_position(self, current):
        """Manage open position"""
        pos = self.position
        price = current['c']
        entry = pos['entry']
        
        # Update peak
        if price > pos['peak']:
            pos['peak'] = price
        
        pnl = ((price - entry) / entry) * 100
        
        # Scale at +20%
        if pnl >= 20 and not getattr(pos, 'scaled', False):
            pos['scaled'] = True
            return
        
        # Break-even stop at +10%
        if pnl >= 10 and not pos['be_set']:
            pos['be_set'] = True
        
        # Trailing stop -10% from peak
        from_peak = ((price - pos['peak']) / pos['peak']) * 100
        if from_peak <= -10:
            self.exit_position(price, 'trailing_stop')
            return
        
        # Hard stop
        stop = entry * 1.005 if pos['be_set'] else entry * 0.93
        if price <= stop:
            self.exit_position(price, 'be_stop' if pos['be_set'] else 'hard_stop')
    
    def exit_position(self, price, reason):
        """Close position"""
        pos = self.position
        entry = pos['entry']
        pnl = ((price - entry) / entry) * 100
        sol_pnl = (price - entry) * pos['tokens']
        
        self.trades += 1
        if pnl > 0:
            self.wins += 1
        else:
            self.losses += 1
        self.total_pnl += sol_pnl
        
        self.position = None
    
    def get_results(self, mode):
        """Get results"""
        final_capital = self.initial_capital + self.total_pnl
        return {
            'token': self.token_name,
            'mode': mode,
            'initial': self.initial_capital,
            'final': final_capital,
            'pnl_sol': self.total_pnl,
            'pnl_pct': (self.total_pnl / self.initial_capital) * 100,
            'trades': self.trades,
            'wins': self.wins,
            'losses': self.losses
        }

def run_comparison():
    print("\n" + "="*80)
    print("MULTI-TOKEN STRATEGY COMPARISON")
    print("Starting Capital: 1.0 SOL per strategy per token")
    print("="*80)
    
    total_breakout_pnl = 0
    total_dip_pnl = 0
    total_buyhold_pnl = 0
    
    results_table = []
    
    for token_key, token_info in TOKEN_DATA.items():
        print(f"\n{'='*80}")
        print(f"TOKEN: {token_info['name']}")
        print(f"{'='*80}")
        
        # Calculate buy & hold
        start_price = token_info['data'][0]['o']
        end_price = token_info['data'][-1]['c']
        buyhold_change = ((end_price - start_price) / start_price) * 100
        buyhold_pnl = buyhold_change / 100  # On 1 SOL
        
        # Run Breakout
        breakout_bt = StrategyBacktest(token_key, token_info['data'])
        breakout_result = breakout_bt.run_breakout()
        
        # Run Dip
        dip_bt = StrategyBacktest(token_key, token_info['data'])
        dip_result = dip_bt.run_dip()
        
        # Track totals
        total_breakout_pnl += breakout_result['pnl_sol']
        total_dip_pnl += dip_result['pnl_sol']
        total_buyhold_pnl += buyhold_pnl
        
        results_table.append({
            'token': token_key,
            'breakout': breakout_result,
            'dip': dip_result,
            'buyhold': buyhold_pnl
        })
        
        # Print results
        print(f"\nBreakout: {breakout_result['trades']} trades | P&L: {breakout_result['pnl_sol']:+.4f} SOL")
        print(f"Dip:      {dip_result['trades']} trades | P&L: {dip_result['pnl_sol']:+.4f} SOL")
        print(f"Buy&Hold: 1 trade | P&L: {buyhold_pnl:+.4f} SOL ({buyhold_change:+.2f}%)")
    
    # Summary table
    print("\n" + "="*80)
    print("AGGREGATE RESULTS (4 Tokens)")
    print("="*80)
    print(f"\n{'Token':<15} {'Breakout':<12} {'Dip':<12} {'Buy&Hold':<12} {'Best':<10}")
    print("-"*80)
    
    for r in results_table:
        b_pnl = r['breakout']['pnl_sol']
        d_pnl = r['dip']['pnl_sol']
        h_pnl = r['buyhold']
        
        if b_pnl > d_pnl and b_pnl > h_pnl:
            best = '🚀 Breakout'
        elif d_pnl > b_pnl and d_pnl > h_pnl:
            best = '📉 Dip'
        elif h_pnl > b_pnl and h_pnl > d_pnl:
            best = '👐 Hold'
        else:
            best = 'Tie'
        
        print(f"{r['token']:<15} {b_pnl:+.4f}      {d_pnl:+.4f}      {h_pnl:+.4f}      {best:<10}")
    
    print("-"*80)
    print(f"{'TOTAL':<15} {total_breakout_pnl:+.4f}      {total_dip_pnl:+.4f}      {total_buyhold_pnl:+.4f}")
    print("="*80)
    
    # Determine overall winner
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if total_breakout_pnl > total_dip_pnl:
        winner = "BREAKOUT"
        diff = total_breakout_pnl - total_dip_pnl
    else:
        winner = "DIP"
        diff = total_dip_pnl - total_breakout_pnl
    
    print(f"\n🏆 OVERALL WINNER: {winner} Strategy")
    print(f"   Outperformed by: +{diff:.4f} SOL")
    print(f"\n   Breakout Total: {total_breakout_pnl:+.4f} SOL")
    print(f"   Dip Total:      {total_dip_pnl:+.4f} SOL")
    print(f"   Buy & Hold:     {total_buyhold_pnl:+.4f} SOL")
    
    if total_buyhold_pnl < total_breakout_pnl and total_buyhold_pnl < total_dip_pnl:
        print(f"\n✅ Both strategies beat buy & hold!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    run_comparison()
