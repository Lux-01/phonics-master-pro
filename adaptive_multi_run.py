#!/usr/bin/env python3
"""
Extended Adaptive Paper Trading for Better Mode Comparison
Adjusted parameters to trigger more breakout trades
"""

import json
import time
import asyncio
import random
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum

class Mode(Enum):
    DIP = "dip"
    BREAKOUT = "breakout"

class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    STOPPED = "stopped"
    TARGET_HIT = "target_hit"

@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class Trade:
    id: str
    mode: Mode
    coin: str
    entry_price: float
    position_size_sol: float
    entry_time: str
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    status: TradeStatus = TradeStatus.OPEN
    pnl_sol: float = 0.0
    pnl_percent: float = 0.0
    exit_reason: str = ""
    scaled: bool = False
    peak_price: float = 0.0
    trailing_stop_price: float = 0.0

class RealisticCryptoSimulator:
    COINS = {
        "BONK": {"base_price": 0.000012, "volatility": 0.09, "trend_bias": 0.02},
        "WIF": {"base_price": 1.85, "volatility": 0.07, "trend_bias": 0.03},
        "POPCAT": {"base_price": 0.42, "volatility": 0.10, "trend_bias": 0.01},
        "BOME": {"base_price": 0.0085, "volatility": 0.13, "trend_bias": 0.02},
        "SLERF": {"base_price": 0.15, "volatility": 0.12, "trend_bias": -0.01},
        "PONKE": {"base_price": 0.035, "volatility": 0.15, "trend_bias": 0.04},
        "MYRO": {"base_price": 0.045, "volatility": 0.11, "trend_bias": 0.03},
        "WEN": {"base_price": 0.000085, "volatility": 0.08, "trend_bias": 0.02},
        "TURBO": {"base_price": 0.0042, "volatility": 0.10, "trend_bias": 0.02},
        "GME": {"base_price": 0.012, "volatility": 0.16, "trend_bias": 0.05},
    }
    
    def __init__(self):
        self.prices = {name: data["base_price"] for name, data in self.COINS.items()}
        self.candle_history = {name: [] for name in self.COINS}
        self.market_regime = {name: "neutral" for name in self.COINS}
        self.regime_duration = {name: 0 for name in self.COINS}
        
        for name in self.COINS:
            for i in range(20):
                self._generate_candle(name, is_initial=True)
    
    def _generate_candle(self, coin: str, is_initial: bool = False):
        data = self.COINS[coin]
        current_price = self.prices[coin]
        
        if not is_initial and random.random() < 0.08:  # Higher regime change probability
            self.regime_duration[coin] = 0
            regimes = ["bullish", "bearish", "ranging"]
            weights = [0.40, 0.25, 0.35]
            self.market_regime[coin] = random.choices(regimes, weights)[0]
        
        regime = self.market_regime[coin]
        self.regime_duration[coin] += 1
        
        if regime == "bullish":
            base_change = random.gauss(0.025, data["volatility"] * 0.5)
        elif regime == "bearish":
            base_change = random.gauss(-0.02, data["volatility"] * 0.5)
        else:
            base_change = random.gauss(0, data["volatility"] * 0.4)
        
        base_change += data["trend_bias"] * 0.01
        
        if random.random() < 0.06:
            event_change = random.choice([-1, 1]) * random.uniform(0.06, 0.18)
            base_change += event_change
        
        body_change = base_change
        wick_factor = data["volatility"] * 0.6
        high_wick = abs(random.gauss(0, wick_factor))
        low_wick = abs(random.gauss(0, wick_factor))
        
        open_price = current_price
        close_price = current_price * (1 + body_change)
        high_price = max(open_price, close_price) * (1 + high_wick)
        low_price = min(open_price, close_price) * (1 - low_wick)
        
        base_volume = random.uniform(100000, 1000000)
        volume_multiplier = 1 + abs(body_change) * 10 + random.uniform(0, 2)
        volume = base_volume * volume_multiplier
        
        candle = Candle(
            timestamp=int(time.time()),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        )
        
        self.candle_history[coin].append(candle)
        self.prices[coin] = close_price
        
        if len(self.candle_history[coin]) > 100:
            self.candle_history[coin].pop(0)
        
        return candle
    
    def update_all(self):
        for coin in self.COINS:
            self._generate_candle(coin)
        return self.get_current_prices()
    
    def get_current_prices(self):
        return self.prices.copy()
    
    def get_candles(self, coin: str, limit: int = 50):
        return self.candle_history[coin][-limit:] if coin in self.candle_history else []


class AdaptiveStrategy:
    def __init__(self, initial_capital: float = 1.0):
        self.initial_capital = initial_capital
        self.balance_sol = initial_capital
        self.peak_balance = initial_capital
        self.min_balance = initial_capital
        self.positions: Dict[str, Trade] = {}
        self.trades: List[Trade] = []
        self.trade_counter = 0
        self.session_start = datetime.now(timezone.utc).isoformat()
        
        self.ema_fast_period = 9
        self.ema_slow_period = 21
        self.scale_target = 0.20
        self.trailing_stop_pct = 0.10
        self.hard_stop_pct = 0.07
        
        self.mode_performance = {
            Mode.DIP.value: {"trades": 0, "wins": 0, "pnl": 0.0},
            Mode.BREAKOUT.value: {"trades": 0, "wins": 0, "pnl": 0.0}
        }
        
        self.market_conditions: List[Dict] = []
    
    def generate_trade_id(self):
        self.trade_counter += 1
        return f"ADAPTIVE_{int(time.time())}_{self.trade_counter}"
    
    def calculate_ema(self, prices: List[float], period: int):
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def detect_market_condition(self, candles: List[Candle]):
        if len(candles) < 20:
            return Mode.DIP, {"reason": "insufficient_data", "confidence": 0.3}
        
        closes = [c.close for c in candles]
        ema_fast = self.calculate_ema(closes, self.ema_fast_period)
        ema_slow = self.calculate_ema(closes, self.ema_slow_period)
        
        price_changes = [(closes[i] - closes[i-1]) / closes[i-1] * 100 
                        for i in range(1, len(closes))]
        
        recent_changes = price_changes[-10:]
        avg_recent_change = sum(recent_changes) / len(recent_changes)
        
        higher_highs = sum(1 for i in range(-10, -1) if candles[i].high > candles[i-1].high)
        higher_lows = sum(1 for i in range(-10, -1) if candles[i].low > candles[i-1].low)
        
        volatility = statistics.stdev(price_changes[-15:]) if len(price_changes) >= 15 else 5.0
        
        trend_score = 0
        
        # EMA alignment (lowered thresholds to trigger more breakouts)
        if ema_fast > ema_slow * 1.015:  # Changed from 1.02
            trend_score += 2.5  # Changed from 3
        elif ema_fast > ema_slow:
            trend_score += 1.5
        elif ema_fast < ema_slow * 0.985:
            trend_score -= 2.5
        elif ema_fast < ema_slow:
            trend_score -= 1.5
        
        # Recent momentum (lowered thresholds)
        if avg_recent_change > 2.0:
            trend_score += 2
        elif avg_recent_change > 0.5:
            trend_score += 1
        elif avg_recent_change < -2.0:
            trend_score -= 2
        elif avg_recent_change < -0.5:
            trend_score -= 1
        
        # Pattern detection
        if higher_highs >= 6 and higher_lows >= 6:
            trend_score += 2
        elif higher_highs <= 3 and higher_lows <= 3:
            trend_score -= 2
        else:
            trend_score -= 0.5
        
        # Determine mode
        if trend_score >= 2.0:  # Changed from 2.5
            mode = Mode.BREAKOUT
            confidence = min(trend_score / 5, 1.0)
            reason = "strong_uptrend"
        elif trend_score <= -1.5:  # Changed from -2
            mode = Mode.DIP
            confidence = min(abs(trend_score) / 5, 1.0)
            reason = "downtrend_buy_dips"
        else:
            mode = Mode.DIP
            confidence = 0.6
            reason = "choppy_market_dip_mode"
        
        details = {
            "mode": mode.value,
            "trend_score": trend_score,
            "confidence": confidence,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "avg_change": avg_recent_change,
            "volatility": volatility,
            "higher_highs": higher_highs,
            "higher_lows": higher_lows,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return mode, details
    
    def find_dip_entry(self, candles: List[Candle], coin: str):
        if len(candles) < 10:
            return None
        
        current = candles[-1]
        recent_high = max(c.high for c in candles[-10:])
        pullback_pct = (recent_high - current.close) / recent_high * 100
        
        if not (3 <= pullback_pct <= 18):  # Wider range
            return None
        
        is_reversal = False
        
        if current.close > current.open:
            body_size = (current.close - current.open) / (current.high - current.low + 0.000001)
            if body_size > 0.25:
                is_reversal = True
        
        lower_wick = min(current.close, current.open) - current.low
        body_size = abs(current.close - current.open)
        if lower_wick > body_size * 1.2:
            is_reversal = True
        
        if not is_reversal:
            return None
        
        entry_price = current.close
        stop_loss = entry_price * (1 - self.hard_stop_pct)
        
        return {
            "coin": coin,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": entry_price * 1.25,
            "signal": "dip_reversal",
            "pullback_pct": pullback_pct
        }
    
    def find_breakout_entry(self, candles: List[Candle], coin: str):
        if len(candles) < 15:
            return None
        
        current = candles[-1]
        recent_candles = candles[-15:-1]
        resistance = max(c.high for c in recent_candles)
        
        breakout_pct = (current.close - resistance) / resistance * 100
        
        if breakout_pct < 2.5:  # Lowered from 3%
            return None
        
        recent_volume = sum(c.volume for c in candles[-3:]) / 3
        prev_volume = sum(c.volume for c in candles[-8:-3]) / 5
        volume_spike = recent_volume / prev_volume if prev_volume > 0 else 1
        
        if volume_spike < 1.2:  # Lowered from 1.3
            return None
        
        closes = [c.close for c in candles]
        ema_fast = self.calculate_ema(closes, 9)
        
        if current.close < ema_fast * 0.985:  # Slightly relaxed
            return None
        
        entry_price = current.close
        stop_loss = entry_price * (1 - self.hard_stop_pct)
        
        return {
            "coin": coin,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": entry_price * 1.20,
            "signal": "momentum_breakout",
            "volume_spike": volume_spike,
            "breakout_pct": breakout_pct
        }
    
    def open_position(self, signal: Dict, mode: Mode):
        coin = signal["coin"]
        
        if coin in self.positions:
            return None
        
        position_size = min(self.balance_sol * 0.35, self.balance_sol - 0.15)
        if position_size < 0.1:
            return None
        
        entry_price = signal["entry_price"]
        
        trade = Trade(
            id=self.generate_trade_id(),
            mode=mode,
            coin=coin,
            entry_price=entry_price,
            position_size_sol=position_size,
            entry_time=datetime.now(timezone.utc).isoformat(),
            peak_price=entry_price,
            trailing_stop_price=entry_price * (1 - self.hard_stop_pct)
        )
        
        self.positions[coin] = trade
        self.balance_sol -= position_size
        
        return trade
    
    def manage_position(self, trade: Trade, current_price: float):
        entry = trade.entry_price
        
        if current_price > trade.peak_price:
            trade.peak_price = current_price
            new_trailing = trade.peak_price * (1 - self.trailing_stop_pct)
            trade.trailing_stop_price = max(new_trailing, entry * (1 - self.hard_stop_pct))
        
        current_pnl_pct = (current_price - entry) / entry
        
        hard_stop_price = entry * (1 - self.hard_stop_pct)
        if current_price <= hard_stop_price:
            return "hard_stop"
        
        if not trade.scaled and current_pnl_pct >= self.scale_target:
            return "scale_50"
        
        if current_price <= trade.trailing_stop_price:
            return "trailing_stop"
        
        return None
    
    def partial_scale_out(self, coin: str, exit_price: float, candles: List[Candle]):
        if coin not in self.positions:
            return 0
        
        trade = self.positions[coin]
        trade.scaled = True
        
        half_position = trade.position_size_sol * 0.5
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        pnl = half_position * price_change_pct
        
        self.balance_sol += half_position + pnl
        trade.position_size_sol -= half_position
        
        return pnl
    
    def close_position(self, coin: str, exit_price: float, reason: str):
        trade = self.positions[coin]
        trade.exit_price = exit_price
        trade.exit_time = datetime.now(timezone.utc).isoformat()
        trade.exit_reason = reason
        
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        trade.pnl_sol = trade.position_size_sol * price_change_pct
        trade.pnl_percent = price_change_pct * 100
        
        if trade.pnl_sol > 0:
            trade.status = TradeStatus.TARGET_HIT
        else:
            trade.status = TradeStatus.STOPPED
        
        self.balance_sol += trade.position_size_sol + trade.pnl_sol
        
        mode_key = trade.mode.value
        self.mode_performance[mode_key]["trades"] += 1
        self.mode_performance[mode_key]["pnl"] += trade.pnl_sol
        if trade.pnl_sol > 0:
            self.mode_performance[mode_key]["wins"] += 1
        
        if self.balance_sol > self.peak_balance:
            self.peak_balance = self.balance_sol
        if self.balance_sol < self.min_balance:
            self.min_balance = self.balance_sol
        
        self.trades.append(trade)
        del self.positions[coin]
        
        return trade
    
    def get_results(self):
        return {
            "total_trades": len(self.trades),
            "dip_trades": self.mode_performance[Mode.DIP.value]["trades"],
            "breakout_trades": self.mode_performance[Mode.BREAKOUT.value]["trades"],
            "final_balance": self.balance_sol,
            "total_pnl": sum(t.pnl_sol for t in self.trades),
            "win_rate": sum(1 for t in self.trades if t.pnl_sol > 0) / len(self.trades) * 100 if self.trades else 0,
            "dip_win_rate": self.mode_performance[Mode.DIP.value]["wins"] / self.mode_performance[Mode.DIP.value]["trades"] * 100 if self.mode_performance[Mode.DIP.value]["trades"] > 0 else 0,
            "breakout_win_rate": self.mode_performance[Mode.BREAKOUT.value]["wins"] / self.mode_performance[Mode.BREAKOUT.value]["trades"] * 100 if self.mode_performance[Mode.BREAKOUT.value]["trades"] > 0 else 0,
            "dip_pnl": self.mode_performance[Mode.DIP.value]["pnl"],
            "breakout_pnl": self.mode_performance[Mode.BREAKOUT.value]["pnl"],
            "trades": [asdict(t) for t in self.trades],
            "mode_performance": self.mode_performance
        }


async def run_simulation(target_trades: int = 10):
    simulator = RealisticCryptoSimulator()
    strategy = AdaptiveStrategy(initial_capital=1.0)
    
    iteration = 0
    
    while len(strategy.trades) < target_trades:
        iteration += 1
        simulator.update_all()
        
        for coin in simulator.COINS:
            candles = simulator.get_candles(coin)
            
            if len(candles) < 20:
                continue
            
            mode, condition = strategy.detect_market_condition(candles)
            
            if coin in strategy.positions:
                current_price = candles[-1].close
                exit_reason = strategy.manage_position(strategy.positions[coin], current_price)
                
                if exit_reason == "scale_50":
                    strategy.partial_scale_out(coin, current_price, candles)
                elif exit_reason:
                    strategy.close_position(coin, current_price, exit_reason)
            
            elif len(strategy.positions) < 3:
                signal = None
                
                if mode == Mode.BREAKOUT:
                    signal = strategy.find_breakout_entry(candles, coin)
                else:
                    signal = strategy.find_dip_entry(candles, coin)
                
                if signal:
                    strategy.open_position(signal, mode)
        
        await asyncio.sleep(0.01)
    
    # Close remaining positions
    for coin in list(strategy.positions.keys()):
        current_price = simulator.get_current_prices()[coin]
        strategy.close_position(coin, current_price, "session_end")
    
    return strategy.get_results()


if __name__ == "__main__":
    # Run multiple simulations and average results
    import sys
    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    target_trades = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"\n{'='*80}")
    print("  ADAPTIVE STRATEGY - MULTI-RUN ANALYSIS")
    print(f"  Runs: {num_runs} | Target Trades per Run: {target_trades}")
    print(f"{'='*80}\n")
    
    all_results = []
    
    for run in range(num_runs):
        print(f"Run {run + 1}/{num_runs}...")
        result = asyncio.run(run_simulation(target_trades))
        all_results.append(result)
        print(f"  Complete: {result['total_trades']} trades, "
              f"DIP: {result['dip_trades']}, BREAKOUT: {result['breakout_trades']}, "
              f"Win Rate: {result['win_rate']:.1f}%, P&L: {result['total_pnl']:+.4f} SOL")
    
    # Aggregate results
    total_trades = sum(r['total_trades'] for r in all_results)
    total_dip = sum(r['dip_trades'] for r in all_results)
    total_breakout = sum(r['breakout_trades'] for r in all_results)
    avg_win_rate = sum(r['win_rate'] for r in all_results) / len(all_results)
    avg_pnl = sum(r['total_pnl'] for r in all_results) / len(all_results)
    
    dip_wins = sum(r['dip_win_rate'] * r['dip_trades'] for r in all_results if r['dip_trades'] > 0)
    dip_wins_avg = dip_wins / total_dip if total_dip > 0 else 0
    breakout_wins = sum(r['breakout_win_rate'] * r['breakout_trades'] for r in all_results if r['breakout_trades'] > 0)
    breakout_wins_avg = breakout_wins / total_breakout if total_breakout > 0 else 0
    
    total_dip_pnl = sum(r['dip_pnl'] for r in all_results)
    total_breakout_pnl = sum(r['breakout_pnl'] for r in all_results)
    
    print(f"\n{'='*80}")
    print("  AGGREGATED RESULTS")
    print(f"{'='*80}\n")
    
    print(f"📊 OVERALL ({num_runs} runs, {total_trades} total trades):")
    print(f"   Avg Win Rate: {avg_win_rate:.1f}%")
    print(f"   Avg P&L: {avg_pnl:+.4f} SOL ({avg_pnl/1.0*100:+.2f}%)")
    
    print(f"\n🔀 MODE BREAKDOWN:")
    print(f"   DIP Mode: {total_dip} trades ({total_dip/total_trades*100:.1f}%)")
    print(f"     • Weighted Win Rate: {dip_wins_avg:.1f}%")
    print(f"     • Total P&L: {total_dip_pnl:+.4f} SOL")
    print(f"     • Avg per Trade: {total_dip_pnl/total_dip if total_dip > 0 else 0:+.4f} SOL")
    
    print(f"\n   BREAKOUT Mode: {total_breakout} trades ({total_breakout/total_trades*100:.1f}%)")
    print(f"     • Weighted Win Rate: {breakout_wins_avg:.1f}%")
    print(f"     • Total P&L: {total_breakout_pnl:+.4f} SOL")
    print(f"     • Avg per Trade: {total_breakout_pnl/total_breakout if total_breakout > 0 else 0:+.4f} SOL")
    
    if total_breakout >= 3 and total_dip >= 3:
        print(f"\n🏆 WINNER:")
        if breakout_wins_avg > dip_wins_avg:
            print(f"   BREAKOUT mode has better win rate ({breakout_wins_avg:.0f}% vs {dip_wins_avg:.0f}%)")
        elif dip_wins_avg > breakout_wins_avg:
            print(f"   DIP mode has better win rate ({dip_wins_avg:.0f}% vs {breakout_wins_avg:.0f}%)")
        else:
            print(f"   Both modes perform equally ({dip_wins_avg:.0f}%)")
    
    print(f"\n{'='*80}\n")
    
    # Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_file = f"/home/skux/.openclaw/workspace/adaptive_aggregated_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "num_runs": num_runs,
            "aggregated": {
                "total_trades": total_trades,
                "avg_win_rate": avg_win_rate,
                "avg_pnl": avg_pnl,
                "dip_wins_avg": dip_wins_avg,
                "breakout_wins_avg": breakout_wins_avg,
                "total_dip_pnl": total_dip_pnl,
                "total_breakout_pnl": total_breakout_pnl
            },
            "runs": all_results
        }, f, indent=2, default=str)
    print(f"💾 Results saved to: {results_file}")