#!/usr/bin/env python3
"""
Solana Meme Coin Paper Trader - Momentum Breakout Strategy
"""
import requests
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict

# Birdeye API Configuration
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BASE_URL = "https://public-api.birdeye.so"

HEADERS = {
    "X-API-KEY": BIRDEYE_API_KEY,
    "accept": "application/json"
}

# Trading Parameters
INITIAL_CAPITAL = 1.0  # SOL
POSITION_SIZE = 0.1    # SOL per trade (10 positions max)
ENTRY_THRESHOLD = 0.05  # +5% from 6h ago
VOLUME_SPIKE_THRESHOLD = 2.0  # 2x average volume
SCALE_OUT_PROFIT = 0.20  # +20%
TRAIL_STOP = 0.10  # -10% from peak
HARD_STOP = -0.07  # -7%
TIMEFRAME = "15m"

@dataclass
class Trade:
    token: str
    symbol: str
    entry_price: float
    entry_time: datetime
    position_size_sol: float
    tokens_bought: float
    peak_price: float = 0
    scaled_out: bool = False
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl_sol: float = 0
    pnl_pct: float = 0
    exit_reason: str = ""
    status: str = "OPEN"  # OPEN, CLOSED

@dataclass
class TradingStats:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl_sol: float = 0
    win_rate: float = 0
    capital: float = INITIAL_CAPITAL
    trades: List[Trade] = field(default_factory=list)
    open_positions: List[Trade] = field(default_factory=list)

class MemeCoinTrader:
    def __init__(self):
        self.stats = TradingStats()
        self.price_history = defaultdict(list)  # token -> list of (timestamp, price, volume)
        print(f"🚀 Meme Coin Paper Trader Initialized")
        print(f"💰 Initial Capital: {INITIAL_CAPITAL} SOL")
        print(f"📊 Position Size: {POSITION_SIZE} SOL per trade")
        print(f"🎯 Entry: +{ENTRY_THRESHOLD*100}% with volume spike")
        print(f"📈 Scale Out: +{SCALE_OUT_PROFIT*100}% (50% position)")
        print(f"⛔ Trail Stop: -{TRAIL_STOP*100}% from peak")
        print(f"🛑 Hard Stop: {HARD_STOP*100}%")
        print("=" * 60)

    def get_trending_tokens(self, limit: int = 30) -> List[Dict]:
        """Get trending Solana tokens from Birdeye"""
        try:
            url = f"{BASE_URL}/defi/token_trending"
            params = {
                "sort_by": "rank",
                "sort_type": "asc",
                "offset": 0,
                "limit": limit
            }
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    # Filter for Solana tokens only
                    tokens = [t for t in data["data"]["tokens"] if t.get("chainId") == "solana"]
                    return tokens[:20]  # Top 20 Solana tokens
            return []
        except Exception as e:
            print(f"❌ Error fetching trending tokens: {e}")
            return []

    def get_token_price_history(self, address: str, hours: int = 6) -> List[Dict]:
        """Get price history for a token"""
        try:
            url = f"{BASE_URL}/defi/ohlcv"
            end_time = int(time.time())
            start_time = end_time - (hours * 3600)
            
            params = {
                "address": address,
                "type": "15m",
                "time_from": start_time,
                "time_to": end_time
            }
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    return data["data"]["items"]
            return []
        except Exception as e:
            print(f"❌ Error fetching price history for {address[:8]}...: {e}")
            return []

    def get_token_price(self, address: str) -> Optional[float]:
        """Get current token price"""
        try:
            url = f"{BASE_URL}/defi/price"
            params = {"address": address}
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    return data["data"].get("value")
            return None
        except Exception as e:
            print(f"❌ Error fetching price: {e}")
            return None

    def check_breakout_signal(self, address: str, symbol: str) -> bool:
        """Check if token meets breakout entry criteria"""
        # Get 6 hours of price history
        history = self.get_token_price_history(address, hours=8)
        
        if len(history) < 24:  # Need at least 24 candles (6 hours of 15m candles)
            return False

        # Calculate 6h ago price
        candles_6h_ago = 24  # 6 hours = 24 candles of 15m
        price_6h_ago = history[-candles_6h_ago - 1]["close"]
        current_price = history[-1]["close"]
        current_volume = history[-1]["v"]

        # Check price momentum
        price_change = (current_price - price_6h_ago) / price_6h_ago

        # Calculate average volume (last 24 candles excluding current)
        avg_volume = sum(c["v"] for c in history[-25:-1]) / 24
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        # Entry condition: +5% price AND volume spike
        if price_change >= ENTRY_THRESHOLD and volume_ratio >= VOLUME_SPIKE_THRESHOLD:
            print(f"\n🎯 BREAKOUT SIGNAL for {symbol}")
            print(f"   Price change: +{price_change*100:.1f}%")
            print(f"   Volume spike: {volume_ratio:.1f}x")
            return True
        
        return False

    def enter_position(self, address: str, symbol: str) -> bool:
        """Enter a new trading position"""
        # Check if already in position for this token
        for pos in self.stats.open_positions:
            if pos.token == address:
                return False

        # Check if we have enough capital
        if self.stats.capital < POSITION_SIZE:
            print(f"⚠️  Not enough capital to enter {symbol}")
            return False

        # Get current price
        price = self.get_token_price(address)
        if not price or price <= 0:
            return False

        # Calculate tokens to buy
        tokens_bought = POSITION_SIZE / price

        # Create trade
        trade = Trade(
            token=address,
            symbol=symbol,
            entry_price=price,
            entry_time=datetime.now(),
            position_size_sol=POSITION_SIZE,
            tokens_bought=tokens_bought,
            peak_price=price
        )

        self.stats.open_positions.append(trade)
        self.stats.capital -= POSITION_SIZE

        print(f"\n🟢 ENTERED: {symbol}")
        print(f"   Price: {price:.6f} SOL")
        print(f"   Size: {POSITION_SIZE} SOL → {tokens_bought:.4f} tokens")
        print(f"   Remaining Capital: {self.stats.capital:.3f} SOL")
        print(f"   Open Positions: {len(self.stats.open_positions)}")

        return True

    def update_positions(self):
        """Update all open positions and check for exits"""
        for trade in self.stats.open_positions[:]:
            current_price = self.get_token_price(trade.token)
            if not current_price:
                continue

            # Update peak price
            if current_price > trade.peak_price:
                trade.peak_price = current_price

            pnl_pct = (current_price - trade.entry_price) / trade.entry_price

            # Check scale out condition (+20%)
            if not trade.scaled_out and pnl_pct >= SCALE_OUT_PROFIT:
                self._scale_out(trade, current_price)
                continue

            # Check hard stop (-7%)
            if pnl_pct <= HARD_STOP:
                self._close_position(trade, current_price, "HARD STOP")
                continue

            # Check trailing stop (-10% from peak) - only for remaining position
            peak_decline = (trade.peak_price - current_price) / trade.peak_price
            if trade.scaled_out and peak_decline >= TRAIL_STOP:
                self._close_position(trade, current_price, "TRAIL STOP")
                continue

    def _scale_out(self, trade: Trade, current_price: float):
        """Scale out 50% of profitable position"""
        trade.scaled_out = True
        pnl_pct = (current_price - trade.entry_price) / trade.entry_price
        pnl_sol = (POSITION_SIZE * 0.5) * pnl_pct

        print(f"\n📈 SCALED OUT 50%: {trade.symbol} (+{pnl_pct*100:.1f}%)")
        print(f"   Realized: +{pnl_sol:.4f} SOL")

    def _close_position(self, trade: Trade, current_price: float, reason: str):
        """Close a trading position"""
        pnl_pct = (current_price - trade.entry_price) / trade.entry_price

        # Calculate P&L
        if trade.scaled_out:
            # Already scaled out 50%, remaining 50% closes now
            pnl_sol = (POSITION_SIZE * 0.5) * pnl_pct
            returned_capital = (POSITION_SIZE * 0.5) * (1 + pnl_pct)
        else:
            # Full position closes
            pnl_sol = POSITION_SIZE * pnl_pct
            returned_capital = POSITION_SIZE * (1 + pnl_pct)

        trade.exit_price = current_price
        trade.exit_time = datetime.now()
        trade.pnl_sol = pnl_sol
        trade.pnl_pct = pnl_pct
        trade.exit_reason = reason
        trade.status = "CLOSED"

        # Update stats
        self.stats.total_trades += 1
        self.stats.total_pnl_sol += pnl_sol
        self.stats.capital += returned_capital

        if pnl_sol > 0:
            self.stats.winning_trades += 1
        else:
            self.stats.losing_trades += 1

        # Remove from open positions
        self.stats.open_positions.remove(trade)
        self.stats.trades.append(trade)

        win_rate = (self.stats.winning_trades / self.stats.total_trades * 100) if self.stats.total_trades > 0 else 0

        print(f"\n🔴 CLOSED: {trade.symbol} ({reason})")
        print(f"   P&L: {'+' if pnl_sol >= 0 else ''}{pnl_sol:.4f} SOL ({pnl_pct*100:+.1f}%)")
        print(f"   Total P&L: {'+' if self.stats.total_pnl_sol >= 0 else ''}{self.stats.total_pnl_sol:.4f} SOL")
        print(f"   Win Rate: {win_rate:.1f}% ({self.stats.winning_trades}/{self.stats.total_trades})")
        print(f"   Capital: {self.stats.capital:.3f} SOL")

    def scan_for_opportunities(self):
        """Scan for new trading opportunities"""
        print("\n🔍 Scanning for breakout opportunities...")
        tokens = self.get_trending_tokens()
        print(f"   Found {len(tokens)} trending tokens")

        opportunities = []
        for token in tokens:
            address = token.get("address")
            symbol = token.get("symbol", "Unknown")
            
            if not address:
                continue

            try:
                if self.check_breakout_signal(address, symbol):
                    opportunities.append((address, symbol))
            except Exception as e:
                continue

        return opportunities

    def run(self):
        """Main trading loop"""
        print("\n" + "=" * 60)
        print("📊 STARTING PAPER TRADING SESSION")
        print("=" * 60)

        iteration = 0
        while self.stats.total_trades < 10:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration} | Trades: {self.stats.total_trades}/10")
            print(f"💰 Capital: {self.stats.capital:.3f} SOL")
            print(f"{'='*60}")

            # Update existing positions
            if self.stats.open_positions:
                print(f"\n📊 Monitoring {len(self.stats.open_positions)} open position(s)...")
                self.update_positions()

            # Look for new opportunities
            if len(self.stats.open_positions) < 5:  # Max 5 concurrent positions
                opportunities = self.scan_for_opportunities()
                for address, symbol in opportunities:
                    if len(self.stats.open_positions) >= 5:
                        break
                    self.enter_position(address, symbol)

            print(f"\n⏳ Waiting for next scan... (10 seconds)")
            time.sleep(10)

            # Safety check - cap iterations
            if iteration >= 50:
                print("\n⚠️  Max iterations reached, forcing exit...")
                break

        # Close remaining positions
        print("\n" + "=" * 60)
        print("📊 CLOSING REMAINING POSITIONS")
        print("=" * 60)
        for trade in self.stats.open_positions[:]:
            current_price = self.get_token_price(trade.token)
            if current_price:
                self._close_position(trade, current_price, "SESSION END")
            time.sleep(1)

        self.print_final_report()

    def print_final_report(self):
        """Print final trading report"""
        print("\n" + "=" * 60)
        print("📊 FINAL TRADING REPORT")
        print("=" * 60)
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Total Trades: {self.stats.total_trades}")
        print(f"   Winning Trades: {self.stats.winning_trades}")
        print(f"   Losing Trades: {self.stats.losing_trades}")
        win_rate = (self.stats.winning_trades / self.stats.total_trades * 100) if self.stats.total_trades > 0 else 0
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"\n💰 P&L SUMMARY:")
        print(f"   Starting Capital: {INITIAL_CAPITAL} SOL")
        print(f"   Final Capital: {self.stats.capital:.4f} SOL")
        print(f"   Total P&L: {'+' if self.stats.total_pnl_sol >= 0 else ''}{self.stats.total_pnl_sol:.4f} SOL")
        print(f"   Return: {(self.stats.total_pnl_sol / INITIAL_CAPITAL) * 100:+.2f}%")

        print(f"\n📝 TRADE LOG:")
        print("-" * 60)
        for i, trade in enumerate(self.stats.trades, 1):
            emoji = "🟢" if trade.pnl_sol >= 0 else "🔴"
            print(f"{emoji} Trade #{i}: {trade.symbol}")
            print(f"   Entry: {trade.entry_price:.6f} → Exit: {trade.exit_price:.6f}")
            print(f"   P&L: {'+' if trade.pnl_sol >= 0 else ''}{trade.pnl_sol:.4f} SOL ({trade.pnl_pct*100:+.1f}%)")
            print(f"   Reason: {trade.exit_reason}")
            print()

        print("=" * 60)

if __name__ == "__main__":
    trader = MemeCoinTrader()
    trader.run()
