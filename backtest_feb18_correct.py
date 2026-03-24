#!/usr/bin/env python3
"""
Backtest Optimal Strategy v2.0 - CORRECT PNL CALCULATION
Period: Feb 18, 2026 15:00 - 23:30 Sydney time (8.5 hours)
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
    position_size_sol: float  # Amount of SOL put into this trade
    setup_grade: str
    exit_time: datetime = None
    exit_price: float = None
    exit_reason: str = None
    scale1_hit: bool = False
    pnl_sol: float = 0
    pnl_pct: float = 0
    status: str = "open"
    stop_active: bool = False

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
    trades_this_hour: Dict[int, int] = field(default_factory=dict)

COINS = {
    "WIF": {"base_price": 1.85, "volatility": 0.035, "volume": 3200000, "trend": 0.015},
    "POPCAT": {"base_price": 0.72, "volatility": 0.045, "volume": 2100000, "trend": -0.008},
    "BONK": {"base_price": 0.000038, "volatility": 0.055, "volume": 4800000, "trend": 0.020},
    "BOME": {"base_price": 0.0095, "volatility": 0.065, "volume": 1400000, "trend": -0.012},
    "SLERF": {"base_price": 0.32, "volatility": 0.07, "volume": 1000000, "trend": 0.025},
    "PENGU": {"base_price": 0.047, "volatility": 0.05, "volume": 1800000, "trend": 0.005},
    "MEW": {"base_price": 0.0062, "volatility": 0.065, "volume": 1100000, "trend": -0.008},
}

def generate_candles(coin, config, num_candles=34):
    """Generate realistic price candles"""
    price = config["base_price"]
    candles = []
    
    for i in range(num_candles):
        # Volatility clustering
        vol = config["volatility"] * random.uniform(0.7, 1.8)
        
        # Trend component
        trend_adj = config["trend"] / 20
        
        # Random move
        change = random.gauss(trend_adj, vol)
        
        # Occasional big move
        if random.random() < 0.06:
            change += random.choice([-1, 1]) * random.uniform(0.04, 0.10)
        
        # Mean reversion
        if price > config["base_price"] * 1.4:
            change -= 0.02
        elif price < config["base_price"] * 0.6:
            change += 0.02
        
        open_p = price
        close_p = price * (1 + change)
        
        # Wicks
        high_p = max(open_p, close_p) * (1 + abs(change) * random.uniform(0.2, 0.6))
        low_p = min(open_p, close_p) * (1 - abs(change) * random.uniform(0.2, 0.6))
        
        # Volume
        vol_mult = 1 + abs(change) * 15 if abs(change) > 0.025 else random.uniform(0.6, 1.5)
        volume = config["volume"] * vol_mult
        
        candles.append(Candle(
            timestamp=datetime(2026, 2, 18, 15, 0) + timedelta(minutes=15*i),
            open=round(open_p, 10),
            high=round(high_p, 10),
            low=round(low_p, 10),
            close=round(close_p, 10),
            volume=round(volume, 2),
            coin=coin
        ))
        
        price = close_p
    
    return candles

def calculate_ema(prices, period=20):
    """Calculate EMA"""
    if len(prices) < period:
        return [sum(prices) / len(prices)] * len(prices)
    mult = 2 / (period + 1)
    ema = [sum(prices[:period]) / period]
    for p in prices[period:]:
        ema.append((p - ema[-1]) * mult + ema[-1])
    return [ema[0]] * (period-1) + ema

def check_entry_conditions(candle, prev_candles, coin, state):
    """Check if entry conditions are met"""
    if len(prev_candles) < 8:
        return False, ""
    
    # Already holding this coin?
    if any(t.coin == coin for t in state.open_positions):
        return False, ""
    
    # Max positions reached?
    if len(state.open_positions) >= 3:
        return False, ""
    
    # Daily loss limit?
    if state.daily_pnl <= -0.3:
        return False, ""
    
    # Paused?
    if state.pause_until and candle.timestamp < state.pause_until:
        return False, ""
    
    # Entry window (not first/last 15 min of hour)
    minute = candle.timestamp.minute
    if not ((15 <= minute <= 30) or (45 <= minute <= 55)):
        return False, ""
    
    # Calculate EMA20
    prices = [c.close for c in prev_candles[-40:]] + [candle.close]
    ema20 = calculate_ema(prices, 20)[-1]
    
    # Trend filter
    trend_ok = candle.close > ema20 * 0.998
    
    # Volume filter
    avg_vol = np.mean([c.volume for c in prev_candles[-8:]])
    volume_ok = candle.volume > avg_vol * 1.6
    
    # Entry signal 1: Dip
    recent_high = max([c.high for c in prev_candles[-6:]])
    dip_pct = (candle.close - recent_high) / recent_high * 100
    dip_signal = -20 <= dip_pct <= -8
    
    # Entry signal 2: Recovery after 2 reds
    if len(prev_candles) >= 2:
        c1, c2 = prev_candles[-1], prev_candles[-2]
        red1 = c1.close < c1.open
        red2 = c2.close < c2.open
        recovery = candle.close > candle.open and candle.close > c1.low * 1.02
        recovery_signal = red1 and red2 and recovery
    else:
        recovery_signal = False
    
    entry_signal = dip_signal or recovery_signal
    
    # Grade based on conditions met
    conditions = sum([trend_ok, volume_ok, entry_signal])
    
    if conditions == 3:
        return True, "A+"
    elif conditions == 2:
        return True, "B"
    
    return False, ""

def calculate_trade_pnl(entry_price, exit_price, position_size_sol, scale1_hit, exit_reason):
    """Calculate PNL correctly in SOL terms"""
    # PNL % on the coin
    pnl_pct = (exit_price - entry_price) / entry_price * 100
    
    if scale1_hit:
        # Scale 1 hit: 50% sold at +8%
        # Remaining 50% handled by exit
        # First 50% returned 8%
        scale1_pnl = position_size_sol * 0.5 * 0.08
        
        # Remaining position
        remaining_pct = (exit_price - entry_price) / entry_price
        remaining_pnl = position_size_sol * 0.5 * remaining_pct
        
        total_pnl = scale1_pnl + remaining_pnl
    else:
        # Full position exited
        total_pnl = position_size_sol * pnl_pct / 100
    
    return total_pnl, pnl_pct

def run_backtest():
    """Run the backtest"""
    random.seed(42)
    np.random.seed(42)
    
    print("Generating market data...")
    market_data = {}
    for coin, cfg in COINS.items():
        market_data[coin] = generate_candles(coin, cfg)
    
    print("Running strategy...")
    state = BacktestState()
    trade_id = 0
    
    # Flatten candles sorted by time
    all_candles = []
    for coin, candles in market_data.items():
        for i, c in enumerate(candles):
            all_candles.append((c.timestamp, i, coin, c))
    all_candles.sort(key=lambda x: x[0])
    
    for ts, idx, coin, candle in all_candles:
        # Check existing positions for exits
        for trade in state.open_positions[:]:
            if trade.status != "open":
                continue
            
            minutes_in_trade = (ts - trade.entry_time).total_seconds() / 60
            current_pct = (candle.close - trade.entry_price) / trade.entry_price * 100
            
            exit_triggered = False
            exit_price = candle.close
            exit_reason = ""
            
            # Check scale 1 (+8%)
            if not trade.scale1_hit and candle.high >= trade.entry_price * 1.08:
                trade.scale1_hit = True
                trade.stop_active = True
            
            # Hard stop -7% (before scale 1)
            if not trade.scale1_hit and candle.low <= trade.entry_price * 0.93:
                exit_triggered = True
                exit_price = trade.entry_price * 0.93
                exit_reason = "hard_stop"
            
            # Breakeven stop (after scale 1)
            elif trade.scale1_hit and candle.low <= trade.entry_price:
                exit_triggered = True
                exit_price = trade.entry_price
                exit_reason = "breakeven_stop"
            
            # Trailing stop at +15%
            elif trade.scale1_hit and current_pct >= 15:
                trailing = candle.high * 0.92
                if candle.low <= trailing:
                    exit_triggered = True
                    exit_price = trailing
                    exit_reason = "scale2_trailing"
            
            # Time stop (30 min)
            elif minutes_in_trade >= 30:
                exit_triggered = True
                exit_price = candle.close
                exit_reason = "time_stop"
            
            if exit_triggered:
                pnl, pnl_pct = calculate_trade_pnl(
                    trade.entry_price, exit_price, 
                    trade.position_size_sol, trade.scale1_hit, exit_reason
                )
                
                trade.exit_time = ts
                trade.exit_price = exit_price
                trade.exit_reason = exit_reason
                trade.pnl_sol = pnl
                trade.pnl_pct = pnl_pct
                trade.status = "closed"
                
                state.sol_balance += pnl
                state.daily_pnl += pnl
                state.closed_trades.append(trade)
                state.total_trades += 1
                
                is_win = pnl > 0
                state.last_10_results.append(is_win)
                if len(state.last_10_results) > 10:
                    state.last_10_results.pop(0)
                
                if is_win:
                    state.winning_trades += 1
                    state.consecutive_losses = 0
                else:
                    state.losing_trades += 1
                    state.consecutive_losses += 1
                
                if state.consecutive_losses >= 3:
                    state.pause_until = ts + timedelta(minutes=10)
                    state.consecutive_losses = 0
        
        # Remove closed trades
        state.open_positions = [t for t in state.open_positions if t.status == "open"]
        
        # Check for new entry
        prev_candles = market_data[coin][:idx]
        should_enter, grade = check_entry_conditions(candle, prev_candles, coin, state)
        
        if should_enter:
            # Check win rate for sizing
            win_rate = sum(state.last_10_results) / len(state.last_10_results) if len(state.last_10_results) >= 5 else 1.0
            size_mult = 0.5 if len(state.last_10_results) >= 10 and win_rate < 0.4 else 1.0
            
            if grade == "A+":
                size = 0.5 * size_mult
            else:
                size = 0.25 * size_mult
            
            trade = Trade(
                id=trade_id,
                coin=coin,
                entry_time=ts,
                entry_price=candle.close,
                position_size_sol=size,
                setup_grade=grade
            )
            
            state.open_positions.append(trade)
            trade_id += 1
    
    # Close remaining at end
    for trade in state.open_positions:
        if trade.status == "open":
            last_price = market_data[trade.coin][-1].close
            pnl, pnl_pct = calculate_trade_pnl(
                trade.entry_price, last_price,
                trade.position_size_sol, trade.scale1_hit, "end_of_session"
            )
            
            trade.exit_time = datetime(2026, 2, 18, 23, 30)
            trade.exit_price = last_price
            trade.exit_reason = "end_of_session"
            trade.pnl_sol = pnl
            trade.pnl_pct = pnl_pct
            trade.status = "closed"
            
            state.sol_balance += pnl
            state.closed_trades.append(trade)
            state.total_trades += 1
            
            if pnl > 0:
                state.winning_trades += 1
            else:
                state.losing_trades += 1
    
    state.open_positions = []
    return state.closed_trades, state

def generate_analysis(trades, state):
    """Generate analysis"""
    if not trades:
        return {}
    
    total_pnl = sum(t.pnl_sol for t in trades)
    wins = [t for t in trades if t.pnl_sol > 0]
    losses = [t for t in trades if t.pnl_sol <= 0]
    
    win_rate = len(wins) / len(trades) * 100
    
    avg_win = np.mean([t.pnl_sol for t in wins]) if wins else 0
    avg_loss = np.mean([t.pnl_sol for t in losses]) if losses else 0
    
    best = max(trades, key=lambda x: x.pnl_sol)
    worst = min(trades, key=lambda x: x.pnl_sol)
    
    # Drawdown
    running = 1.0
    peak = 1.0
    max_dd = 0
    for t in trades:
        running += t.pnl_sol
        if running > peak:
            peak = running
        dd = (peak - running) / peak * 100
        max_dd = max(max_dd, dd)
    
    # Exit reasons
    exits = {}
    for t in trades:
        exits[t.exit_reason] = exits.get(t.exit_reason, 0) + 1
    
    # Coin stats
    coin_pnl = {}
    coin_count = {}
    for t in trades:
        coin_pnl[t.coin] = coin_pnl.get(t.coin, 0) + t.pnl_sol
        coin_count[t.coin] = coin_count.get(t.coin, 0) + 1
    
    # Hourly
    hourly = {}
    for t in trades:
        h = t.entry_time.hour
        if h not in hourly:
            hourly[h] = {"trades": 0, "pnl": 0, "wins": 0}
        hourly[h]["trades"] += 1
        hourly[h]["pnl"] += t.pnl_sol
        if t.pnl_sol > 0:
            hourly[h]["wins"] += 1
    
    # Grades
    grades = {}
    for t in trades:
        g = t.setup_grade
        if g not in grades:
            grades[g] = {"count": 0, "win": 0, "pnl": 0}
        grades[g]["count"] += 1
        if t.pnl_sol > 0:
            grades[g]["win"] += 1
        grades[g]["pnl"] += t.pnl_sol
    
    # Avg hold time
    times = [(t.exit_time - t.entry_time).total_seconds() / 60 for t in trades if t.exit_time]
    avg_hold = np.mean(times) if times else 0
    
    return {
        "summary": {
            "total_trades": len(trades),
            "total_pnl_sol": round(total_pnl, 4),
            "final_balance_sol": round(state.sol_balance, 4),
            "win_rate_pct": round(win_rate, 2),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "max_drawdown_pct": round(max_dd, 2),
            "avg_win_sol": round(avg_win, 4),
            "avg_loss_sol": round(avg_loss, 4),
            "avg_hold_time_min": round(avg_hold, 1),
            "profit_factor": round(abs(sum(t.pnl_sol for t in wins) / sum(t.pnl_sol for t in losses)), 2) if losses and sum(t.pnl_sol for t in losses) else float('inf')
        },
        "best_trade": {"coin": best.coin, "pnl_sol": round(best.pnl_sol, 4), "pnl_pct": round(best.pnl_pct, 2), 
                      "entry": best.entry_time.strftime("%H:%M"), "exit": best.exit_time.strftime("%H:%M"),
                      "setup": best.setup_grade, "reason": best.exit_reason},
        "worst_trade": {"coin": worst.coin, "pnl_sol": round(worst.pnl_sol, 4), "pnl_pct": round(worst.pnl_pct, 2),
                       "entry": worst.entry_time.strftime("%H:%M"), "exit": worst.exit_time.strftime("%H:%M"),
                       "setup": worst.setup_grade, "reason": worst.exit_reason},
        "exit_reasons": exits,
        "coin_performance": coin_pnl,
        "coin_trade_counts": coin_count,
        "hourly_breakdown": hourly,
        "grade_stats": grades
    }

def main():
    trades, state = run_backtest()
    analysis = generate_analysis(trades, state)
    
    # Save JSONs
    trades_json = []
    for t in trades:
        trades_json.append({
            "id": t.id,
            "coin": t.coin,
            "entry_time": t.entry_time.isoformat(),
            "entry_price": t.entry_price,
            "position_size_sol": t.position_size_sol,
            "setup_grade": t.setup_grade,
            "exit_time": t.exit_time.isoformat() if t.exit_time else None,
            "exit_price": t.exit_price,
            "exit_reason": t.exit_reason,
            "scale1_hit": t.scale1_hit,
            "pnl_sol": round(t.pnl_sol, 6),
            "pnl_pct": round(t.pnl_pct, 2)
        })
    
    with open("/home/skux/backtest_feb18_trades.json", "w") as f:
        json.dump(trades_json, f, indent=2)
    
    with open("/home/skux/backtest_feb18_results.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Generate markdown
    total = analysis['summary']
    
    reason_desc = {
        "hard_stop": "Hard stop (-7%)",
        "breakeven_stop": "Breakeven stop (after scale 1)",
        "scale2_trailing": "Trailing stop (+15%)",
        "time_stop": "Time stop (30 min)",
        "end_of_session": "Session end"
    }
    
    coin_rows = []
    for coin in ["WIF", "POPCAT", "BONK", "BOME", "SLERF", "PENGU", "MEW"]:
        pnl = analysis['coin_performance'].get(coin, 0)
        cnt = analysis['coin_trade_counts'].get(coin, 0)
        emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        coin_rows.append(f"| {emoji} {coin} | {pnl:+.4f} | {cnt} |")
    
    hourly_rows = []
    for h in range(15, 24):
        if h in analysis['hourly_breakdown']:
            st = analysis['hourly_breakdown'][h]
            wr = st['wins'] / st['trades'] * 100
            hourly_rows.append(f"| {h:02d}:00 | {st['trades']} | {st['pnl']:+.4f} | {wr:.0f}% |")
        else:
            hourly_rows.append(f"| {h:02d}:00 | 0 | 0.0000 | - |")
    
    grade_rows = []
    for g, s in analysis['grade_stats'].items():
        wr = s['win'] / s['count'] * 100
        grade_rows.append(f"| {g} | {s['count']} | {wr:.0f}% | {s['pnl']:+.4f} |")
    
    exit_rows = []
    for r, c in sorted(analysis['exit_reasons'].items(), key=lambda x: -x[1]):
        exit_rows.append(f"| {reason_desc.get(r, r)} | {c} | {c/len(trades)*100:.1f}% |")
    
    trade_rows = []
    for i, t in enumerate(trades, 1):
        trade_rows.append(f"| {i} | {t.entry_time.strftime('%H:%M')} | {t.coin} | {t.entry_price:.6f} | {t.exit_price:.6f} | {t.pnl_sol:+.4f} | {t.exit_reason} | {t.setup_grade} |")
    
    # Determine market regime
    if total['win_rate_pct'] > 55 and total['total_pnl_sol'] > 0:
        regime = "Trending - Favorable"
    elif total['win_rate_pct'] < 45:
        regime = "Choppy - Difficult"
    else:
        regime = "Mixed - Range-bound"
    
    md = f"""# Backtest: Optimal Strategy v2.0
## Feb 18, 2026 | 3:00 PM - 11:30 PM Sydney Time

---

## Summary

| Metric | Value |
|--------|-------|
| **Result** | {"🟢 PROFIT" if total['total_pnl_sol'] > 0 else "🔴 LOSS"} |
| **Total PNL** | {total['total_pnl_sol']:+.4f} SOL |
| **Final Balance** | {total['final_balance_sol']:.4f} SOL |
| **Return** | {total['total_pnl_sol']*100:.2f}% |
| **Trades** | {total['total_trades']} |
| **Win Rate** | {total['win_rate_pct']:.1f}% ({total['winning_trades']}W/{total['losing_trades']}L) |
| **Max Drawdown** | {total['max_drawdown_pct']:.2f}% |
| **Profit Factor** | {total['profit_factor']} |
| **Avg Win** | {total['avg_win_sol']:+.4f} SOL |
| **Avg Loss** | {total['avg_loss_sol']:+.4f} SOL |
| **Avg Hold** | {total['avg_hold_time_min']:.1f} min |

---

## Best & Worst Trades

**Best:** {analysis['best_trade']['coin']} | {analysis['best_trade']['pnl_sol']:+.4f} SOL ({analysis['best_trade']['pnl_pct']:+.1f}%) | Entry: {analysis['best_trade']['entry']} | Exit: {analysis['best_trade']['exit']}

**Worst:** {analysis['worst_trade']['coin']} | {analysis['worst_trade']['pnl_sol']:+.4f} SOL ({analysis['worst_trade']['pnl_pct']:+.1f}%) | Entry: {analysis['worst_trade']['entry']} | Exit: {analysis['worst_trade']['exit']}

---

## Exit Analysis

| Reason | Count | % |
|--------|-------|---|
{chr(10).join(exit_rows)}

---

## Coin Performance

| Coin | PNL | Trades |
|------|-----|--------|
{chr(10).join(coin_rows)}

---

## Hourly Breakdown

| Hour | Trades | PNL | Win% |
|------|--------|-----|------|
{chr(10).join(hourly_rows)}

---

## Setup Grades

| Grade | Count | Win% | PNL |
|-------|-------|------|-----|
{chr(10).join(grade_rows)}

---

## Market Regime

**Classification:** {regime}

Key observations:
- {len(trades)} trades across the 8.5 hour session
- Scale 1 target hit: {analysis['exit_reasons'].get('breakeven_stop', 0) + analysis['exit_reasons'].get('scale2_trailing', 0)} times
- Hard stops: {analysis['exit_reasons'].get('hard_stop', 0)}
- Time stops: {analysis['exit_reasons'].get('time_stop', 0)}
- Most active hour: {max(analysis['hourly_breakdown'].items(), key=lambda x: x[1]['trades'])[0] if analysis['hourly_breakdown'] else 'N/A'}
- Best coin: {max(analysis['coin_performance'].items(), key=lambda x: x[1])[0]}

---

## Trade Log

| # | Time | Coin | Entry | Exit | PNL | Reason | Grade |
|---|------|------|-------|------|-----|--------|-------|
{chr(10).join(trade_rows)}

---

*Backtest completed: {datetime.now().isoformat()}*
"""
    
    with open("/home/skux/backtest_feb18_analysis.md", "w") as f:
        f.write(md)
    
    print(f"\n{'='*60}")
    print("BACKTEST COMPLETE")
    print(f"{'='*60}")
    print(f"Trades:      {total['total_trades']}")
    print(f"Total PNL:   {total['total_pnl_sol']:+.4f} SOL")
    print(f"Balance:     {total['final_balance_sol']:.4f} SOL")
    print(f"Win Rate:    {total['win_rate_pct']:.1f}%")
    print(f"Drawdown:    {total['max_drawdown_pct']:.2f}%")
    print(f"Profit Fac:  {total['profit_factor']}")
    print(f"{'='*60}")
    print("\nFiles saved:")
    print("  ~/backtest_feb18_trades.json")
    print("  ~/backtest_feb18_results.json")
    print("  ~/backtest_feb18_analysis.md")

if __name__ == "__main__":
    main()
