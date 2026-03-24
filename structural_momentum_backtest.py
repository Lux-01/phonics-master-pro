#!/usr/bin/env python3
"""
Structural Momentum with RSI Divergence Strategy Backtest
===========================================================
Entry Rules (ALL must be met):
1. Trend Structure: Price makes higher low (HL) or lower low depending on setup
2. RSI Divergence: Price makes higher high BUT RSI makes lower high (bearish) 
   OR price makes lower low BUT RSI makes higher low (bullish)
3. Volume Confirmation: Volume on the divergence candle is 1.5x average
4. Support/Test: Price is at or near a recent support/resistance level

Exit Rules:
- Target 1: Close 50% at first resistance/support (3-5% move)
- Target 2: Trail remaining at -5% from peak or until opposing RSI divergence
- Stop: 2% beyond the swing low/high
- Time stop: 2 hours maximum
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

# API Configuration
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BASE_URL = "https://public-api.birdeye.so"

# Token Addresses (Solana)
TOKENS = {
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "MEW": "MEW1gQWJ3nEXg2qgERiKu5RAReMVrCXkAAd2dBEH7Jf",
    "GIGA": "63LfDmNb3MQ8MW9AbZivb2pTCYQ6i4r8hF1yT3qY7ZV",  # Volatile meme
    "MOODENG": "ED5nyyWEzpPPiWimP5vQy7UniKvCe7TJ1kTbD3nEqs7j",  # Trending
    "Pnut": "2qEHjDLDLbuBgRYvsxhc5D8uE4JnJ6BQv2R4bH3w4XHi",  # Popular
    "FARTCOIN": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",  # Volatile
}

@dataclass
class OHLCV:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
@dataclass
class Trade:
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime]
    exit_price: Optional[float]
    direction: str  # 'long' or 'short'
    size: float
    pnl_pct: float
    exit_reason: str
    targets_hit: int
    
def fetch_ohlcv(address: str, timeframe: str = "15m", days: int = 14) -> List[OHLCV]:
    """Fetch OHLCV data from Birdeye API"""
    end_time = int(time.time())
    start_time = end_time - (days * 24 * 3600)
    
    url = f"{BASE_URL}/defi/ohlcv"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    params = {
        "address": address,
        "type": timeframe,
        "time_from": start_time,
        "time_to": end_time
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()
        
        if not data.get("success", False):
            print(f"  API error: {data.get('message', 'Unknown error')}")
            return []
        
        items = data.get("data", {}).get("items", [])
        candles = []
        for item in items:
            candles.append(OHLCV(
                timestamp=item["unixTime"],
                open=item["o"],
                high=item["h"],
                low=item["l"],
                close=item["c"],
                volume=item.get("v", 0)
            ))
        return candles
    except Exception as e:
        print(f"  Error fetching data: {e}")
        return []

def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Calculate RSI(14)"""
    if len(prices) < period + 1:
        return [50.0] * len(prices)
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    rsis = [50.0] * period  # Neutral RSI for initial period
    
    # First average gain/loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsis.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsis.append(rsi)
    
    return rsis

def find_swing_points(prices: List[float], lookback: int = 8) -> Tuple[List[int], List[int]]:
    """Find swing highs and lows using local extrema"""
    swing_highs = []
    swing_lows = []
    
    for i in range(lookback, len(prices) - lookback):
        # Check if this is a local maximum (swing high)
        is_high = all(prices[i] >= prices[j] for j in range(i - lookback, i + lookback + 1) if j != i)
        if is_high:
            swing_highs.append(i)
        
        # Check if this is a local minimum (swing low)
        is_low = all(prices[i] <= prices[j] for j in range(i - lookback, i + lookback + 1) if j != i)
        if is_low:
            swing_lows.append(i)
    
    return swing_highs, swing_lows

def find_divergences(prices: List[float], rsi: List[float], swing_highs: List[int], 
                     swing_lows: List[int], window: int = 5) -> Dict[str, List[Dict]]:
    """Find RSI divergences"""
    divergences = {"bullish": [], "bearish": [], "hidden_bullish": [], "hidden_bearish": []}
    
    # Regular Bullish Divergence: Lower low in price, higher low in RSI
    for i in range(1, len(swing_lows)):
        curr_idx = swing_lows[i]
        prev_idx = swing_lows[i-1]
        
        if curr_idx >= len(prices) or prev_idx >= len(prices):
            continue
            
        if curr_idx >= len(rsi) or prev_idx >= len(rsi):
            continue
        
        price_lower_low = prices[curr_idx] < prices[prev_idx]
        rsi_higher_low = rsi[curr_idx] > rsi[prev_idx]
        
        if price_lower_low and rsi_higher_low:
            divergences["bullish"].append({
                "curr_idx": curr_idx,
                "prev_idx": prev_idx,
                "price_diff": abs(prices[prev_idx] - prices[curr_idx]) / prices[prev_idx],
                "rsi_diff": abs(rsi[curr_idx] - rsi[prev_idx])
            })
    
    # Regular Bearish Divergence: Higher high in price, lower high in RSI
    for i in range(1, len(swing_highs)):
        curr_idx = swing_highs[i]
        prev_idx = swing_highs[i-1]
        
        if curr_idx >= len(prices) or prev_idx >= len(prices):
            continue
            
        if curr_idx >= len(rsi) or prev_idx >= len(rsi):
            continue
        
        price_higher_high = prices[curr_idx] > prices[prev_idx]
        rsi_lower_high = rsi[curr_idx] < rsi[prev_idx]
        
        if price_higher_high and rsi_lower_high:
            divergences["bearish"].append({
                "curr_idx": curr_idx,
                "prev_idx": prev_idx,
                "price_diff": abs(prices[curr_idx] - prices[prev_idx]) / prices[prev_idx],
                "rsi_diff": abs(rsi[curr_idx] - rsi[prev_idx])
            })
    
    return divergences

def calculate_vwap(candles: List[OHLCV], window: int = 20) -> List[float]:
    """Calculate simple VWAP-based support/resistance levels"""
    vwaps = []
    for i in range(len(candles)):
        start = max(0, i - window)
        total_pv = sum((c.high + c.low + c.close) / 3 * c.volume for c in candles[start:i+1])
        total_v = sum(c.volume for c in candles[start:i+1])
        vwaps.append(total_pv / total_v if total_v > 0 else candles[i].close)
    return vwaps

def find_support_resistance(candles: List[OHLCV], window: int = 10) -> Tuple[float, float]:
    """Find recent support and resistance levels"""
    recent = candles[-window:] if len(candles) >= window else candles
    if not recent:
        return 0, 0
    
    support = min(c.low for c in recent)
    resistance = max(c.high for c in recent)
    return support, resistance

def check_volume_spike(candles: List[OHLCV], idx: int, multiplier: float = 1.5) -> bool:
    """Check if volume at idx is significantly above average"""
    if idx < 10 or idx >= len(candles):
        return False
    
    # Calculate average volume of previous 20 candles
    avg_volume = sum(c.volume for c in candles[idx-20:idx]) / 20
    current_volume = candles[idx].volume
    
    return current_volume > avg_volume * multiplier

def is_near_level(price: float, level: float, tolerance: float = 0.02) -> bool:
    """Check if price is near a support/resistance level"""
    return abs(price - level) / price < tolerance

class StructuralMomentumStrategy:
    def __init__(self, candles: List[OHLCV]):
        self.candles = candles
        self.rsi = calculate_rsi([c.close for c in candles])
        self.swing_highs, self.swing_lows = find_swing_points([c.close for c in candles])
        self.divergences = find_divergences(
            [c.close for c in candles], 
            self.rsi, 
            self.swing_highs, 
            self.swing_lows
        )
    
    def generate_signals(self) -> List[Dict]:
        """Generate entry signals based on strategy rules"""
        signals = []
        
        for div_type, div_list in self.divergences.items():
            for div in div_list:
                idx = div["curr_idx"]
                if idx >= len(self.candles) - 1:
                    continue
                
                candle = self.candles[idx]
                price = candle.close
                
                # Check volume confirmation
                if not check_volume_spike(self.candles, idx, 1.5):
                    continue
                
                # Find recent support/resistance
                support, resistance = find_support_resistance(self.candles[:idx+1])
                
                # Check if price is near support/resistance
                near_support = is_near_level(price, support)
                near_resistance = is_near_level(price, resistance)
                
                # Determine direction and validate context
                if div_type == "bullish":
                    if not near_support:
                        continue
                    # Check trend structure - looking for higher low
                    if idx > 10 and price < self.candles[idx-10].close * 0.95:
                        direction = "long"
                    else:
                        continue
                elif div_type == "bearish":
                    if not near_resistance:
                        continue
                    # Check trend structure - looking for lower high pattern
                    if idx > 10 and price > self.candles[idx-10].close * 1.05:
                        direction = "short"
                    else:
                        continue
                else:
                    continue
                
                signals.append({
                    "idx": idx,
                    "time": datetime.fromtimestamp(candle.timestamp),
                    "price": price,
                    "direction": direction,
                    "div_type": div_type,
                    "rsi": self.rsi[idx],
                    "support": support,
                    "resistance": resistance,
                    "volume": candle.volume
                })
        
        return signals
    
    def run_backtest(self, initial_capital: float = 10000) -> Dict:
        """Run complete backtest simulation"""
        signals = self.generate_signals()
        trades = []
        capital = initial_capital
        position = None
        max_capital = capital
        min_capital = capital
        
        for signal in signals:
            idx = signal["idx"]
            entry_price = signal["price"]
            direction = signal["direction"]
            entry_time = signal["time"]
            
            # Find stop loss level
            if direction == "long":
                stop_idx = max(0, idx - 20)
                swing_lows_recent = [i for i in self.swing_lows if i < idx and i >= stop_idx]
                if swing_lows_recent:
                    stop_price = min(self.candles[i].low for i in swing_lows_recent) * 0.98
                else:
                    stop_price = entry_price * 0.97
            else:
                stop_idx = max(0, idx - 20)
                swing_highs_recent = [i for i in self.swing_highs if i < idx and i >= stop_idx]
                if swing_highs_recent:
                    stop_price = max(self.candles[i].high for i in swing_highs_recent) * 1.02
                else:
                    stop_price = entry_price * 1.03
            
            # Calculate position size (2% risk)
            risk_amount = capital * 0.02
            stop_pct = abs(stop_price - entry_price) / entry_price
            if stop_pct == 0:
                continue
            position_size = risk_amount / stop_pct
            
            # Simulate trade
            exit_idx = idx + 1
            time_stop_idx = min(idx + 8, len(self.candles) - 1)  # 2 hours = 8 candles of 15m
            highest_price = entry_price
            lowest_price = entry_price
            targets_hit = 0
            exit_price = None
            exit_reason = None
            
            for i in range(idx + 1, min(len(self.candles), idx + 100)):
                candle = self.candles[i]
                
                # Track high/low
                if candle.high > highest_price:
                    highest_price = candle.high
                if candle.low < lowest_price:
                    lowest_price = candle.low
                
                # Check stop loss
                if direction == "long" and candle.low <= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop_loss"
                    exit_idx = i
                    break
                elif direction == "short" and candle.high >= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop_loss"
                    exit_idx = i
                    break
                
                # Check target 1 (3-5% move)
                if direction == "long" and targets_hit == 0:
                    target1 = entry_price * 1.04  # 4% target
                    if candle.high >= target1:
                        # Close 50% at target 1
                        targets_hit = 1
                elif direction == "short" and targets_hit == 0:
                    target1 = entry_price * 0.96  # 4% target
                    if candle.low <= target1:
                        targets_hit = 1
                
                # Check trailing stop for remaining position
                if direction == "long" and targets_hit == 1:
                    trailing_stop = highest_price * 0.95
                    if candle.low <= trailing_stop:
                        exit_price = trailing_stop
                        exit_reason = "trailing_stop"
                        exit_idx = i
                        break
                elif direction == "short" and targets_hit == 1:
                    trailing_stop = lowest_price * 1.05
                    if candle.high >= trailing_stop:
                        exit_price = trailing_stop
                        exit_reason = "trailing_stop"
                        exit_idx = i
                        break
                
                # Check time stop (2 hours = 8 candles)
                if i >= time_stop_idx:
                    exit_price = candle.close
                    exit_reason = "time_stop"
                    exit_idx = i
                    break
                
                # Check opposing divergence
                if i < len(self.rsi) and i > idx + 2:
                    recent_highs, recent_lows = find_swing_points([c.close for c in self.candles[:i+1]])
                    if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                        recent_div = find_divergences(
                            [c.close for c in self.candles[:i+1]],
                            self.rsi[:i+1],
                            recent_highs,
                            recent_lows
                        )
                        
                        if direction == "long" and recent_div["bearish"]:
                            last_bear = max(d["curr_idx"] for d in recent_div["bearish"] if d["curr_idx"] <= i)
                            if last_bear > idx:
                                exit_price = candle.close
                                exit_reason = "opposing_divergence"
                                exit_idx = i
                                break
                        elif direction == "short" and recent_div["bullish"]:
                            last_bull = max(d["curr_idx"] for d in recent_div["bullish"] if d["curr_idx"] <= i)
                            if last_bull > idx:
                                exit_price = candle.close
                                exit_reason = "opposing_divergence"
                                exit_idx = i
                                break
            
            # Calculate P&L
            if exit_price is None:
                exit_price = self.candles[min(exit_idx, len(self.candles) - 1)].close
                exit_reason = exit_reason or "end_of_data"
            
            if direction == "long":
                pnl_pct = (exit_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - exit_price) / entry_price
            
            # Apply targets - if target 1 hit, we closed 50% at target and rest at exit
            if targets_hit == 1:
                pnl_pct = pnl_pct * 0.5 + 0.04 * 0.5 if direction == "long" else pnl_pct * 0.5 - 0.04 * 0.5
            
            trade_pnl = position_size * pnl_pct
            capital += trade_pnl
            
            max_capital = max(max_capital, capital)
            min_capital = min(min_capital, capital)
            
            trades.append(Trade(
                entry_time=entry_time,
                entry_price=entry_price,
                exit_time=datetime.fromtimestamp(self.candles[exit_idx].timestamp),
                exit_price=exit_price,
                direction=direction,
                size=position_size,
                pnl_pct=pnl_pct * 100,
                exit_reason=exit_reason,
                targets_hit=targets_hit
            ))
        
        # Calculate metrics
        if trades:
            winning_trades = [t for t in trades if t.pnl_pct > 0]
            losing_trades = [t for t in trades if t.pnl_pct <= 0]
            
            win_rate = len(winning_trades) / len(trades) if trades else 0
            avg_win = sum(t.pnl_pct for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t.pnl_pct for t in losing_trades) / len(losing_trades) if losing_trades else 0
            
            gross_profit = sum(t.pnl_pct for t in winning_trades)
            gross_loss = abs(sum(t.pnl_pct for t in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            max_drawdown = (max_capital - min_capital) / max_capital * 100 if max_capital > 0 else 0
            total_return = (capital - initial_capital) / initial_capital * 100
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
            max_drawdown = 0
            total_return = 0
        
        return {
            "trades": trades,
            "metrics": {
                "total_trades": len(trades),
                "winning_trades": len([t for t in trades if t.pnl_pct > 0]),
                "losing_trades": len([t for t in trades if t.pnl_pct <= 0]),
                "win_rate": win_rate * 100,
                "avg_win_pct": avg_win,
                "avg_loss_pct": avg_loss,
                "profit_factor": profit_factor,
                "max_drawdown_pct": max_drawdown,
                "total_return_pct": total_return,
                "final_capital": capital,
                "initial_capital": initial_capital
            },
            "exit_reasons": defaultdict(int)
        }

def run_full_backtest():
    """Run backtest on all configured tokens"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "strategy": "Structural Momentum with RSI Divergence",
        "parameters": {
            "rsi_period": 14,
            "swing_lookback": 8,
            "volume_multiplier": 1.5,
            "target_pct": 4,
            "stop_pct": 2,
            "time_stop_hours": 2
        },
        "tokens": {}
    }
    
    print("=" * 80)
    print("STRUCTURAL MOMENTUM WITH RSI DIVERGENCE BACKTEST")
    print("=" * 80)
    print(f"Testing {len(TOKENS)} tokens over 14 days of 15m data\n")
    
    all_trades = []
    
    for symbol, address in TOKENS.items():
        print(f"\n{'='*60}")
        print(f"Testing: {symbol}")
        print(f"Address: {address[:30]}...")
        print("="*60)
        
        candles = fetch_ohlcv(address, "15m", 14)
        if len(candles) < 100:
            print(f"  Insufficient data: only {len(candles)} candles")
            continue
        
        print(f"  Fetched {len(candles)} candles")
        
        strategy = StructuralMomentumStrategy(candles)
        print(f"  Found {len(strategy.swing_highs)} swing highs, {len(strategy.swing_lows)} swing lows")
        print(f"  Divergences - Bullish: {len(strategy.divergences['bullish'])}, Bearish: {len(strategy.divergences['bearish'])}")
        
        result = strategy.run_backtest()
        
        if result["trades"]:
            m = result["metrics"]
            results["tokens"][symbol] = {
                "metrics": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()},
                "trades": [
                    {
                        "entry": t.entry_time.isoformat(),
                        "exit": t.exit_time.isoformat() if t.exit_time else None,
                        "direction": t.direction,
                        "entry_price": round(t.entry_price, 8),
                        "exit_price": round(t.exit_price, 8) if t.exit_price else None,
                        "pnl_pct": round(t.pnl_pct, 4),
                        "exit_reason": t.exit_reason,
                        "targets_hit": t.targets_hit
                    }
                    for t in result["trades"]
                ]
            }
            
            all_trades.extend(result["trades"])
            
            print(f"\n  RESULTS FOR {symbol}:")
            print(f"  {'Trades:':<25} {m['total_trades']}")
            print(f"  {'Win Rate:':<25} {m['win_rate']:.2f}%")
            print(f"  {'Avg Win:':<25} {m['avg_win_pct']:.2f}%")
            print(f"  {'Avg Loss:':<25} {m['avg_loss_pct']:.2f}%")
            print(f"  {'Profit Factor:':<25} {m['profit_factor']:.2f}")
            print(f"  {'Max Drawdown:':<25} {m['max_drawdown_pct']:.2f}%")
            print(f"  {'Total Return:':<25} {m['total_return_pct']:.2f}%")
        else:
            print(f"  No trades generated")
            results["tokens"][symbol] = {"metrics": {"total_trades": 0}, "trades": []}
    
    # Calculate aggregate results
    if all_trades:
        winning = [t for t in all_trades if t.pnl_pct > 0]
        losing = [t for t in all_trades if t.pnl_pct <= 0]
        
        results["aggregate"] = {
            "total_trades": len(all_trades),
            "symbols_tested": len(TOKENS),
            "win_rate": len(winning) / len(all_trades) * 100,
            "profit_factor": abs(sum(t.pnl_pct for t in winning)) / abs(sum(t.pnl_pct for t in losing)) if losing else float('inf'),
            "avg_trade_return": sum(t.pnl_pct for t in all_trades) / len(all_trades),
            "success": len(winning) / len(all_trades) > 0.55 and (abs(sum(t.pnl_pct for t in winning)) / abs(sum(t.pnl_pct for t in losing)) if losing else 1) > 1.5
        }
    
    # Save results
    with open("structural_momentum_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    if "aggregate" in results:
        a = results["aggregate"]
        print(f"{'Total Trades:':<30} {a['total_trades']}")
        print(f"{'Symbols Tested:':<30} {a['symbols_tested']}")
        print(f"{'Aggregate Win Rate:':<30} {a['win_rate']:.2f}%")
        print(f"{'Aggregate Profit Factor:':<30} {a['profit_factor']:.2f}")
        print(f"{'Avg Trade Return:':<30} {a['avg_trade_return']:.2f}%")
        print(f"\n{'SUCCESS CRITERIA:':<30}")
        print(f"  Win Rate > 55%:             {'✓ PASS' if a['win_rate'] > 55 else '✗ FAIL'}")
        print(f"  Profit Factor > 1.5:        {'✓ PASS' if a['profit_factor'] > 1.5 else '✗ FAIL'}")
    
    print(f"\nResults saved to: structural_momentum_results.json")
    return results

if __name__ == "__main__":
    results = run_full_backtest()
