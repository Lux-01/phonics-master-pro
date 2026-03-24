#!/usr/bin/env python3
"""
Solana Meme Coin Paper Trader - Fast Simulation
Uses historical data to simulate trades
"""
import requests
import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

# Birdeye API Configuration
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BASE_URL = "https://public-api.birdeye.so"
HEADERS = {"X-API-KEY": BIRDEYE_API_KEY, "accept": "application/json"}

# Trading Parameters
INITIAL_CAPITAL = 1.0
POSITION_SIZE = 0.1
ENTRY_THRESHOLD = 0.05  # 5%
VOLUME_SPIKE = 2.0
SCALE_OUT = 0.20  # 20%
TRAIL_STOP = 0.10  # -10% from peak
HARD_STOP = -0.07  # -7%
MIN_TRADES = 10

@dataclass
class Trade:
    token: str
    symbol: str
    entry_price: float
    entry_time: str
    position_size: float
    peak_price: float = 0
    scaled_out: bool = False
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    pnl_sol: float = 0
    pnl_pct: float = 0
    exit_reason: str = ""
    status: str = "OPEN"

@dataclass
class Stats:
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    total_pnl: float = 0
    capital: float = INITIAL_CAPITAL
    trades: List[Trade] = field(default_factory=list)
    open_positions: List[Trade] = field(default_factory=list)

class FastTrader:
    def __init__(self):
        self.stats = Stats()
        print("🚀 Solana Meme Coin Paper Trader - Fast Simulation")
        print("="*60)
        print(f"💰 Capital: {INITIAL_CAPITAL} SOL | Position: {POSITION_SIZE} SOL")
        print(f"🎯 Entry: +{ENTRY_THRESHOLD*100}% with {VOLUME_SPIKE}x volume")
        print(f"📈 Scale Out: +{SCALE_OUT*100}% | Trail: -{TRAIL_STOP*100}% | Hard: {HARD_STOP*100}%")
        print("="*60)

    def get_trending(self, limit=20):
        try:
            url = f"{BASE_URL}/defi/token_trending"
            params = {"sort_by": "rank", "sort_type": "asc", "offset": 0, "limit": limit}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and "data" in data:
                    return data["data"]["tokens"]
            return []
        except Exception as e:
            print(f"⚠️ API Error: {e}")
            return []

    def get_price_history(self, address, hours=8):
        try:
            url = f"{BASE_URL}/defi/ohlcv"
            end = int(time.time())
            start = end - (hours * 3600)
            params = {"address": address, "type": "15m", "time_from": start, "time_to": end}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and "data" in data:
                    return data["data"]["items"]
            return []
        except Exception as e:
            return []

    def get_current_price(self, address):
        try:
            url = f"{BASE_URL}/defi/price"
            resp = requests.get(url, headers=HEADERS, params={"address": address}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data["data"].get("value")
            return None
        except:
            return None

    def analyze_token(self, token):
        """Analyze a token for breakout trades"""
        address = token.get("address")
        symbol = token.get("symbol", "Unknown")
        name = token.get("name", "Unknown")
        
        # Skip tokens without proper data
        if not address or not symbol:
            return None

        history = self.get_price_history(address, hours=8)
        if len(history) < 32:  # Need at least ~8 hours of data
            return None

        trades_found = []
        
        # Scan through history looking for breakout entries
        for i in range(24, len(history) - 12):  # 6 hours ago window
            # Calculate price change from 6h ago
            price_6h = history[i - 24]["close"] if i >= 24 else history[0]["close"]
            current = history[i]["close"]
            volume = history[i]["v"]
            
            # Calculate average volume
            avg_vol = sum(h["v"] for h in history[max(0,i-25):i]) / 25
            vol_ratio = volume / avg_vol if avg_vol > 0 else 0
            
            change = (current - price_6h) / price_6h
            
            # Entry signal: +5% price + 2x volume
            if change >= ENTRY_THRESHOLD and vol_ratio >= VOLUME_SPIKE:
                entry_price = current
                entry_time = history[i]["unixTime"]
                peak = entry_price
                position_size = POSITION_SIZE
                
                # Simulate the trade forward
                scaled = False
                exited = False
                exit_price = 0
                exit_reason = ""
                exit_idx = i
                
                for j in range(i+1, min(i+48, len(history))):  # Forward simulation
                    price = history[j]["close"]
                    if price > peak:
                        peak = price
                    
                    pnl_pct = (price - entry_price) / entry_price
                    
                    # Scale out at +20%
                    if not scaled and pnl_pct >= SCALE_OUT:
                        scaled = True
                        # Take 50% profit, track remaining
                        realized_pnl = (position_size * 0.5) * pnl_pct
                        position_size *= 0.5  # Remaining position
                    
                    # Hard stop at -7%
                    if pnl_pct <= HARD_STOP:
                        exit_price = price
                        exit_reason = "HARD STOP"
                        exited = True
                        exit_idx = j
                        break
                    
                    # Trailing stop at -10% from peak (after scale out)
                    if scaled:
                        peak_decline = (peak - price) / peak
                        if peak_decline >= TRAIL_STOP:
                            exit_price = price
                            exit_reason = "TRAIL STOP"
                            exited = True
                            exit_idx = j
                            break
                    
                    # Time exit after 24 candles (6 hours)
                    if j >= i + 24:
                        exit_price = price
                        exit_reason = "TIME EXIT"
                        exited = True
                        exit_idx = j
                        break
                
                if exited:
                    final_pnl_pct = (exit_price - entry_price) / entry_price
                    final_pnl_sol = POSITION_SIZE * final_pnl_pct
                    
                    trade = Trade(
                        token=address,
                        symbol=symbol,
                        entry_price=entry_price,
                        entry_time=datetime.fromtimestamp(entry_time).strftime("%Y-%m-%d %H:%M"),
                        position_size=POSITION_SIZE,
                        peak_price=peak,
                        scaled_out=scaled,
                        exit_price=exit_price,
                        exit_time=datetime.fromtimestamp(history[exit_idx]["unixTime"]).strftime("%Y-%m-%d %H:%M"),
                        pnl_sol=final_pnl_sol,
                        pnl_pct=final_pnl_pct,
                        exit_reason=exit_reason,
                        status="CLOSED"
                    )
                    trades_found.append(trade)
        
        return {symbol: trades_found} if trades_found else None

    def run(self):
        print("\n🔍 Fetching trending tokens...")
        tokens = self.get_trending(limit=20)
        print(f"✅ Found {len(tokens)} Solana tokens")
        
        print("\n📊 Analyzing historical data for breakout opportunities...")
        
        all_trades = []
        for token in tokens[:15]:  # Analyze top 15
            symbol = token.get("symbol", "?")
            print(f"   Analyzing {symbol}...", end="\r")
            result = self.analyze_token(token)
            if result:
                for sym, trades in result.items():
                    all_trades.extend(trades)
                    print(f"   ✓ {sym}: Found {len(trades)} trades")
        
        print(f"\n✅ Total breakout opportunities found: {len(all_trades)}")
        
        # Take first 10 trades
        selected_trades = all_trades[:MIN_TRADES]
        
        print("\n" + "="*60)
        print("📋 EXECUTING 10 PAPER TRADES")
        print("="*60)
        
        for i, trade in enumerate(selected_trades, 1):
            self.stats.trades.append(trade)
            self.stats.total_trades += 1
            self.stats.total_pnl += trade.pnl_sol
            self.stats.capital += (POSITION_SIZE * (1 + trade.pnl_pct))
            
            if trade.pnl_sol >= 0:
                self.stats.wins += 1
                emoji = "🟢"
            else:
                self.stats.losses += 1
                emoji = "🔴"
            
            print(f"\n{emoji} TRADE #{i}: {trade.symbol}")
            print(f"   Entry: {trade.entry_price:.8f} ({trade.entry_time})")
            print(f"   Exit:  {trade.exit_price:.8f} ({trade.exit_time})")
            print(f"   Peak:  {trade.peak_price:.8f}")
            print(f"   Return: {trade.pnl_pct*100:+.1f}% | P&L: {trade.pnl_sol:+.4f} SOL")
            print(f"   Reason: {trade.exit_reason} {'(Scaled out 50%)' if trade.scaled_out else ''}")
        
        self.print_report()

    def print_report(self):
        print("\n" + "="*60)
        print("📊 FINAL PAPER TRADING REPORT - MOMENTUM BREAKOUT STRATEGY")
        print("="*60)
        
        win_rate = (self.stats.wins / self.stats.total_trades * 100) if self.stats.total_trades > 0 else 0
        
        print(f"\n📈 PERFORMANCE SUMMARY:")
        print(f"   Total Trades:     {self.stats.total_trades}")
        print(f"   Winning Trades:   {self.stats.wins}")
        print(f"   Losing Trades:    {self.stats.losses}")
        print(f"   Win Rate:         {win_rate:.1f}%")
        
        print(f"\n💰 PROFIT & LOSS:")
        print(f"   Starting Capital: {INITIAL_CAPITAL} SOL")
        print(f"   Final Capital:    {self.stats.capital:.4f} SOL")
        print(f"   Total P&L:        {self.stats.total_pnl:+.4f} SOL")
        print(f"   Return:           {(self.stats.total_pnl/INITIAL_CAPITAL)*100:+.2f}%")
        
        avg_win = sum(t.pnl_sol for t in self.stats.trades if t.pnl_sol > 0) / self.stats.wins if self.stats.wins > 0 else 0
        avg_loss = sum(t.pnl_sol for t in self.stats.trades if t.pnl_sol < 0) / self.stats.losses if self.stats.losses > 0 else 0
        
        print(f"\n📊 TRADE STATISTICS:")
        print(f"   Average Win:      +{avg_win:.4f} SOL")
        print(f"   Average Loss:     {avg_loss:.4f} SOL")
        print(f"   Profit Factor:    {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "   Profit Factor:    N/A")
        
        # Exit breakdown
        exits = {}
        for t in self.stats.trades:
            exits[t.exit_reason] = exits.get(t.exit_reason, 0) + 1
        
        print(f"\n🚪 EXIT BREAKDOWN:")
        for reason, count in sorted(exits.items(), key=lambda x: -x[1]):
            print(f"   {reason}: {count} trade(s)")
        
        print("\n" + "="*60)
        print("📝 STRATEGY ASSESSMENT:")
        
        if win_rate >= 50 and self.stats.total_pnl > 0:
            print("   ✅ Strategy shows positive expectancy")
        elif win_rate >= 40 and self.stats.total_pnl > 0:
            print("   ⚠️  Strategy profitable but low win rate")
        elif self.stats.total_pnl >= -0.1:
            print("   ⚠️  Strategy near breakeven - needs optimization")
        else:
            print("   ❌ Strategy underperforming - requires adjustment")
        
        print("="*60)

if __name__ == "__main__":
    trader = FastTrader()
    trader.run()
