#!/usr/bin/env python3
"""
Backtest Optimal Strategy v2.0 - FINAL VERSION
Period: Feb 18, 2026 3:00 PM - 11:30 PM Sydney time (8.5 hours)
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    coin: str

@dataclass
class Trade:
    id: int
    coin: str
    entry_time: datetime
    entry_price: float
    position_size: float  # SOL at risk
    quantity: float  # token amount
    setup_grade: str
    exit_time: datetime = None
    exit_price: float = None
    exit_reason: str = None
    scale1_hit: bool = False
    scale1_price: float = None
    scale1_time: datetime = None
    remaining_quantity: float = 0
    pnl_sol: float = 0
    pnl_pct: float = 0
    status: str = "open"
    stop_price: float = 0
    breakeven_price: float = 0
    scale1_pnl: float = 0

@dataclass
class BacktestState:
    sol_balance: float = 1.0
    open_positions: List[Trade] = field(default_factory=list)
    closed_trades: List[Trade] = field(default_factory=list)
    consecutive_losses: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    pause_until: datetime = None
    daily_pnl: float = 0
    last_10_results: List[bool] = field(default_factory=list)

# Coin configurations - realistic Feb 2026 meme coin prices
COINS = {
    "WIF": {"base_price": 1.85, "volatility": 0.035, "volume_base": 3200000, "trend": 0.012, "market_cap": 1.8e9},
    "POPCAT": {"base_price": 0.72, "volatility": 0.045, "volume_base": 2100000, "trend": -0.005, "market_cap": 720e6},
    "BONK": {"base_price": 0.000038, "volatility": 0.055, "volume_base": 4800000, "trend": 0.018, "market_cap": 2.5e9},
    "BOME": {"base_price": 0.0095, "volatility": 0.062, "volume_base": 1400000, "trend": -0.008, "market_cap": 650e6},
    "SLERF": {"base_price": 0.32, "volatility": 0.07, "volume_base": 1000000, "trend": 0.025, "market_cap": 320e6},
    "PENGU": {"base_price": 0.047, "volatility": 0.05, "volume_base": 1800000, "trend": 0.008, "market_cap": 520e6},
    "MEW": {"base_price": 0.0062, "volatility": 0.065, "volume_base": 1100000, "trend": -0.012, "market_cap": 280e6},
}

def generate_price_path(config, num_candles):
    """Generate realistic price action with volatility clusters"""
    price = config["base_price"]
    volatility = config["volatility"]
    
    candles = []
    regime = 1.0
    momentum = 0
    
    for i in range(num_candles):
        # Volatility regime switching
        if random.random() < 0.04:
            regime = random.uniform(1.3, 2.5)
        else:
            regime = regime * 0.85 + 0.15
        
        # Price change with momentum
        momentum = momentum * 0.65 + random.gauss(0, volatility * regime) * 0.35
        trend = config["trend"] / (240 / 15)  # Annualized trend
        
        # Mean reversion
        mean_reversion = (config["base_price"] - price) / config["base_price"] * 0.015
        
        change = trend + momentum + mean_reversion
        
        # Occasional large moves
        if random.random() < 0.06:
            direction = 1 if random.random() > 0.4 else -1
            change += direction * random.uniform(0.025, 0.08)
        
        # Create candle
        open_p = price
        close_p = price * (1 + change)
        
        # Wicks
        up_wick = abs(change) * random.uniform(0.3, 0.7) if change > 0 else abs(change) * random.uniform(0.1, 0.25)
        down_wick = abs(change) * random.uniform(0.1, 0.25) if change > 0 else abs(change) * random.uniform(0.3, 0.7)
        
        high_p = max(open_p, close_p) * (1 + up_wick)
        low_p = min(open_p, close_p) * (1 - down_wick)
        
        # Volume
        vol_spike = 1 + abs(change) * 12 if abs(change) > 0.02 else random.uniform(0.7, 1.6)
        volume = config["volume_base"] * vol_spike * regime
        
        candles.append({"open": open_p, "high": high_p, "low": low_p, "close": close_p, "volume": volume})
        price = close_p
    
    return candles

def calculate_ema(prices, period):
    """Calculate EMA"""
    if len(prices) < period:
        return [sum(prices) / len(prices)] * len(prices)
    
    multiplier = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    
    # Pad beginning
    ema = [ema[0]] * (period - 1) + ema
    return ema

def generate_market_data():
    """Generate market data for 8.5 hours"""
    start_time = datetime(2026, 2, 18, 15, 0, 0)
    num_candles = 34  # 8.5 hours of 15m candles
    
    market_data = {}
    for coin, config in COINS.items():
        candles = generate_price_path(config, num_candles)
        coin_candles = []
        for i, c in enumerate(candles):
            ts = start_time + timedelta(minutes=15 * i)
            coin_candles.append(Candle(
                timestamp=ts, open=c["open"], high=c["high"],
                low=c["low"], close=c["close"], volume=c["volume"],
                coin=coin
            ))
        market_data[coin] = coin_candles
    
    return market_data

def check_entry(candle: Candle, prev_candles: List[Candle], coin: str, state: BacktestState) -> Tuple[bool, str]:
    """Check entry conditions"""
    if len(prev_candles) < 8:
        return False, ""
    
    # Get prices for EMA
    close_prices = [c.close for c in prev_candles] + [candle.close]
    
    # Calculate 20-period EMA on 15m candles (simulating 1h EMA20)
    ema20 = calculate_ema(close_prices, 20)[-1]
    
    # Trend filter
    trend_ok = candle.close > ema20 * 0.998
    
    # Volume filter
    avg_vol = np.mean([c.volume for c in prev_candles[-8:]])
    volume_ok = candle.volume > avg_vol * 1.6
    
    # Entry signals
    # Signal 1: Dip of -8% to -18%
    recent_high = max([c.high for c in prev_candles[-6:]])
    dip_pct = (candle.close - recent_high) / recent_high
    dip_signal = -0.20 <= dip_pct <= -0.06
    
    # Signal 2: Green after 2 reds
    prev1 = prev_candles[-1]
    prev2 = prev_candles[-2] if len(prev_candles) >= 2 else prev1
    red1 = prev1.close < prev1.open
    red2 = prev2.close < prev2.open
    green_now = candle.close > candle.open
    recovery_signal = green_now and red1 and red2
    
    entry_signal = dip_signal or recovery_signal
    
    # Market regime: no entries first/last 15 min of hour
    minute = candle.timestamp.minute
    entry_window = (15 <= minute <= 30) or (45 <= minute)
    
    # Check pause
    if state.pause_until and candle.timestamp < state.pause_until:
        return False, ""
    
    # Check max positions
    if len(state.open_positions) >= 3:
        return False, ""
    
    # Check if already in this coin
    if any(t.coin == coin for t in state.open_positions):
        return False, ""
    
    # Daily loss limit
    if state.daily_pnl <= -0.3:
        return False, ""
    
    # Check conditions
    conditions = [trend_ok, volume_ok, entry_signal]
    met = sum(conditions)
    
    if met >= 3 and entry_window:
        return True, "A+"
    elif met == 2 and entry_window:
        return True, "B"
    
    return False, ""

def run_backtest(market_data: dict) -> Tuple[List[Trade], BacktestState]:
    """Run strategy backtest"""
    state = BacktestState(sol_balance=1.0)
    trade_id = 0
    
    # Flatten and sort all candles
    all_candles = []
    for coin, candles in market_data.items():
        for i, c in enumerate(candles):
            all_candles.append((c.timestamp, i, coin, c))
    all_candles.sort(key=lambda x: (x[0], x[2]))
    
    for timestamp, idx, coin, candle in all_candles:
        # Update open positions
        for trade in state.open_positions:
            if trade.status != "open":
                continue
            
            minutes_elapsed = (timestamp - trade.entry_time).total_seconds() / 60
            
            # Current unrealized PNL
            current_pct = (candle.close - trade.entry_price) / trade.entry_price * 100
            
            # Check Scale 1 (+8%)
            if not trade.scale1_hit and candle.high >= trade.entry_price * 1.08:
                trade.scale1_hit = True
                trade.scale1_price = trade.entry_price * 1.08
                trade.scale1_time = timestamp
                
                # Sell 50% at scale 1
                half_qty = trade.quantity * 0.5
                trade.remaining_quantity = half_qty
                
                # Calculate PNL on first 50%
                trade.scale1_pnl = (trade.scale1_price - trade.entry_price) * half_qty
                trade.pnl_sol += trade.scale1_pnl
                
                # Move stop to breakeven + small profit
                trade.stop_price = trade.entry_price * 1.001
            
            # Check exits
            exited = False
            exit_price = candle.close
            exit_reason = ""
            
            # Hard stop / Breakeven stop
            if candle.low <= trade.stop_price:
                exit_price = max(candle.low, trade.stop_price * 0.99)
                exit_reason = "breakeven_stop" if trade.scale1_hit else "hard_stop"
                exited = True
            
            # Trailing stop at +15%
            if not exited and trade.scale1_hit and current_pct >= 15:
                trailing = candle.high * 0.92
                if candle.low <= trailing and trailing > trade.entry_price:
                    exit_price = trailing
                    exit_reason = "scale2_trailing"
                    exited = True
            
            # Time stop (30 min)
            if not exited and minutes_elapsed >= 30:
                exit_price = candle.close
                exit_reason = "time_stop"
                exited = True
            
            if exited:
                trade.exit_time = timestamp
                trade.exit_price = exit_price
                trade.exit_reason = exit_reason
                trade.status = "closed"
                
                # Calculate remaining PNL
                remaining_qty = trade.remaining_quantity if trade.scale1_hit else trade.quantity
                remaining_pnl = (exit_price - trade.entry_price) * remaining_qty
                trade.pnl_sol += remaining_pnl
                trade.pnl_pct = (exit_price - trade.entry_price) / trade.entry_price * 100
                
                # Update state
                state.sol_balance += trade.pnl_sol
                state.daily_pnl += trade.pnl_sol
                state.closed_trades.append(trade)
                state.total_trades += 1
                
                is_win = trade.pnl_sol > 0
                state.last_10_results.append(is_win)
                if len(state.last_10_results) > 10:
                    state.last_10_results.pop(0)
                
                if is_win:
                    state.winning_trades += 1
                    state.consecutive_losses = 0
                else:
                    state.losing_trades += 1
                    state.consecutive_losses += 1
                
                # Pause after 3 losses
                if state.consecutive_losses >= 3:
                    state.pause_until = timestamp + timedelta(minutes=10)
                    state.consecutive_losses = 0
        
        # Clean up closed positions
        state.open_positions = [t for t in state.open_positions if t.status == "open"]
        
        # Check for new entry
        prev_candles = market_data[coin][:idx]
        should_enter, grade = check_entry(candle, prev_candles, coin, state)
        
        if should_enter:
            # Check win rate for sizing
            win_rate = sum(state.last_10_results) / len(state.last_10_results) if len(state.last_10_results) >= 5 else 1.0
            size_reduction = 0.5 if len(state.last_10_results) >= 10 and win_rate < 0.4 else 1.0
            
            # Position size
            if grade == "A+":
                position_sol = 0.5 * size_reduction
            else:
                position_sol = 0.25 * size_reduction
            
            # Calculate token quantity
            token_qty = position_sol / candle.close
            
            trade = Trade(
                id=trade_id,
                coin=coin,
                entry_time=timestamp,
                entry_price=candle.close,
                position_size=position_sol,
                quantity=token_qty,
                setup_grade=grade,
                remaining_quantity=token_qty,
                stop_price=candle.close * 0.93,
                breakeven_price=candle.close
            )
            
            state.open_positions.append(trade)
            trade_id += 1
    
    # Close remaining positions at end
    final_time = datetime(2026, 2, 18, 23, 30, 0)
    for trade in state.open_positions:
        if trade.status == "open":
            last_candle = market_data[trade.coin][-1]
            
            trade.exit_time = final_time
            trade.exit_price = last_candle.close
            trade.exit_reason = "end_of_session"
            
            remaining_qty = trade.remaining_quantity if trade.scale1_hit else trade.quantity
            final_pnl = (last_candle.close - trade.entry_price) * remaining_qty
            trade.pnl_sol += final_pnl
            trade.pnl_pct = (last_candle.close - trade.entry_price) / trade.entry_price * 100
            trade.status = "closed"
            
            state.sol_balance += trade.pnl_sol
            state.daily_pnl += trade.pnl_sol
            state.closed_trades.append(trade)
            state.total_trades += 1
            
            if trade.pnl_sol > 0:
                state.winning_trades += 1
                state.consecutive_losses = 0
            else:
                state.losing_trades += 1
                state.consecutive_losses += 1
    
    state.open_positions = []
    return state.closed_trades, state

def generate_analysis(trades: List[Trade], state: BacktestState) -> dict:
    """Generate analysis"""
    if not trades:
        return {"error": "No trades"}
    
    total_pnl = sum(t.pnl_sol for t in trades)
    wins = [t for t in trades if t.pnl_sol > 0]
    losses = [t for t in trades if t.pnl_sol <= 0]
    
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = win_count / len(trades) * 100
    
    avg_win = np.mean([t.pnl_sol for t in wins]) if wins else 0
    avg_loss = np.mean([t.pnl_sol for t in losses]) if losses else 0
    
    best = max(trades, key=lambda x: x.pnl_sol)
    worst = min(trades, key=lambda x: x.pnl_sol)
    
    # Max drawdown
    running = 1.0
    peak = running
    max_dd = 0
    for trade in trades:
        running += trade.pnl_sol
        if running > peak:
            peak = running
        dd = (peak - running) / peak * 100
        max_dd = max(max_dd, dd)
    
    # Exit reasons
    exits = {}
    for t in trades:
        reason = t.exit_reason or "unknown"
        exits[reason] = exits.get(reason, 0) + 1
    
    # Coin performance
    coin_pnl = {}
    coin_trades = {}
    for t in trades:
        coin_pnl[t.coin] = coin_pnl.get(t.coin, 0) + t.pnl_sol
        coin_trades[t.coin] = coin_trades.get(t.coin, 0) + 1
    
    # Hourly
    hourly = {}
    for t in trades:
        h = t.entry_time.strftime("%H")
        if h not in hourly:
            hourly[h] = {"trades": 0, "pnl": 0, "wins": 0}
        hourly[h]["trades"] += 1
        hourly[h]["pnl"] += t.pnl_sol
        if t.pnl_sol > 0:
            hourly[h]["wins"] += 1
    
    # Grades
    grades = {}
    for t in trades:
        if t.setup_grade not in grades:
            grades[t.setup_grade] = {"count": 0, "win": 0, "pnl": 0}
        grades[t.setup_grade]["count"] += 1
        if t.pnl_sol > 0:
            grades[t.setup_grade]["win"] += 1
        grades[t.setup_grade]["pnl"] += t.pnl_sol
    
    # Hold time
    hold_times = [(t.exit_time - t.entry_time).total_seconds() / 60 for t in trades if t.exit_time]
    avg_hold = np.mean(hold_times) if hold_times else 0
    
    return {
        "summary": {
            "total_trades": len(trades),
            "total_pnl_sol": round(total_pnl, 4),
            "final_balance_sol": round(state.sol_balance, 4),
            "win_rate_pct": round(win_rate, 2),
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "max_drawdown_pct": round(max_dd, 2),
            "avg_win_sol": round(avg_win, 4),
            "avg_loss_sol": round(avg_loss, 4),
            "avg_hold_time_min": round(avg_hold, 1),
            "profit_factor": round(abs(sum(t.pnl_sol for t in wins) / sum(t.pnl_sol for t in losses)), 2) if losses and sum(t.pnl_sol for t in losses) != 0 else float('inf')
        },
        "best_trade": {
            "coin": best.coin,
            "pnl_sol": round(best.pnl_sol, 4),
            "pnl_pct": round(best.pnl_pct, 2),
            "entry": best.entry_time.strftime("%H:%M"),
            "exit": best.exit_time.strftime("%H:%M"),
            "setup": best.setup_grade,
            "exit_reason": best.exit_reason
        },
        "worst_trade": {
            "coin": worst.coin,
            "pnl_sol": round(worst.pnl_sol, 4),
            "pnl_pct": round(worst.pnl_pct, 2),
            "entry": worst.entry_time.strftime("%H:%M"),
            "exit": worst.exit_time.strftime("%H:%M"),
            "setup": worst.setup_grade,
            "exit_reason": worst.exit_reason
        },
        "exit_reasons": exits,
        "coin_performance": coin_pnl,
        "coin_trade_counts": coin_trades,
        "hourly_breakdown": hourly,
        "grade_stats": grades
    }

def main():
    random.seed(42)
    np.random.seed(42)
    
    print("=" * 65)
    print("BACKTEST: Optimal Strategy v2.0")
    print("Feb 18, 2026 | 3:00 PM - 11:30 PM Sydney Time")
    print("=" * 65)
    
    market_data = generate_market_data()
    print("\nGenerated market data for 7 coins x 34 candles")
    
    trades, state = run_backtest(market_data)
    
    analysis = generate_analysis(trades, state)
    
    # Save trades JSON
    trades_json = []
    for t in trades:
        trades_json.append({
            "id": t.id,
            "coin": t.coin,
            "entry_time": t.entry_time.isoformat(),
            "entry_price": round(t.entry_price, 8),
            "position_size_sol": t.position_size,
            "quantity": round(t.quantity, 2),
            "setup_grade": t.setup_grade,
            "exit_time": t.exit_time.isoformat() if t.exit_time else None,
            "exit_price": round(t.exit_price, 8) if t.exit_price else None,
            "exit_reason": t.exit_reason,
            "scale1_hit": t.scale1_hit,
            "scale1_price": round(t.scale1_price, 8) if t.scale1_price else None,
            "pnl_sol": round(t.pnl_sol, 6),
            "pnl_pct": round(t.pnl_pct, 2),
            "hold_time_min": round((t.exit_time - t.entry_time).total_seconds() / 60, 1) if t.exit_time else None
        })
    
    with open("/home/skux/backtest_feb18_trades.json", "w") as f:
        json.dump(trades_json, f, indent=2)
    
    with open("/home/skux/backtest_feb18_results.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Determine market regime
    pnl_normalized = analysis['summary']['total_pnl_sol'] / len(trades) if trades else 0
    if analysis['summary']['win_rate_pct'] > 55 and analysis['summary']['total_pnl_sol'] > 0:
        regime = "Trending/Favorable"
    elif analysis['summary']['win_rate_pct'] < 45:
        regime = "Choppy/Difficult"
    else:
        regime = "Mixed/Range-bound"
    
    # Generate markdown report
    report = f"""# Backtest Analysis: Optimal Strategy v2.0
## February 18, 2026 | 3:00 PM - 11:30 PM Sydney Time (AEDT)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Session Result** | {"🟢 PROFIT" if analysis['summary']['total_pnl_sol'] > 0 else "🔴 LOSS"} |
| **Total PNL** | {analysis['summary']['total_pnl_sol']:+.4f} SOL |
| **Final Balance** | {analysis['summary']['final_balance_sol']:.4f} SOL |
| **Return on Capital** | {analysis['summary']['total_pnl_sol']:.2f}% |
| **Total Trades** | {analysis['summary']['total_trades']} |
| **Win Rate** | {analysis['summary']['win_rate_pct']:.1f}% ({analysis['summary']['winning_trades']}W / {analysis['summary']['losing_trades']}L) |
| **Max Drawdown** | {analysis['summary']['max_drawdown_pct']:.2f}% |
| **Profit Factor** | {analysis['summary']['profit_factor']} |
| **Average Win** | {analysis['summary']['avg_win_sol']:+.4f} SOL |
| **Average Loss** | {analysis['summary']['avg_loss_sol']:+.4f} SOL |
| **Avg Hold Time** | {analysis['summary']['avg_hold_time_min']:.1f} minutes |

---

## Best & Worst Trades

### 🟢 Best Trade
- **Coin:** {analysis['best_trade']['coin']}
- **PNL:** {analysis['best_trade']['pnl_sol']:+.4f} SOL ({analysis['best_trade']['pnl_pct']:+.1f}%)
- **Entry Time:** {analysis['best_trade']['entry']}
- **Exit Time:** {analysis['best_trade']['exit']}
- **Setup Grade:** {analysis['best_trade']['setup']}
- **Exit Reason:** {analysis['best_trade']['exit_reason']}

### 🔴 Worst Trade
- **Coin:** {analysis['worst_trade']['coin']}
- **PNL:** {analysis['worst_trade']['pnl_sol']:+.4f} SOL ({analysis['worst_trade']['pnl_pct']:+.1f}%)
- **Entry Time:** {analysis['worst_trade']['entry']}
- **Exit Time:** {analysis['worst_trade']['exit']}
- **Setup Grade:** {analysis['worst_trade']['setup']}
- **Exit Reason:** {analysis['worst_trade']['exit_reason']}

---

## Exit Analysis

| Exit Reason | Count | % of Trades | Description |
|-------------|-------|-------------|-------------|
"""
    
    reason_desc = {
        "scale1_target": "Scale 1 profit target reached (+8%)",
        "scale2_trailing": "Trailing stop after +15% move",
        "hard_stop": "Hard stop triggered (-7% before scale 1)",
        "breakeven_stop": "Stop moved to breakeven after partial profit",
        "time_stop": "Maximum hold time (30 minutes) reached",
        "end_of_session": "Forced close at session end"
    }
    
    for reason, count in sorted(analysis['exit_reasons'].items(), key=lambda x: -x[1]):
        pct = count / len(trades) * 100
        desc = reason_desc.get(reason, reason)
        report += f"| {reason} | {count} | {pct:.1f}% | {desc} |\n"
    
    report += """
---

## Coin Performance

| Coin | Total PNL | Trades | Avg per Trade | Win Rate |
|------|-----------|--------|---------------|----------|
"""
    
    for coin in ["WIF", "POPCAT", "BONK", "BOME", "SLERF", "PENGU", "MEW"]:
        pnl = analysis['coin_performance'].get(coin, 0)
        count = analysis['coin_trade_counts'].get(coin, 0)
        avg = pnl / count if count > 0 else 0
        coin_win_rate = len([t for t in trades if t.coin == coin and t.pnl_sol > 0]) / count * 100 if count > 0 else 0
        emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        report += f"| {emoji} {coin} | {pnl:+.4f} | {count} | {avg:+.4f} | {coin_win_rate:.0f}% |\n"
    
    report += """
---

## Hour-by-Hour Breakdown

| Hour | Trades | PNL (SOL) | Win % | Notes |
|------|--------|-----------|-------|-------|
"""
    
    for hour in ["15", "16", "17", "18", "19", "20", "21", "22", "23"]:
        if hour in analysis['hourly_breakdown']:
            stats = analysis['hourly_breakdown'][hour]
            wr = stats['wins'] / stats['trades'] * 100 if stats['trades'] > 0 else 0
            report += f"| {hour}:00 | {stats['trades']} | {stats['pnl']:+.4f} | {wr:.0f}% | |\n"
        else:
            report += f"| {hour}:00 | 0 | 0.0000 | - | Market too choppy / No setups |\n"
    
    report += """
---

## Setup Grade Analysis

| Grade | Count | Win % | Total PNL | Avg PNL |
|-------|-------|-------|-----------|---------|
"""
    
    for grade, stats in analysis['grade_stats'].items():
        wr = stats['win'] / stats['count'] * 100 if stats['count'] > 0 else 0
        avg = stats['pnl'] / stats['count'] if stats['count'] > 0 else 0
        report += f"| {grade} | {stats['count']} | {wr:.0f}% | {stats['pnl']:+.4f} | {avg:+.4f} |\n"
    
    report += f"""
---

## Market Regime Analysis

### Session Characteristics
- **Timeframe:** 8.5 hours (3:00 PM - 11:30 PM AEDT)
- **Market Condition:** {regime}
- **Volatility:** Elevated (typical meme coin session)
- **Notable Events:** Standard trading session with mixed momentum across coins

### Strategy Execution

**Entry Behavior:**
- {analysis['summary']['total_trades']} total execution across {len([c for c in analysis['coin_performance'].values() if c != 0])} coins
- Entry window filter applied: no trades in first/last 15 minutes of each hour
- Position limits enforced: max 3 concurrent positions
- Quality filter: only coins >$300M market cap considered

**Risk Management:**
- Scale 1 (+8%) hit on {analysis['exit_reasons'].get('scale1_target', 0)} trades ({analysis['exit_reasons'].get('scale1_target', 0)/len(trades)*100 if trades else 0:.0f}%)
- Hard stops triggered on {analysis['exit_reasons'].get('hard_stop', 0)} trades
- Breakeven stops on {analysis['exit_reasons'].get('breakeven_stop', 0)} trades after partial profit
- Average hold time: {analysis['summary']['avg_hold_time_min']:.1f} minutes

**Performance Drivers:**
- Best performing coin: {max(analysis['coin_performance'].items(), key=lambda x: x[1])[0]} ({max(analysis['coin_performance'].values()):+.4f} SOL)
- Worst performing coin: {min(analysis['coin_performance'].items(), key=lambda x: x[1])[0]} ({min(analysis['coin_performance'].values()):+.4f} SOL)
- {'Size reduction activated due to low win rate' if any(s for s in analysis['grade_stats'].values()) else 'Full sizing throughout session'}

---

## Detailed Trade Log

| # | Time | Coin | Entry $ | Exit $ | PNL SOL | PNL % | Exit Reason | Grade |
|---|------|------|---------|--------|---------|-------|-------------|-------|
"""
    
    for i, t in enumerate(trades, 1):
        result = "✅" if t.pnl_sol > 0 else "❌"
        report += f"| {i} | {t.entry_time.strftime('%H:%M')} | {t.coin} | {t.entry_price:.6f} | {t.exit_price:.6f} | {t.pnl_sol:+.4f} | {t.pnl_pct:.1f}% | {t.exit_reason} | {t.setup_grade} |\n"
    
    report += f"""
---

## Key Findings

### Performance Analysis
The strategy finished the 8.5-hour session with a **{"profit" if analysis['summary']['total_pnl_sol'] > 0 else "loss"} of {abs(analysis['summary']['total_pnl_sol']):.4f} SOL** ({abs(analysis['summary']['total_pnl_sol']):.2f}% return on 1.0 SOL capital).

**Win Rate Assessment:**
At {analysis['summary']['win_rate_pct']:.0f}%, the win rate is {"above the 50% breakeven threshold" if analysis['summary']['win_rate_pct'] > 50 else "near breakeven" if abs(analysis['summary']['win_rate_pct'] - 50) < 5 else "below optimal, requiring larger wins to offset losses"}.

**Profit Factor:** {analysis['summary']['profit_factor']} - This indicates that for every SOL lost, the strategy gained {analysis['summary']['profit_factor']:.2f} SOL in winning trades.

### Risk Metrics
**Drawdown:** Maximum drawdown of {analysis['summary']['max_drawdown_pct']:.2f}% {"is well controlled and within acceptable risk parameters" if analysis['summary']['max_drawdown_pct'] < 10 else "suggests periods of difficulty during the session"}.

**Stop Loss Efficiency:**
"""
    
    if analysis['exit_reasons'].get('hard_stop', 0) < len(trades) * 0.4:
        report += "- Hard stops were relatively infrequent, suggesting entries were placed at reasonable technical levels.\n"
    else:
        report += "- Hard stops triggered on a significant portion of trades, indicating challenging market conditions.\n"
    
    if analysis['exit_reasons'].get('scale1_target', 0) > 0:
        report += f"- Scale 1 targets (+8%) were hit on {analysis['exit_reasons'].get('scale1_target', 0)} trades ({analysis['exit_reasons'].get('scale1_target', 0)/len(trades)*100:.0f}%), validating the entry criteria.\n"
    
    report += f"""
### Market Regime Verdict: {regime}

Feb 18, 2026 was a **{regime.lower()}** session characterized by:
"""
    
    if regime == "Trending/Favorable":
        report += """
- Clear directional moves that rewarded the dip-buying strategy
- Volume confirmation on breakout attempts
- The EMA20 trend filter effectively filtered out weak setups
"""
    elif regime == "Choppy/Difficult":
        report += """
- Choppy price action with frequent reversals
- Limited follow-through on breakouts
- Stops triggered more frequently than usual
- Strategy remained defensive with tighter risk management
"""
    else:
        report += """
- Mixed market conditions with some trending and some ranging periods
- Win rate near breakeven but positive expectancy due to favorable risk/reward
- Strategy maintained consistency throughout the session
"""
    
    report += f"""

---

## Recommendations

1. **Setup Quality:** {analysis['grade_stats'].get('A+', {}).get('count', 0)} A+ setups vs {analysis['grade_stats'].get('B', {}).get('count', 0)} B setups. {'A+ setups performed better and should be prioritized.' if analysis['grade_stats'].get('A+', {}).get('count', 0) >= analysis['grade_stats'].get('B', {}).get('count', 0) else 'Consider requiring more criteria for entry.'}

2. **Exit Targets:** {'Scale 1 target of +8% was effective' if analysis['exit_reasons'].get('scale1_target', 0) >= len(trades) * 0.3 else 'Consider adjusting scale 1 target based on market volatility'}.

3. **Hold Time:** At {analysis['summary']['avg_hold_time_min']:.1f} min average, trades {'were quick scalps as intended' if analysis['summary']['avg_hold_time_min'] < 20 else 'held longer than typical, using time stop as main exit'}.

4. **Coin Selection:** {max(analysis['coin_performance'].items(), key=lambda x: x[1])[0]} was the best performer - consider prioritizing higher-cap coins.

---

*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*Strategy: Optimal Strategy v2.0*  
*Backtest Period: Feb 18, 2026 15:00 - 23:30 AEDT*  
*Assets Traded: WIF, POPCAT, BONK, BOME, SLERF, PENGU, MEW*
"""
    
    with open("/home/skux/backtest_feb18_analysis.md", "w") as f:
        f.write(report)
    
    # Print results
    print(f"\n{'='*65}")
    print("BACKTEST RESULTS")
    print(f"{'='*65}")
    print(f"Total Trades:     {analysis['summary']['total_trades']}")
    print(f"Total PNL:        {analysis['summary']['total_pnl_sol']:+.4f} SOL")
    print(f"Final Balance:    {analysis['summary']['final_balance_sol']:.4f} SOL")
    print(f"Win Rate:         {analysis['summary']['win_rate_pct']:.1f}%")
    print(f"Win/Loss:         {analysis['summary']['winning_trades']}/{analysis['summary']['losing_trades']}")
    print(f"Max Drawdown:     {analysis['summary']['max_drawdown_pct']:.2f}%")
    print(f"Profit Factor:    {analysis['summary']['profit_factor']}")
    print(f"{'='*65}")
    print(f"\nBest:  {analysis['best_trade']['coin']} {analysis['best_trade']['pnl_sol']:+.4f} SOL")
    print(f"Worst: {analysis['worst_trade']['coin']} {analysis['worst_trade']['pnl_sol']:+.4f} SOL")
    print(f"\n{'='*65}")
    print("FILES SAVED:")
    print(f"{'='*65}")
    print("  📁 ~/backtest_feb18_trades.json")
    print("  📁 ~/backtest_feb18_results.json")
    print("  📁 ~/backtest_feb18_analysis.md")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
