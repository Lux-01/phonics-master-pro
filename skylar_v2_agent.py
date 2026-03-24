#!/usr/bin/env python3
"""
SKYLAR V2 - Trend Following Trading Agent with Survivor Filter
Created: 2026-02-21
Timeframe: 00:00 - 02:59 Sydney (3 hours)"

import json
import random
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# TOKENS - 1 Month+ Survivors (already aged 30+ days)
TOKENS = {
    'WIF': {
        'address': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
        'birth': 'Dec 2023',
        'base_price': 0.50,  # Simulated base
        'volatility': 0.15  # 15% volatility
    },
    'BONK': {
        'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', 
        'birth': 'Dec 2022',
        'base_price': 0.000012,
        'volatility': 0.12
    },
    'POPCAT': {
        'address': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',
        'birth': 'Mar 2024', 
        'base_price': 0.35,
        'volatility': 0.18
    },
    'MEW': {
        'address': 'MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5',
        'birth': 'Mar 2024',
        'base_price': 0.0025,
        'volatility': 0.20
    },
    'BOME': {
        'address': 'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82',
        'birth': 'Mar 2024', 
        'base_price': 0.004,
        'volatility': 0.16
    }
}

@dataclass
class Trade:
    entry_time: datetime
    exit_time: Optional[datetime] = None
    symbol: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    position_size: float = 0.0  # SOL invested
    peak_price: float = 0.0
    exit_reason: str = ""
    pnl_sol: float = 0.0
    pnl_pct: float = 0.0
    hold_minutes: float = 0.0

@dataclass
class Position:
    symbol: str
    entry_price: float
    entry_time: datetime
    position_size: float
    peak_price: float = 0.0
    highest_price: float = 0.0
    trailing_stop: float = 0.0

class SkylarV2:
    """
    SKYLAR V2 Trading Agent
    Personality: Adaptive, trend-following, rides strong momentum
    Risk Appetite: MODERATE
    """
    
    # Strategy Parameters
    RSI_PERIOD = 14
    EMA_PERIOD = 20
    LOOKBACK_PERIOD = 20
    
    # Entry Conditions
    VOLUME_MULT_THRESHOLD = 2.5
    RSI_MIN = 50
    RSI_MAX = 70
    
    # Exit Conditions
    TRAILING_STOP_PCT = -0.06  # -6%
    PROFIT_TARGET_PCT = 0.20   # +20%
    RSI_OVERBOUGHT = 75
    MAX_HOLD_MINUTES = 25
    
    # Position Sizing
    POSITION_SIZE_SOL = 0.33
    MAX_CONCURRENT = 3
    
    def __init__(self, initial_capital: float = 1.0):
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Trade] = []
        self.price_history: Dict[str, List[float]] = {k: [] for k in TOKENS}
        self.volume_history: Dict[str, List[float]] = {k: [] for k in TOKENS}
        self.rsi_history: Dict[str, List[float]] = {k: [] for k in TOKENS}
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI for price data"""
        if len(prices) < period + 1:
            return 50.0  # neutral
        
        deltas = np.diff(prices)
        gains = deltas[deltas > 0]
        losses = -deltas[deltas < 0]
        
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0.0001
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_ema(self, prices: List[float], period: int = 20) -> float:
        """Calculate EMA for trend filter"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def is_above_ema(self, symbol: str) -> bool:
        """Check if current price is above EMA20"""
        prices = self.price_history[symbol]
        if len(prices) < self.EMA_PERIOD:
            return False
        ema = self.calculate_ema(prices)
        return prices[-1] > ema
    
    def is_breaking_above_high(self, symbol: str) -> bool:
        """Check if price breaks above 20-period high"""
        prices = self.price_history[symbol]
        if len(prices) < self.LOOKBACK_PERIOD + 1:
            return False
        
        current_price = prices[-1]
        prev_period_high = max(prices[-self.LOOKBACK_PERIOD-1:-1])
        
        return current_price > prev_period_high
    
    def volume_spike(self, symbol: str) -> bool:
        """Check if volume is >2.5x average"""
        volumes = self.volume_history[symbol]
        if len(volumes) < self.LOOKBACK_PERIOD:
            return False
        
        current_vol = volumes[-1]
        avg_vol = np.mean(volumes[-self.LOOKBACK_PERIOD:])
        
        if avg_vol == 0:
            return False
        
        return (current_vol / avg_vol) >= self.VOLUME_MULT_THRESHOLD
    
    def get_entry_rsi(self, symbol: str) -> float:
        """Get RSI for entry signal (RSI 50-70 = healthy momentum)"""
        return self.calculate_rsi(self.price_history[symbol])
    
    def check_entry_signal(self, symbol: str, current_time: datetime) -> bool:
        """
        Entry: Price breaks above 20-period high + volume >2.5x + RSI(14) 50-70 + above EMA20
        """
        prices = self.price_history[symbol]
        if len(prices) < self.LOOKBACK_PERIOD + 1:
            return False
        
        # Can't enter if at max positions
        if len(self.positions) >= self.MAX_CONCURRENT:
            return False
        
        # Check already in position
        if symbol in self.positions:
            return False
        
        # Condition 1: Breaking above 20-period high
        breakout = self.is_breaking_above_high(symbol)
        if not breakout:
            return False
        
        # Condition 2: Volume spike >2.5x
        vol_spike = self.volume_spike(symbol)
        if not vol_spike:
            return False
        
        # Condition 3: RSI between 50-70 (healthy momentum zone)
        rsi = self.get_entry_rsi(symbol)
        if not (self.RSI_MIN <= rsi <= self.RSI_MAX):
            return False
        
        # Condition 4: Price above EMA20
        if not self.is_above_ema(symbol):
            return False
        
        return True
    
    def calculate_exit(self, symbol: str, current_price: float, current_time: datetime) -> Optional[str]:
        """
        Exit Conditions:
        - Trailing stop at -6% from peak
        - +20% profit target
        - RSI >75 (overbought)
        - Max hold 25 minutes
        """
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        
        # Update peak price
        if current_price > pos.peak_price:
            pos.peak_price = current_price
        
        # Calculate time held
        time_held = (current_time - pos.entry_time).total_seconds() / 60
        
        # Check max hold time
        if time_held >= self.MAX_HOLD_MINUTES:
            return "TIME_STOP"
        
        # Check trailing stop (-6% from peak)
        if pos.peak_price > 0:
            drop_from_peak = (current_price - pos.peak_price) / pos.peak_price
            if drop_from_peak <= self.TRAILING_STOP_PCT:
                return "TRAILING_STOP"
        
        # Check profit target (+20%)
        profit_pct = (current_price - pos.entry_price) / pos.entry_price
        if profit_pct >= self.PROFIT_TARGET_PCT:
            return "PROFIT_TARGET"
        
        # Check RSI overbought
        rsi = self.calculate_rsi(self.price_history[symbol])
        if rsi > self.RSI_OVERBOUGHT:
            return "RSI_OVERBOUGHT"
        
        return None
    
    def enter_position(self, symbol: str, price: float, time: datetime):
        """Enter a new position"""
        position = Position(
            symbol=symbol,
            entry_price=price,
            entry_time=time,
            position_size=self.POSITION_SIZE_SOL,
            peak_price=price,
            highest_price=price
        )
        self.positions[symbol] = position
        self.available_capital -= self.POSITION_SIZE_SOL
        
        print(f"[ENTRY] {symbol} @ ${price:.8f} | Size: {self.POSITION_SIZE_SOL} SOL | Time: {time.strftime('%H:%M')}")
    
    def exit_position(self, symbol: str, exit_price: float, exit_time: datetime, reason: str):
        """Exit a position and record trade"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        time_held = (exit_time - pos.entry_time).total_seconds() / 60
        pnl_pct = (exit_price - pos.entry_price) / pos.entry_price
        pnl_sol = pos.position_size * pnl_pct
        
        trade = Trade(
            entry_time=pos.entry_time,
            exit_time=exit_time,
            symbol=symbol,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            position_size=pos.position_size,
            peak_price=pos.peak_price,
            exit_reason=reason,
            pnl_sol=pnl_sol,
            pnl_pct=pnl_pct,
            hold_minutes=time_held
        )
        
        self.trade_history.append(trade)
        self.available_capital += pos.position_size + pnl_sol
        del self.positions[symbol]
        
        outcome = "✅ WIN" if pnl_sol > 0 else "❌ LOSS"
        print(f"[EXIT] {symbol} @ ${exit_price:.8f} | P&L: {pnl_sol:+.4f} SOL ({pnl_pct*100:+.2f}%) | Reason: {reason} | Hold: {time_held:.1f}min | {outcome}")
    
    def generate_market_data(self, start_time: datetime, hours: int = 3) -> Dict:
        """Generate realistic price/volume data for backtest"""
        data = {k: [] for k in TOKENS}
        
        # Generate 1-minute candles for specified hours
        for minute in range(hours * 60):
            timestamp = start_time.timestamp() + (minute * 60)
            time = datetime.fromtimestamp(timestamp, timezone.utc)
            
            for symbol, meta in TOKENS.items():
                # Base price with random walk
                base = meta['base_price']
                vol = meta['volatility']
                
                # Simulate trend moves and reversals
                trend_bias = np.sin(minute / 60) * 0.05  # Hourly cycles
                noise = np.random.normal(0, vol * 0.01)
                momentum = random.choice([-0.02, -0.01, 0, 0.01, 0.02, 0.05, 0.08]) if random.random() < 0.1 else 0
                
                if len(data[symbol]) == 0:
                    price = base * (1 + noise)
                else:
                    last_price = data[symbol][-1]['price']
                    change = trend_bias + noise + momentum
                    price = last_price * (1 + change)
                
                # Volume with spikes during moves
                base_vol = random.uniform(100000, 500000)
                if abs(change) > 0.03:  # High volume on big moves
                    vol_multiplier = random.uniform(3.0, 8.0)
                else:
                    vol_multiplier = random.uniform(0.8, 1.5)
                    
                volume = base_vol * vol_multiplier
                
                data[symbol].append({
                    'timestamp': timestamp,
                    'time': time,
                    'price': price,
                    'volume': volume
                })
        
        return data
    
    def run_backtest(self, start_time: datetime, hours: int = 3) -> Dict:
        """Run 3-hour backtest simulation"""
        print("="*70)
        print("SKYLAR V2 - Trend Following with Survivor Filter")
        print(f"Backtest: {start_time.strftime('%Y-%m-%d %H:%M')} to {(start_time.timestamp() + hours*3600)} UTC")
        print(f"Capital: {self.initial_capital} SOL | Max Positions: {self.MAX_CONCURRENT}")
        print("="*70)
        print()
        
        # Generate market data
        market_data = self.generate_market_data(start_time, hours)
        
        # Run simulation minute by minute
        for minute_idx in range(hours * 60):
            for symbol in TOKENS:
                candle = market_data[symbol][minute_idx]
                price = candle['price']
                volume = candle['volume']
                current_time = candle['time']
                
                # Update history
                self.price_history[symbol].append(price)
                self.volume_history[symbol].append(volume)
                
                # Check exits first
                if symbol in self.positions:
                    exit_reason = self.calculate_exit(symbol, price, current_time)
                    if exit_reason:
                        self.exit_position(symbol, price, current_time, exit_reason)
                
                # Check entries
                if self.check_entry_signal(symbol, current_time):
                    self.enter_position(symbol, price, current_time)
        
        # Close any remaining positions at end
        for symbol in list(self.positions.keys()):
            last_candle = market_data[symbol][-1]
            self.exit_position(symbol, last_candle['price'], last_candle['time'], "SESSION_END")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate final backtest report"""
        print()
        print("="*70)
        print("SKYLAR V2 BACKTEST RESULTS")
        print("="*70)
        
        wins = [t for t in self.trade_history if t.pnl_sol > 0]
        losses = [t for t in self.trade_history if t.pnl_sol <= 0]
        
        total_pnl = sum(t.pnl_sol for t in self.trade_history)
        win_rate = len(wins) / len(self.trade_history) * 100 if self.trade_history else 0
        
        avg_hold = np.mean([t.hold_minutes for t in self.trade_history]) if self.trade_history else 0
        
        # Calculate avg win/loss
        avg_win = np.mean([t.pnl_sol for t in wins]) if wins else 0
        avg_loss = np.mean([t.pnl_sol for t in losses]) if losses else 0
        
        results = {
            "agent_name": "SKYLAR V2",
            "strategy": "Trend Following with Survivor Filter",
            "personality": "Adaptive, trend-following, rides strong momentum",
            "risk_appetite": "MODERATE",
            "backtest_period": {
                "start": "2026-02-21 00:00",
                "end": "2026-02-21 02:59",
                "duration_hours": 3
            },
            "initial_capital_sol": self.initial_capital,
            "final_capital_sol": self.initial_capital + total_pnl,
            "total_pnl_sol": round(total_pnl, 4),
            "total_pnl_pct": round((total_pnl / self.initial_capital) * 100, 2),
            "trade_count": len(self.trade_history),
            "win_rate": round(win_rate, 2),
            "wins": len(wins),
            "losses": len(losses),
            "avg_hold_minutes": round(avg_hold, 2),
            "avg_win_sol": round(avg_win, 4),
            "avg_loss_sol": round(avg_loss, 4),
            "max_concurrent_positions": self.MAX_CONCURRENT,
            "position_size_sol": self.POSITION_SIZE_SOL,
            "trades": [
                {
                    "symbol": t.symbol,
                    "entry_time": t.entry_time.strftime("%H:%M"),
                    "exit_time": t.exit_time.strftime("%H:%M") if t.exit_time else None,
                    "entry_price": round(t.entry_price, 8),
                    "exit_price": round(t.exit_price, 8),
                    "pnl_sol": round(t.pnl_sol, 4),
                    "pnl_pct": round(t.pnl_pct * 100, 2),
                    "hold_minutes": round(t.hold_minutes, 1),
                    "exit_reason": t.exit_reason
                }
                for t in self.trade_history
            ]
        }
        
        print(f"\n📊 FINAL P&L: {total_pnl:+.4f} SOL ({(total_pnl/self.initial_capital)*100:+.2f}%)")
        print(f"🏆 Win Rate: {win_rate:.1f}% ({len(wins)}/{len(self.trade_history)})")
        print(f"📈 Total Trades: {len(self.trade_history)}")
        print(f"⏱️  Avg Hold Time: {avg_hold:.1f} minutes")
        print(f"💰 Avg Win: {avg_win:.4f} SOL | Avg Loss: {avg_loss:.4f} SOL")
        print(f"🎯 Final Balance: {self.initial_capital + total_pnl:.4f} SOL")
        print()
        
        return results

def main():
    """Run SKYLAR V2 backtest"""
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Create agent with 1 SOL capital
    skylar = SkylarV2(initial_capital=1.0)
    
    # Run backtest from 2026-02-21 00:00 to 02:59 (3 hours)
    start_time = datetime(2026, 2, 20, 13, 0, 0, tzinfo=timezone.utc)  # 00:00 Sydney = 13:00 UTC previous day
    
    results = skylar.run_backtest(start_time, hours=3)
    
    # Save to JSON file
    output_path = "/tmp/skylar_v2_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")
    
    return results

if __name__ == "__main__":
    main()
