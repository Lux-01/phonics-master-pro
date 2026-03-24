#!/usr/bin/env python3
"""
Paper Trading - Mean Reversion (DIP) Strategy v2.1
Direct approach with extended history
"""

import json
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# Load API key
with open('/home/skux/.openclaw/agent/main/agent/auth.json') as f:
    auth = json.load(f)
    BIRDEYE_API_KEY = auth['birdeye']['api_key']

# Strategy Config
CONFIG = {
    'initial_sol': 1.0,
    'dip_threshold_min': 0.08,      # 8% minimum dip
    'dip_threshold_max': 0.15,      # 15% maximum dip
    'scale_out_pct': 0.20,          # Scale 50% at +20%
    'scale_out_portion': 0.50,      # Portion to scale out
    'trail_stop_pct': 0.10,         # Trail -10% from peak
    'hard_stop_pct': 0.07,          # Hard stop -7%
    'timeframe': '15m',
    'lookback_hours': 12,  # Extended for more data
}

@dataclass
class Trade:
    token: str
    symbol: str
    entry_price: float
    sol_used: float
    entry_time: str
    exit_price: float = 0.0
    exit_reason: str = ""
    pnl_pct: float = 0.0
    pnl_sol: float = 0.0


async def fetch_token_list(session) -> List[Dict]:
    """Fetch top Solana tokens by volume"""
    url = "https://public-api.birdeye.so/defi/tokenlist"
    headers = {'X-API-KEY': BIRDEYE_API_KEY}
    params = {
        'sort_by': 'v24hUSD',
        'sort_type': 'desc',
        'offset': 0,
        'limit': 50,
        'min_liquidity': 100000
    }
    
    try:
        async with session.get(url, headers=headers, params=params, timeout=15) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('success'):
                    return data.get('data', [])
    except Exception as e:
        print(f"Error fetching token list: {type(e).__name__}")
    return []


async def fetch_ohlcv(session, token: str, hours: int = 12) -> List[Dict]:
    """Fetch OHLCV data with extended history"""
    url = "https://public-api.birdeye.so/defi/ohlcv"
    
    now = int(time.time())
    # Extended lookback to ensure we have data
    from_ts = now - (hours * 3600) - 3600  # Extra hour buffer
    
    headers = {'X-API-KEY': BIRDEYE_API_KEY}
    params = {
        'address': token,
        'type': '15m',
        'time_from': from_ts,
        'time_to': now
    }
    
    try:
        async with session.get(url, headers=headers, params=params, timeout=30) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('success'):
                    items = data.get('data', {}).get('items', [])
                    return items
            else:
                print(f"  API status: {resp.status}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}")
    return []


def calc_6h_high(ohlcv: List[Dict], idx: int) -> float:
    """Get highest price in last 6h (24 candles)"""
    lookback = min(24, idx)
    if lookback < 1:
        return 0
    
    high = 0
    for i in range(idx - lookback, idx):
        high = max(high, ohlcv[i].get('h', 0))
    return high if high > 0 else 0


def is_ranging(ohlcv: List[Dict]) -> bool:
    """Check if market is choppy/ranging"""
    if len(ohlcv) < 12:
        return True
    
    closes = [c.get('c', 0) for c in ohlcv[-12:]]
    if not closes or min(closes) <= 0:
        return True
    
    first = sum(closes[:4]) / 4
    last = sum(closes[-4:]) / 4
    change = (last - first) / first if first > 0 else 0
    
    return abs(change) < 0.05


def check_entry(ohlcv: List[Dict], idx: int) -> Optional[Dict]:
    """Check for dip entry signal"""
    if idx < 1 or idx >= len(ohlcv):
        return None
    
    price = ohlcv[idx].get('c', 0)
    if price == 0:
        return None
    
    high_6h = calc_6h_high(ohlcv, idx)
    if high_6h == 0:
        return None
    
    # Dip from 6h high
    dip = (price - high_6h) / high_6h
    
    # Must be -8% to -15%
    if not (CONFIG['dip_threshold_min'] <= abs(dip) <= CONFIG['dip_threshold_max']):
        return None
    
    # Check ranging
    if not is_ranging(ohlcv):
        return None
    
    return {'dip_pct': dip, 'high_6h': high_6h, 'price': price}


def simulate_exit(entry_price: float, candles: List[Dict]) -> Dict:
    """Simulate exit based on trailing stops"""
    high_water = entry_price
    partial_sold = False
    
    for candle in candles:
        high = candle.get('h', entry_price)
        low = candle.get('l', entry_price)
        close = candle.get('c', entry_price)
        
        high_water = max(high_water, high)
        current_return = (close - entry_price) / entry_price
        
        # Scale out at +20% if not done
        if not partial_sold and current_return >= CONFIG['scale_out_pct']:
            partial_sold = True
        
        # Hard stop at -7%
        if current_return <= -CONFIG['hard_stop_pct']:
            exit_price = min(low, entry_price * (1 - CONFIG['hard_stop_pct']))
            return {
                'price': exit_price,
                'reason': 'HARD_STOP',
                'pnl': (exit_price - entry_price) / entry_price,
                'partial': partial_sold
            }
        
        # Trail stop at -10% from peak (only after partial exit)
        if partial_sold:
            trail_price = high_water * (1 - CONFIG['trail_stop_pct'])
            if low <= trail_price:
                return {
                    'price': trail_price,
                    'reason': 'TRAIL_STOP',
                    'pnl': (trail_price - entry_price) / entry_price,
                    'partial': True
                }
        
        # Original target hit for remaining position
        elif high >= entry_price * (1 + CONFIG['scale_out_pct']):
            return {
                'price': entry_price * (1 + CONFIG['scale_out_pct']),
                'reason': 'SCALE_OUT',
                'pnl': CONFIG['scale_out_pct'],
                'partial': False
            }
    
    # End of data
    final = candles[-1].get('c', entry_price) if candles else entry_price
    return {
        'price': final,
        'reason': 'END_OF_DATA',
        'pnl': (final - entry_price) / entry_price,
        'partial': partial_sold
    }


def calc_trade_pnl(entry: float, exit_result: Dict, sol_used: float) -> float:
    """Calculate P&L"""
    if exit_result['partial']:
        # 50% at +20%, rest at exit P&L
        partial = CONFIG['scale_out_portion'] * CONFIG['scale_out_pct']
        remaining = (1 - CONFIG['scale_out_portion']) * exit_result['pnl']
        return sol_used * (partial + remaining)
    return sol_used * exit_result['pnl']


async def run_paper_trade():
    print("🎯 PAPER TRADING: Mean Reversion (DIP) Strategy")
    print(f"   Capital: {CONFIG['initial_sol']} SOL")
    print(f"   Entry: -8% to -15% from 6h high")
    print(f"   Exit: 50% @ +20%, trail rest at -10% from peak")
    print(f"   Stop: Hard stop -7%")
    print("="*60)
    
    trades = []
    sol_balance = CONFIG['initial_sol']
    target_trades = 10
    
    async with aiohttp.ClientSession() as session:
        print("\n🔍 Fetching token list...")
        tokens = await fetch_token_list(session)
        
        if not tokens:
            print("❌ No tokens found")
            return trades, sol_balance
        
        print(f"✅ Found {len(tokens)} tokens")
        
        for token_info in tokens:
            if len(trades) >= target_trades:
                break
            
            # Handle different response structures
            token_info = token_info if isinstance(token_info, dict) else {}
            token = token_info.get('address') or token_info
            symbol = token_info.get('symbol', 'UNK') if isinstance(token_info, dict) else 'UNK'
            
            if not token or len(token) < 32:
                continue
            
            print(f"\n📊 Checking {symbol} ({token[:12]}...)")
            
            # Fetch OHLCV
            ohlcv = await fetch_ohlcv(session, token, hours=16)
            
            if len(ohlcv) < 35:
                print(f"   ⚠️ Insufficient data ({len(ohlcv)} candles)")
                continue
            
            # Look for entries (skip first 24 for 6h history, leave last 5 for exit)
            for i in range(24, len(ohlcv) - 5):
                signal = check_entry(ohlcv, i)
                
                if signal:
                    dip_pct = signal['dip_pct']
                    entry_price = signal['price']
                    
                    print(f"   ✅ ENTRY: -{abs(dip_pct)*100:.1f}% DIP")
                    print(f"      ${entry_price:.6f} (6h high: ${signal['high_6h']:.6f})")
                    
                    # Position sizing
                    position_sol = sol_balance * 0.9
                    
                    # Simulate exits
                    remaining = ohlcv[i+1:i+20]
                    if not remaining:
                        continue
                    
                    exit_res = simulate_exit(entry_price, remaining)
                    
                    # Calculate P&L
                    pnl_sol = calc_trade_pnl(entry_price, exit_res, position_sol)
                    sol_balance += pnl_sol
                    
                    trade = Trade(
                        token=token,
                        symbol=symbol,
                        entry_price=entry_price,
                        sol_used=position_sol,
                        entry_time=datetime.fromtimestamp(ohlcv[i].get('t', 0) or time.time()).strftime('%m/%d %H:%M'),
                        exit_price=exit_res['price'],
                        exit_reason=exit_res['reason'],
                        pnl_pct=exit_res['pnl'] * 100,
                        pnl_sol=pnl_sol
                    )
                    
                    trades.append(trade)
                    
                    emoji = "✅" if pnl_sol > 0 else "❌"
                    print(f"   {emoji} EXIT: {exit_res['reason']}")
                    print(f"      ${exit_res['price']:.6f} | {exit_res['pnl']*100:+.2f}% ({pnl_sol:+.4f} SOL)")
                    print(f"      Balance: {sol_balance:.4f} SOL")
                    
                    break
            
            await asyncio.sleep(0.3)
    
    # Summary
    print("\n" + "="*60)
    print("📊 PAPER TRADING SUMMARY - DIP STRATEGY")
    print("="*60)
    
    print(f"\nInitial: {CONFIG['initial_sol']:.4f} SOL | Final: {sol_balance:.4f} SOL")
    print(f"Return: {(sol_balance - CONFIG['initial_sol'])/CONFIG['initial_sol']*100:+.2f}% ({sol_balance - CONFIG['initial_sol']:+.4f} SOL)")
    
    total = len(trades)
    if total == 0:
        print("\n   No trades executed")
        return trades, sol_balance
    
    wins = sum(1 for t in trades if t.pnl_sol > 0)
    losses = total - wins
    win_rate = (wins / total * 100) if total > 0 else 0
    
    print(f"\n📈 Trade Stats:")
    print(f"   Trades: {total} | Wins: {wins} | Losses: {losses}")
    print(f"   Win Rate: {win_rate:.1f}%")
    
    total_pnl = sum(t.pnl_sol for t in trades)
    avg_pnl = total_pnl / total
    
    avg_win = sum(t.pnl_sol for t in trades if t.pnl_sol > 0) / wins if wins > 0 else 0
    avg_loss = sum(t.pnl_sol for t in trades if t.pnl_sol <= 0) / losses if losses > 0 else 0
    
    print(f"   Total P&L: {total_pnl:+.4f} SOL")
    print(f"   Avg Trade: {avg_pnl:+.4f} SOL")
    print(f"   Avg Win: {avg_win:+.4f} SOL | Avg Loss: {avg_loss:+.4f} SOL")
    
    if losses > 0 and avg_loss != 0:
        pf = abs(avg_win / avg_loss)
        print(f"   Profit Factor: {pf:.2f}")
    
    # Exit reasons
    print(f"\n📋 Exit Breakdown:")
    reasons = {}
    for t in trades:
        reasons[t.exit_reason] = reasons.get(t.exit_reason, 0) + 1
    for r, c in reasons.items():
        print(f"   {r}: {c}")
    
    # Trade log
    print(f"\n📜 Trade Log:")
    print(f"   {'#':<3} {'Time':<11} {'Symbol':<6} {'Entry':<11} {'Exit':<11} {'P&L':<9} {'Reason':<12}")
    print(f"   {'---':<3} {'-----------':<11} {'------':<6} {'-----------':<11} {'-----------':<11} {'---------':<9} {'------------':<12}")
    
    for i, t in enumerate(trades, 1):
        print(f"   {i:<3} {t.entry_time:<11} {t.symbol:<6} ${t.entry_price:<10.6f} ${t.exit_price:<10.6f} {t.pnl_sol:+.4f}  {t.exit_reason:<12}")
    
    return trades, sol_balance


if __name__ == "__main__":
    try:
        trades, final_balance = asyncio.run(run_paper_trade())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()