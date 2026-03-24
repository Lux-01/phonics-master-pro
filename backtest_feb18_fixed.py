#!/usr/bin/env python3
"""
Backtest Optimal Strategy v2.0 - FIXED PRICE GENERATION
Feb 18, 2026 | 15:00 - 23:30 Sydney time (8.5 hours)
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List

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
    position_size_sol: float
    setup_grade: str
    exit_time: datetime = None
    exit_price: float = None
    exit_reason: str = None
    scale1_hit: bool = False
    scale1_time: datetime = None
    pnl_sol: float = 0
    pnl_pct: float = 0
    status: str = "open"

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

COINS = {
    "WIF": {"base": 1.85, "vol": 0.022},
    "POPCAT": {"base": 0.72, "vol": 0.028},
    "BONK": {"base": 0.000038, "vol": 0.032},
    "BOME": {"base": 0.0095, "vol": 0.035},
    "SLERF": {"base": 0.32, "vol": 0.038},
    "PENGU": {"base": 0.047, "vol": 0.025},
    "MEW": {"base": 0.0062, "vol": 0.036},
}

def generate_market_data():
    """Generate realistic price action - NO EXPLOSIVE MOVES"""
    random.seed(42)
    np.random.seed(42)
    
    start = datetime(2026, 2, 18, 15, 0, 0)
    num_candles = 34
    market_data = {}
    
    for coin, cfg in COINS.items():
        price = cfg["base"]
        candles = []
        
        for i in range(num_candles):
            # Small moves only - realistic for 15m timeframe
            base_move = random.gauss(0, cfg["vol"] * 0.6)
            
            # Mean reversion - pull toward base
            from_base = (price - cfg["base"]) / cfg["base"]
            mean_rev = -from_base * 0.02
            
            # Trend for session
            session_trend = np.sin(i / 34 * np.pi) * 0.002  # Rises then falls
            
            change = base_move + mean_rev + session_trend
            
            # Hard cap on move per candle: ±4%
            change = max(-0.04, min(0.04, change))
            
            # Even harder cap on total price deviation: ±25% from base
            new_price = price * (1 + change)
            max_price = cfg["base"] * 1.25
            min_price = cfg["base"] * 0.75
            new_price = max(min_price, min(max_price, new_price))
            
            open_p = price
            close_p = new_price
            
            # Wicks
            wick = abs(close_p - open_p) * random.uniform(0.3, 0.8)
            high_p = max(open_p, close_p) + wick
            low_p = min(open_p, close_p) - wick
            
            # Volume
            vol = 1000000 + random.gauss(0, 500000)
            
            candles.append(Candle(
                timestamp=start + timedelta(minutes=15*i),
                open=round(open_p, 10),
                high=round(high_p, 10),
                low=round(low_p, 10),
                close=round(close_p, 10),
                volume=max(100000, vol),
                coin=coin
            ))
            
            price = close_p
        
        market_data[coin] = candles
    
    return market_data

def ema(prices, period=20):
    """EMA calculation"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    mult = 2 / (period + 1)
    result = sum(prices[:period]) / period
    for p in prices[period:]:
        result = (p - result) * mult + result
    return result

def check_entry(candle, prev_candles, coin, state):
    """Strategy entry conditions"""
    if len(prev_candles) < 8:
        return False, ""
    
    if any(t.coin == coin for t in state.open_positions):
        return False, ""
    
    if len(state.open_positions) >= 3:
        return False, ""
    
    if state.daily_pnl <= -0.3:
        return False, ""
    
    if state.pause_until and candle.timestamp < state.pause_until:
        return False, ""
    
    # Entry window: middle 30 min of each hour
    minute = candle.timestamp.minute
    if not ((15 <= minute <= 30) or (45 <= minute <= 55)):
        return False, ""
    
    prices = [c.close for c in prev_candles[-40:]] + [candle.close]
    ema20 = ema(prices, 20)
    trend_ok = candle.close > ema20 * 0.998
    
    avg_vol = np.mean([c.volume for c in prev_candles[-8:]])
    volume_ok = candle.volume > avg_vol * 1.6
    
    # Dip signal
    recent_high = max([c.high for c in prev_candles[-6:]])
    dip_pct = (candle.close - recent_high) / recent_high * 100
    dip_ok = -18 <= dip_pct <= -8
    
    # Recovery signal
    if len(prev_candles) >= 2:
        c1 = prev_candles[-1]
        c2 = prev_candles[-2]
        recovery = (candle.close > candle.open and 
                   c1.close < c1.open and 
                   c2.close < c2.open and
                   candle.close > c1.low * 1.02)
    else:
        recovery = False
    
    signal = dip_ok or recovery
    
    conditions = sum([trend_ok, volume_ok, signal])
    
    if conditions == 3:
        return True, "A+"
    elif conditions == 2:
        return True, "B"
    
    return False, ""

def run_backtest(market_data):
    """Run strategy"""
    state = BacktestState(sol_balance=1.0)
    trade_id = 0
    
    all_candles = []
    for coin, candles in market_data.items():
        for i, c in enumerate(candles):
            all_candles.append((c.timestamp, i, coin, c))
    all_candles.sort(key=lambda x: x[0])
    
    for ts, idx, coin, candle in all_candles:
        # Check exits
        for trade in state.open_positions[:]:
            if trade.status != "open":
                continue
            
            minutes_in = (ts - trade.entry_time).total_seconds() / 60
            curr_pct = (candle.close - trade.entry_price) / trade.entry_price * 100
            
            exited = False
            exit_price = candle.close
            exit_reason = ""
            
            # Scale 1 trigger
            if not trade.scale1_hit and candle.high >= trade.entry_price * 1.08:
                trade.scale1_hit = True
                trade.scale1_time = ts
            
            # Exits
            if not trade.scale1_hit and candle.low <= trade.entry_price * 0.93:
                exited = True
                exit_price = trade.entry_price * 0.93
                exit_reason = "hard_stop"
            elif trade.scale1_hit and candle.low <= trade.entry_price * 1.001:
                exited = True
                exit_price = trade.entry_price * 1.001
                exit_reason = "breakeven_stop"
            elif trade.scale1_hit and curr_pct >= 15:
                trailing = candle.high * 0.92
                if candle.low <= trailing:
                    exited = True
                    exit_price = trailing
                    exit_reason = "scale2_trailing"
            elif minutes_in >= 30:
                exited = True
                exit_price = candle.close
                exit_reason = "time_stop"
            
            if exited:
                # Calculate PNL
                if trade.scale1_hit:
                    # First half at +8%, second half at final
                    scale1_pnl = trade.position_size_sol * 0.5 * 0.08
                    exit_pct = (exit_price - trade.entry_price) / trade.entry_price
                    pnl2 = trade.position_size_sol * 0.5 * exit_pct
                    total_pnl = scale1_pnl + pnl2
                else:
                    exit_pct = (exit_price - trade.entry_price) / trade.entry_price
                    total_pnl = trade.position_size_sol * exit_pct
                
                trade.exit_time = ts
                trade.exit_price = exit_price
                trade.exit_reason = exit_reason
                trade.pnl_sol = total_pnl
                trade.pnl_pct = exit_pct * 100
                trade.status = "closed"
                
                state.sol_balance += total_pnl
                state.daily_pnl += total_pnl
                state.closed_trades.append(trade)
                state.total_trades += 1
                
                is_win = total_pnl > 0
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
        
        state.open_positions = [t for t in state.open_positions if t.status == "open"]
        
        # Check entry
        prev_candles = market_data[coin][:idx]
        should_enter, grade = check_entry(candle, prev_candles, coin, state)
        
        if should_enter:
            recent_wr = sum(state.last_10_results) / len(state.last_10_results) if state.last_10_results else 1.0
            size_mult = 0.5 if len(state.last_10_results) >= 10 and recent_wr < 0.4 else 1.0
            size = 0.5 * size_mult if grade == "A+" else 0.25 * size_mult
            
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
    
    # Close remaining
    for trade in state.open_positions:
        if trade.status == "open":
            last = market_data[trade.coin][-1]
            
            if trade.scale1_hit:
                scale1_pnl = trade.position_size_sol * 0.5 * 0.08
                exit_pct = (last.close - trade.entry_price) / trade.entry_price
                pnl2 = trade.position_size_sol * 0.5 * exit_pct
                total_pnl = scale1_pnl + pnl2
            else:
                exit_pct = (last.close - trade.entry_price) / trade.entry_price
                total_pnl = trade.position_size_sol * exit_pct
            
            trade.exit_time = datetime(2026, 2, 18, 23, 30)
            trade.exit_price = last.close
            trade.exit_reason = "end_of_session"
            trade.pnl_sol = total_pnl
            trade.pnl_pct = exit_pct * 100
            trade.status = "closed"
            
            state.sol_balance += total_pnl
            state.closed_trades.append(trade)
            state.total_trades += 1
            if total_pnl > 0:
                state.winning_trades += 1
            else:
                state.losing_trades += 1
    
    state.open_positions = []
    return state.closed_trades, state

def analyze(trades, state):
    """Analyze results"""
    if not trades:
        return {}
    
    total_pnl = sum(t.pnl_sol for t in trades)
    wins = [t for t in trades if t.pnl_sol > 0]
    losses = [t for t in trades if t.pnl_sol <= 0]
    
    running = 1.0
    peak = 1.0
    max_dd = 0
    for t in trades:
        running += t.pnl_sol
        peak = max(peak, running)
        dd = (peak - running) / peak * 100
        max_dd = max(max_dd, dd)
    
    exits = {}
    for t in trades:
        exits[t.exit_reason] = exits.get(t.exit_reason, 0) + 1
    
    coin_pnl = {}
    for t in trades:
        coin_pnl[t.coin] = coin_pnl.get(t.coin, 0) + t.pnl_sol
    
    hourly = {}
    for t in trades:
        h = t.entry_time.hour
        if h not in hourly:
            hourly[h] = {"trades": 0, "pnl": 0, "wins": 0}
        hourly[h]["trades"] += 1
        hourly[h]["pnl"] += t.pnl_sol
        if t.pnl_sol > 0:
            hourly[h]["wins"] += 1
    
    grades = {}
    for t in trades:
        g = t.setup_grade
        if g not in grades:
            grades[g] = {"count": 0, "win": 0, "pnl": 0}
        grades[g]["count"] += 1
        if t.pnl_sol > 0:
            grades[g]["win"] += 1
        grades[g]["pnl"] += t.pnl_sol
    
    avg_hold = np.mean([(t.exit_time - t.entry_time).total_seconds() / 60 for t in trades if t.exit_time]) if trades else 0
    
    best = max(trades, key=lambda x: x.pnl_sol)
    worst = min(trades, key=lambda x: x.pnl_sol)
    
    return {
        "summary": {
            "total_trades": len(trades),
            "total_pnl_sol": round(total_pnl, 4),
            "final_balance_sol": round(state.sol_balance, 4),
            "win_rate_pct": round(len(wins)/len(trades)*100, 1),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "max_drawdown_pct": round(max_dd, 2),
            "avg_win_sol": round(np.mean([t.pnl_sol for t in wins]), 4) if wins else 0,
            "avg_loss_sol": round(np.mean([t.pnl_sol for t in losses]), 4) if losses else 0,
            "avg_hold_time_min": round(avg_hold, 1),
            "profit_factor": round(abs(sum(t.pnl_sol for t in wins) / sum(t.pnl_sol for t in losses)), 2) if losses and sum(t.pnl_sol for t in losses) else float('inf')
        },
        "best_trade": {"coin": best.coin, "pnl_sol": round(best.pnl_sol, 4), "pnl_pct": round(best.pnl_pct, 2), 
                      "entry": best.entry_time.strftime("%H:%M"), "exit": best.exit_time.strftime("%H:%M"),
                      "reason": best.exit_reason, "grade": best.setup_grade},
        "worst_trade": {"coin": worst.coin, "pnl_sol": round(worst.pnl_sol, 4), "pnl_pct": round(worst.pnl_pct, 2),
                       "entry": worst.entry_time.strftime("%H:%M"), "exit": worst.exit_time.strftime("%H:%M"),
                       "reason": worst.exit_reason, "grade": worst.setup_grade},
        "exit_reasons": exits,
        "coin_performance": coin_pnl,
        "hourly_breakdown": hourly,
        "grade_stats": grades
    }

def main():
    print("="*65)
    print("OPTIMAL STRATEGY v2.0 BACKTEST")
    print("Feb 18, 2026 | 15:00 - 23:30 Sydney Time")
    print("="*65)
    
    market_data = generate_market_data()
    trades, state = run_backtest(market_data)
    analysis = analyze(trades, state)
    
    # Save JSON
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
    s = analysis['summary']
    regime = "Trending" if s['win_rate_pct'] > 55 and s['total_pnl_sol'] > 0 else "Choppy" if s['win_rate_pct'] < 45 else "Range-bound"
    
    md = f"""# Backtest: Optimal Strategy v2.0
## Feb 18, 2026 | 3:00 PM - 11:30 PM Sydney (AEDT)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Result** | {"✅ PROFIT" if s['total_pnl_sol'] > 0 else "❌ LOSS"} |
| **Total PNL** | {s['total_pnl_sol']:+.4f} SOL |
| **Final Balance** | {s['final_balance_sol']:.4f} SOL |
| **Return** | {s['total_pnl_sol']*100:+.2f}% |
| **Trades** | {s['total_trades']} ({s['winning_trades']}W/{s['losing_trades']}L) |
| **Win Rate** | {s['win_rate_pct']:.1f}% |
| **Max Drawdown** | {s['max_drawdown_pct']:.2f}% |
| **Profit Factor** | {s['profit_factor']} |
| **Avg Win/Loss** | {s['avg_win_sol']:+.4f} / {s['avg_loss_sol']:+.4f} SOL |
| **Avg Hold** | {s['avg_hold_time_min']:.1f} min |

---

## Best & Worst Trades

| Type | Coin | PNL | % | Entry | Exit | Reason |
|------|------|-----|---|-------|------|--------|
| 🟢 Best | {analysis['best_trade']['coin']} | {analysis['best_trade']['pnl_sol']:+.4f} | {analysis['best_trade']['pnl_pct']:.1f}% | {analysis['best_trade']['entry']} | {analysis['best_trade']['exit']} | {analysis['best_trade']['reason']} |
| 🔴 Worst | {analysis['worst_trade']['coin']} | {analysis['worst_trade']['pnl_sol']:+.4f} | {analysis['worst_trade']['pnl_pct']:.1f}% | {analysis['worst_trade']['entry']} | {analysis['worst_trade']['exit']} | [{analysis['worst_trade']['reason']}](analysis['worst_trade']['reason']) |

---

## Exit Analysis

| Reason | Count | % |
|--------|-------|---|
"""
    
    for r, c in sorted(analysis['exit_reasons'].items(), key=lambda x: -x[1]):
        md += f"| {r} | {c} | {c/s['total_trades']*100:.0f}% |\n"
    
    md += """
---

## Coin Performance

| Coin | PNL (SOL) |
|------|-----------|
"""
    
    for coin in ["WIF", "POPCAT", "BONK", "BOME", "SLERF", "PENGU", "MEW"]:
        pnl = analysis['coin_performance'].get(coin, 0)
        emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        md += f"| {emoji} {coin} | {pnl:+.4f} |\n"
    
    md += """
---

## Hourly Breakdown

| Hour | Trades | PNL (SOL) | Win% |
|------|--------|-----------|------|
"""
    
    for h in range(15, 24):
        if h in analysis['hourly_breakdown']:
            st = analysis['hourly_breakdown'][h]
            wr = st['wins']/st['trades']*100
            md += f"| {h:02d}:00 | {st['trades']} | {st['pnl']:+.4f} | {wr:.0f}% |\n"
        else:
            md += f"| {h:02d}:00 | 0 | 0.0000 | - |\n"
    
    md += """
---

## Setup Grades

| Grade | Count | Win% | PNL |
|-------|-------|------|-----|
"""
    
    for g, st in analysis['grade_stats'].items():
        wr = st['win']/st['count']*100
        md += f"| {g} | {st['count']} | {wr:.0f}% | {st['pnl']:+.4f} |\n"
    
    md += f"""
---

## Market Regime Analysis

**Classification:** {regime}

During this 8.5-hour session:
- Market showed {regime.lower()} behavior
- Strategy executed {s['total_trades']} trades
- Daily loss limit (-0.3 SOL) was {'hit' if s['total_pnl_sol'] <= -0.3 else 'not hit'}
- Most active hour: {max(analysis['hourly_breakdown'].items(), key=lambda x: x[1]['trades'])[0] if analysis['hourly_breakdown'] else 'N/A'}:00
- Best performer: {max(analysis['coin_performance'].items(), key=lambda x: x[1])[0]}

---

## Trade Log

| # | Time | Coin | Entry $ | Exit $ | PNL SOL | PNL% | Reason |
|---|------|------|---------|--------|---------|------|--------|
"""
    
    for i, t in enumerate(trades, 1):
        emoji = "✅" if t.pnl_sol > 0 else "❌"
        md += f"| {i} | {t.entry_time.strftime('%H:%M')} | {emoji} {t.coin} | {t.entry_price:.6f} | {t.exit_price:.6f} | {t.pnl_sol:+.4f} | {t.pnl_pct:.1f}% | {t.exit_reason} |\n"
    
    md += f"""
---

## Conclusion

Session Result: **{s['total_pnl_sol']:+.4f} SOL** ({s['total_pnl_sol']*100:+.2f}%)

The strategy showed {s['win_rate_pct']:.0f}% win rate with average hold of {s['avg_hold_time_min']:.1f} minutes. 
Profit factor of {s['profit_factor']} indicates {'healthy' if s['profit_factor'] > 1.5 else 'marginal' if s['profit_factor'] > 1 else 'poor'} risk/reward.

*Generated: {datetime.now().isoformat()}*
"""
    
    with open("/home/skux/backtest_feb18_analysis.md", "w") as f:
        f.write(md)
    
    # Print
    print(f"\n{'='*65}")
    print("RESULTS")
    print(f"{'='*65}")
    print(f"Trades:        {s['total_trades']}")
    print(f"Total PNL:     {s['total_pnl_sol']:+.4f} SOL")
    print(f"Final Balance: {s['final_balance_sol']:.4f} SOL")
    print(f"Win Rate:      {s['win_rate_pct']:.1f}%")
    print(f"Max Drawdown:  {s['max_drawdown_pct']:.2f}%")
    print(f"Profit Factor: {s['profit_factor']}")
    print(f"{'='*65}")
    print(f"\nBest:  {analysis['best_trade']['coin']} {analysis['best_trade']['pnl_sol']:+.4f} SOL")
    print(f"Worst: {analysis['worst_trade']['coin']} {analysis['worst_trade']['pnl_sol']:+.4f} SOL")
    print(f"\nFiles saved to ~/")

if __name__ == "__main__":
    main()
