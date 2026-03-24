#!/usr/bin/env python3
"""
Paper Trading - Mean Reversion (DIP) Strategy
Strategy: Buy tokens when they drop 8-15% from recent highs

Trading Parameters:
- Entry: Price down 8-15% from 6h high
- Exit: Scale 50% at +20%, trail remaining at -10% from peak
- Stop: Hard stop -7%
- Timeframe: 15m candles
- Markets: Trade during choppy conditions (sideways, not trending)

Capital: 1 SOL
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import deque

# Load API key
with open('/home/skux/.openclaw/agent/main/agent/auth.json') as f:
    auth = json.load(f)
    BIRDEYE_API_KEY = auth['birdeye']['api_key']

# Strategy Config
CONFIG = {
    'initial_sol': 1.0,
    'max_positions': 1,  # One at a time per SOL
    'dip_threshold_min': 0.08,      # 8% minimum dip
    'dip_threshold_max': 0.15,      # 15% maximum dip
    'scale_out_pct': 0.20,          # Scale 50% at +20%
    'scale_out_portion': 0.50,      # Portion to scale out
    'trail_stop_pct': 0.10,         # Trail -10% from peak
    'hard_stop_pct': 0.07,          # Hard stop -7%
    'timeframe': '15m',
    'lookback_hours': 6,             # 6h high
    'min_liquidity_usd': 100000,   # Min $100k liquidity
    'max_volume_spike': 5.0,       # Avoid pump/dumps
}

POPULAR_MEMES = [
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',  # BONK
    'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',  # WIF
    '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',  # POPCAT
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',  # RAY
    '5oV2yr2kGXw6w5d9gXkFpvD7qZq3sX7J4u6d8s9f0g1',  # Example - will be replaced
]

@dataclass
class Trade:
    token: str
    entry_price: float
    position_size_usd: float
    sol_used: float
    entry_time: datetime
    
    # Position tracking
    high_water_mark: float
    partial_exit_done: bool = False
    partial_exit_price: Optional[float] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    pnl_pct: Optional[float] = None
    pnl_sol: Optional[float] = None
    
    def get_peak_price_sold(self) -> float:
        if self.partial_exit_done:
            # Return weighted average of exits
            price_exit = self.partial_exit_price if self.partial_exit_price else self.exit_price
            if self.exit_price:
                return (self.partial_exit_price * 0.5 + self.exit_price * 0.5)
            return price_exit
        return self.exit_price or self.high_water_mark

@dataclass
class TradeResult:
    entry_time: datetime
    exit_time: datetime
    token: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    pnl_sol: float
    exit_reason: str
    partial_exit: bool
    duration_minutes: int

class PaperTrader:
    def __init__(self):
        self.sol_balance = CONFIG['initial_sol']
        self.active_position: Optional[Trade] = None
        self.trade_history: List[TradeResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.price_history: Dict[str, deque] = {}  # Token -> deque of prices
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def fetch_ohlcv(self, token: str, hours: int = 24) -> List[Dict]:
        """Fetch OHLCV data from Birdeye"""
        url = "https://public-api.birdeye.so/defi/ohlcv"
        
        # Get timeframe in seconds
        tf_map = {'15m': 900, '1H': 3600, '1D': 86400}
        tf_seconds = tf_map.get(CONFIG['timeframe'], 900)
        
        now = int(time.time())
        from_ts = now - (hours * 3600)
        
        headers = {'X-API-KEY': BIRDEYE_API_KEY}
        params = {
            'address': token,
            'type': CONFIG['timeframe'],
            'time_from': from_ts,
            'time_to': now
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success') and data.get('data', {}).get('items'):
                        return data['data']['items']
        except Exception as e:
            print(f"  ⚠️ Error fetching OHLCV: {e}")
        
        return []
    
    async def get_token_price(self, token: str) -> Optional[float]:
        """Get current token price"""
        url = "https://public-api.birdeye.so/defi/price"
        headers = {'X-API-KEY': BIRDEYE_API_KEY}
        params = {'address': token}
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success'):
                        return data['data'].get('value')
        except Exception as e:
            print(f"  ⚠️ Error fetching price: {e}")
        
        return None
    
    async def get_token_list(self, limit: int = 20) -> List[Dict]:
        """Get trending tokens with good liquidity"""
        url = "https://public-api.birdeye.so/defi/tokenlist"
        headers = {'X-API-KEY': BIRDEYE_API_KEY}
        params = {
            'sort_by': 'v24hChangePercent',
            'sort_type': 'desc',
            'offset': 0,
            'limit': limit,
            'min_liquidity': CONFIG['min_liquidity_usd']
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success') and data.get('data'):
                        tokens = []
                        for token in data['data']:
                            if token.get('address') and token.get('liquidity', 0) >= CONFIG['min_liquidity_usd']:
                                tokens.append({
                                    'address': token['address'],
                                    'symbol': token.get('symbol', 'UNKNOWN'),
                                    'name': token.get('name', 'Unknown'),
                                    'liquidity': token.get('liquidity', 0),
                                    'v24hChange': token.get('v24hChangePercent', 0),
                                    'price': token.get('price', 0)
                                })
                        return tokens
        except Exception as e:
            print(f"  ⚠️ Error fetching token list: {e}")
        
        return []
    
    def calculate_6h_high(self, ohlcv: List[Dict], current_idx: int) -> float:
        """Calculate 6h high from 15m candles (24 candles = 6 hours)"""
        lookback_candles = CONFIG['lookback_hours'] * 4  # 6h * 4 candles/hour
        start_idx = max(0, current_idx - lookback_candles)
        
        high = 0
        for i in range(start_idx, current_idx):
            if i < len(ohlcv):
                high = max(high, ohlcv[i].get('h', 0))
        
        return high
    
    def is_choppy_market(self, ohlcv: List[Dict], count: int = 12) -> bool:
        """Check if market is choppy/sideways (not strongly trending)"""
        if len(ohlcv) < count:
            return True
        
        # Calculate EMA
        prices = [c.get('c', 0) for c in ohlcv[-count:]]
        if len(prices) < count:
            return True
            
        # EMA9 vs EMA21
        ema9_sum = sum(prices[-9:])
        ema21_sum = sum(prices) * 9 / 21  # Simplified
        
        ema9 = ema9_sum / 9
        ema21 = ema21_sum / count * 21 / 9  # Normalize
        
        # ADX-like calculation (trend strength)
        gains = []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            gains.append(abs(diff))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        price_range = max(prices) - min(prices)
        
        # Choppy if price swings but no clear direction
        if price_range > 0:
            trend_ratio = avg_gain / price_range
            # Lower ratio = more choppy
            return trend_ratio < 0.4  # Arbitrary threshold for choppiness
        
        return True
    
    def check_entry_signal(self, ohlcv: List[Dict], current_idx: int) -> Optional[float]:
        """Check if current candle meets DIP entry criteria"""
        if current_idx < 1 or current_idx >= len(ohlcv):
            return None
            
        current = ohlcv[current_idx]
        prev = ohlcv[current_idx - 1]
        
        current_price = current.get('c', 0)
        high_6h = self.calculate_6h_high(ohlcv, current_idx)
        
        if high_6h == 0:
            return None
            
        # Calculate dip percentage
        dip_pct = (current_price - high_6h) / high_6h
        
        # Must be between -8% and -15% (negative)
        if CONFIG['dip_threshold_min'] > abs(dip_pct) or abs(dip_pct) > CONFIG['dip_threshold_max']:
            return None
        
        # Check choppy market condition
        if not self.is_choppy_market(ohlcv):
            return None
            
        return dip_pct
    
    def check_exit_signals(self, current_price: float) -> str:
        """Check exit conditions for active position"""
        if not self.active_position:
            return ""
            
        trade = self.active_position
        entry = trade.entry_price
        
        # Calculate P&L
        pnl_pct = (current_price - entry) / entry
        
        # Update high water mark
        if current_price > trade.high_water_mark:
            trade.high_water_mark = current_price
        
        # 1. Scale out at +20%
        if not trade.partial_exit_done and pnl_pct >= CONFIG['scale_out_pct']:
            return "SCALE_OUT"
        
        # 2. Hard stop at -7%
        if pnl_pct <= -CONFIG['hard_stop_pct']:
            return "HARD_STOP"
        
        # 3. Trail stop at -10% from peak
        peak = trade.high_water_mark
        trail_price = peak * (1 - CONFIG['trail_stop_pct'])
        
        if current_price <= trail_price and pnl_pct > 0:
            return "TRAIL_STOP"
            
        return ""
    
    def enter_position(self, token: str, price: float, sol_to_use: float):
        """Enter new position"""
        position_size = sol_to_use * price  # USD value at entry
        
        self.active_position = Trade(
            token=token,
            entry_price=price,
            position_size_usd=position_size,
            sol_used=sol_to_use,
            entry_time=datetime.now(),
            high_water_mark=price
        )
        
        self.sol_balance -= sol_to_use
        
        print(f"\n🟢 ENTER LONG: {token[:12]}...")
        print(f"   Entry: ${price:.6f}")
        print(f"   Size: {sol_to_use:.4f} SOL (${position_size:.2f})")
        print(f"   Remaining: {self.sol_balance:.4f} SOL")
    
    def exit_position(self, price: float, reason: str):
        """Exit active position"""
        if not self.active_position:
            return
            
        trade = self.active_position
        entry = trade.entry_price
        
        # Calculate P&L
        pnl_pct = (price - entry) / entry
        pnl_sol = trade.sol_used * pnl_pct
        
        trade.exit_price = price
        trade.exit_time = datetime.now()
        trade.exit_reason = reason
        trade.pnl_pct = pnl_pct
        trade.pnl_sol = pnl_sol
        
        # Update balance
        if reason == "SCALE_OUT":
            # Sell half, keep half open for trail
            partial_proceeds = trade.sol_used * CONFIG['scale_out_portion'] * (1 + pnl_pct)
            self.sol_balance += partial_proceeds
            trade.partial_exit_done = True
            trade.partial_exit_price = price
            
            print(f"\n📊 SCALE OUT (50%): {token[:12]}...")
            print(f"   Price: ${price:.6f} | P&L: {pnl_pct*100:+.2f}% ({pnl_sol*CONFIG['scale_out_portion']:+.4f} SOL)")
            print(f"   Proceeds: {partial_proceeds:.4f} SOL")
            
            # Keep position open for trailing
            self.active_position = trade
            return
        else:
            # Full exit
            if trade.partial_exit_done:
                # Already sold half at +20%, now sell remaining
                partial_pnl = CONFIG['scale_out_pct']  # +20%
                remaining_sol = trade.sol_used * (1 - CONFIG['scale_out_portion'])
                
                # Current P&L for remaining portion
                current_pnl_pct = (price - entry) / entry
                remaining_proceeds = remaining_sol * (1 + current_pnl_pct)
                
                self.sol_balance += remaining_proceeds
                
                # Calculate total P&L
                total_proceeds = (trade.sol_used * CONFIG['scale_out_portion'] * (1 + partial_pnl)) + remaining_proceeds
                total_pnl_sol = total_proceeds - trade.sol_used
                total_pnl_pct = total_pnl_sol / trade.sol_used
            else:
                # Full position exit
                proceeds = trade.sol_used * (1 + pnl_pct)
                self.sol_balance += proceeds
                total_pnl_sol = pnl_sol
                total_pnl_pct = pnl_pct
        
        duration = int((datetime.now() - trade.entry_time).total_seconds() / 60)
        
        # Record trade
        result = TradeResult(
            entry_time=trade.entry_time,
            exit_time=datetime.now(),
            token=trade.token,
            entry_price=trade.entry_price,
            exit_price=price,
            pnl_pct=total_pnl_pct,
            pnl_sol=total_pnl_sol,
            exit_reason=reason,
            partial_exit=trade.partial_exit_done,
            duration_minutes=duration
        )
        self.trade_history.append(result)
        
        # Clear active position
        self.active_position = None
        
        symbol = "✅" if total_pnl_sol > 0 else "❌"
        print(f"\n{symbol} EXIT: {reason} - {token[:12]}...")
        print(f"   Exit: ${price:.6f} | P&L: {total_pnl_pct*100:+.2f}% ({total_pnl_sol:+.4f} SOL)")
        print(f"   Duration: {duration}m")
        print(f"   Balance: {self.sol_balance:.4f} SOL")
    
    def print_summary(self):
        """Print trading summary"""
        print("\n" + "="*60)
        print("📊 PAPER TRADING SUMMARY - DIP STRATEGY")
        print("="*60)
        
        print(f"\nInitial Capital: {CONFIG['initial_sol']:.4f} SOL")
        print(f"Final Balance: {self.sol_balance:.4f} SOL")
        print(f"Total P&L: {(self.sol_balance - CONFIG['initial_sol'])/CONFIG['initial_sol']*100:+.2f}% ({self.sol_balance - CONFIG['initial_sol']:+.4f} SOL)")
        
        print(f"\n📈 Trade Statistics:")
        total_trades = len(self.trade_history)
        if total_trades == 0:
            print("   No trades executed")
            return
            
        wins = sum(1 for t in self.trade_history if t.pnl_sol > 0)
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        print(f"   Total Trades: {total_trades}")
        print(f"   Wins: {wins} | Losses: {losses}")
        print(f"   Win Rate: {win_rate:.1f}%")
        
        total_pnl = sum(t.pnl_sol for t in self.trade_history)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        avg_win = sum(t.pnl_sol for t in self.trade_history if t.pnl_sol > 0) / wins if wins > 0 else 0
        avg_loss = sum(t.pnl_sol for t in self.trade_history if t.pnl_sol <= 0) / losses if losses > 0 else 0
        
        print(f"   Total P&L: {total_pnl:+.4f} SOL")
        print(f"   Avg Trade: {avg_pnl:+.4f} SOL")
        print(f"   Avg Win: {avg_win:+.4f} SOL")
        print(f"   Avg Loss: {avg_loss:+.4f} SOL")
        
        if losses > 0:
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            print(f"   Profit Factor: {profit_factor:.2f}")
        
        print(f"\n📜 Exit Breakdown:")
        exits = {}
        for t in self.trade_history:
            exits[t.exit_reason] = exits.get(t.exit_reason, 0) + 1
        for reason, count in exits.items():
            print(f"   {reason}: {count}")
        
        print(f"\n📋 Trade Log:")
        print(f"   {'#':<3} {'Time':<12} {'Token':<18} {'Entry':<12} {'Exit':<12} {'P&L':<10} {'Reason':<12}")
        print(f"   {'-'*3} {'-'*12} {'-'*18} {'-'*12} {'-'*12} {'-'*10} {'-'*12}")
        
        for i, t in enumerate(self.trade_history, 1):
            time_str = t.exit_time.strftime("%H:%M")
            token_short = t.token[:15] + "..." if len(t.token) > 18 else t.token
            pnl_str = f"{t.pnl_sol:+.4f}SOL"
            entry_str = f"${t.entry_price:.6f}"
            exit_str = f"${t.exit_price:.6f}"
            print(f"   {i:<3} {time_str:<12} {token_short:<18} {entry_str:<12} {exit_str:<12} {pnl_str:<10} {t.exit_reason:<12}")


async def run_paper_trade():
    """Run paper trading simulation"""
    
    print("🎯 PAPER TRADING: Mean Reversion (DIP) Strategy")
    print(f"   Capital: {CONFIG['initial_sol']} SOL")
    print(f"   Entry: Price down 8-15% from 6h high")
    print(f"   Exit: Scale 50% at +20%, trail rest at -10% from peak")
    print(f"   Stop: Hard stop at -7%")
    print(f"   Timeframe: {CONFIG['timeframe']} candles")
    print("\nStarting simulation... Looking for dip opportunities...")
    print("="*60)
    
    async with PaperTrader() as trader:
        target_trades = 10
        max_iterations = 500  # Safety limit
        iteration = 0
        
        while len(trader.trade_history) < target_trades and iteration < max_iterations:
            iteration += 1
            
            print(f"\n📊 Scanning for dip opportunities... (Iteration {iteration}, Trades: {len(trader.trade_history)}/{target_trades})")
            
            # Get popular meme coins
            tokens = await trader.get_token_list(limit=30)
            
            if not tokens:
                print("  ⚠️ No tokens found, waiting...")
                await asyncio.sleep(2)
                continue
            
            # Filter for tokens with reasonable volatility
            candidates = [t for t in tokens if abs(t.get('v24hChange', 0)) < 50]
            
            print(f"  Found {len(candidates)} candidates with <50% daily change")
            
            # Check each token for dip signals
            for token_info in candidates[:15]:  # Check top 15
                token = token_info['address']
                symbol = token_info.get('symbol', 'UNK')
                
                # Skip if we have an active position
                if trader.active_position:
                    print(f"  ⏳ Active position open, checking exits...")
                    break
                
                print(f"  🔍 Checking {symbol} ({token[:12]}...)")
                
                # Get OHLCV data
                ohlcv = await trader.fetch_ohlcv(token, hours=8)
                
                if len(ohlcv) < 25:
                    print(f"     ⚠️ Insufficient data ({len(ohlcv)} candles)")
                    continue
                
                # Check the last 5 candles for entry signals
                for i in range(-5, 0):
                    current_idx = len(ohlcv) + i
                    if current_idx < 1:
                        continue
                        
                    dip_pct = trader.check_entry_signal(ohlcv, current_idx)
                    
                    if dip_pct:
                        # Calculate position size
                        position_sol = trader.sol_balance * 0.95  # 95% of available
                        
                        if position_sol < 0.1:
                            print(f"     ⚠️ Insufficient SOL balance")
                            break
                        
                        # Get current price
                        current_price = ohlcv[current_idx].get('c', 0)
                        if current_price == 0:
                            break
                        
                        high_6h = trader.calculate_6h_high(ohlcv, current_idx)
                        
                        print(f"     ✅ ENTRY SIGNAL: {abs(dip_pct)*100:.1f}% dip from 6h high")
                        print(f"        Current: ${current_price:.6f}")
                        print(f"        6h High: ${high_6h:.6f}")
                        print(f"        Dip: {abs(dip_pct)*100:.1f}%")
                        
                        trader.enter_position(token, current_price, position_sol)
                        
                        # Now simulate holding through the candle
                        await asyncio.sleep(0.1)  # Instant for simulation
                        
                        # Get next few candles to simulate price movement
                        next_candles = ohlcv[current_idx+1:current_idx+20] if current_idx < len(ohlcv) - 1 else []
                        
                        if not next_candles:
                            # Use current candle close
                            exit_price = current_price
                            trader.exit_position(exit_price, "END_OF_DATA")
                        else:
                            # Simulate through candles
                            for next_candle in next_candles:
                                price = next_candle.get('c', current_price)
                                
                                # Check each candle for exits
                                exit_reason = trader.check_exit_signals(price)
                                
                                if exit_reason:
                                    if exit_reason == "SCALE_OUT":
                                        # Partial exit, continue monitoring
                                        trader.exit_position(price, exit_reason)
                                        # Continue with remaining
                                        continue
                                    else:
                                        # Full exit
                                        trader.exit_position(price, exit_reason)
                                        break
                            else:
                                # No exit triggered, close at last available price
                                last_price = next_candles[-1].get('c', current_price)
                                trader.exit_position(last_price, "END_OF_DATA")
                        
                        break
                
                if trader.active_position:
                    break
                
                await asyncio.sleep(0.1)
            
            if trader.active_position:
                # Check exits for active position
                print(f"  Managing active position: {trader.active_position.token[:12]}...")
                current_price = await trader.get_token_price(trader.active_position.token)
                
                if current_price:
                    exit_reason = trader.check_exit_signals(current_price)
                    if exit_reason:
                        print(f"     Exit triggered: {exit_reason}")
                        trader.exit_position(current_price, exit_reason)
            
            # Brief pause between scans
            await asyncio.sleep(1)
        
        # Print final summary
        trader.print_summary()
        
        return trader


if __name__ == "__main__":
    try:
        result = asyncio.run(run_paper_trade())
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()