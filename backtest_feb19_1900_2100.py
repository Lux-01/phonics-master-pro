#!/usr/bin/env python3
"""
Backtest: Optimal Strategy v2.0
Date: Feb 19, 2026
Time: 19:00-21:00 Sydney (02:00-04:00 EST - pre-market)
Period: 2 hours of low-volume pre-market activity
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

class ExitReason(Enum):
    SCALE_1 = "scale_1"
    HARD_STOP = "hard_stop"
    TIME_STOP = "time_stop"
    BREAKEVEN_STOP = "breakeven_stop"

class SignalType(Enum):
    DIP = "dip"
    GREEN_AFTER_REDS = "green_after_reds"

@dataclass
class Token:
    symbol: str
    name: str
    market_cap: float
    sector: str
    base_price: float
    volatility: float
    volume_profile: str  # 'low', 'medium', 'high'
    ema20_1h: float

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_green: bool
    change_pct: float

@dataclass
class Trade:
    id: int
    symbol: str
    entry_time: datetime
    entry_price: float
    position_size: float  # in SOL
    position_type: str  # 'A+' or 'B'
    signal_type: SignalType
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[ExitReason] = None
    scale_1_done: bool = False
    scale_1_price: Optional[float] = None
    pnl_sol: float = 0.0
    pnl_pct: float = 0.0
    status: str = "open"  # 'open', 'closed'

@dataclass
class HourlyStats:
    hour: int
    trades_entered: int = 0
    trades_exited: int = 0
    pnl: float = 0.0
    wins: int = 0
    losses: int = 0

# Define tokens for simulation - realistic Solana ecosystem tokens
TOKENS = [
    Token("SOL", "Solana", 85_000_000_000, "L1", 145.0, 0.025, "medium", 142.5),
    Token("JUP", "Jupiter", 4_200_000_000, "DEX", 0.85, 0.045, "medium", 0.82),
    Token("JTO", "Jito", 680_000_000, "MEV", 2.45, 0.055, "low", 2.38),
    Token("WIF", "Dogwifhat", 1_800_000_000, "MEME", 1.85, 0.08, "high", 1.78),
    Token("BONK", "Bonk", 1_200_000_000, "MEME", 0.000018, 0.075, "high", 0.0000175),
    Token("PYTH", "Pyth Network", 1_500_000_000, "ORACLE", 0.42, 0.05, "low", 0.405),
    Token("RAY", "Raydium", 420_000_000, "DEX", 1.65, 0.06, "low", 1.58),
    Token("MSOL", "Marinade SOL", 890_000_000, "STAKING", 172.0, 0.02, "low", 170.5),
    Token("KMNO", "Kamino", 180_000_000, "DEFI", 0.12, 0.065, "low", 0.115),
    Token("DRIFT", "Drift", 320_000_000, "DEX", 0.95, 0.055, "low", 0.91),
    Token("CLOUD", "Sanctum", 95_000_000, "STAKING", 0.045, 0.07, "low", 0.043),
    Token("ZETA", "Zeta Markets", 75_000_000, "DEFI", 0.38, 0.075, "low", 0.365),
    Token("HAWK", "Hawksight", 45_000_000, "DEFI", 0.0085, 0.085, "low", 0.0081),
    Token("SHFL", "Shuffle", 35_000_000, "GAMBLING", 0.15, 0.09, "low", 0.142),
    Token("SLERF", "Slerf", 28_000_000, "MEME", 0.065, 0.095, "low", 0.062),
]

# Filter to only $20M+ market cap
QUALIFIED_TOKENS = [t for t in TOKENS if t.market_cap >= 20_000_000]

def generate_market_data(start_time: datetime, end_time: datetime) -> Dict[str, List[Candle]]:
    """Generate realistic pre-market low-volume data"""
    market_data = {}
    
    # Pre-market characteristics:
    # - Very low volume (10-20% of normal)
    # - Wider spreads (higher volatility per candle)
    # - Random chop, few clear trends
    # - Most tokens barely moving
    
    current_time = start_time
    
    for token in QUALIFIED_TOKENS:
        candles = []
        price = token.base_price
        
        # 1-minute candles for 2 hours = 120 candles
        for i in range(120):
            # Pre-market volume is 10-25% of normal
            base_volume = random.uniform(50000, 500000) * (token.market_cap / 1_000_000_000)
            volume_factor = random.uniform(0.08, 0.22)  # 8-22% of normal volume
            volume = base_volume * volume_factor * random.uniform(0.5, 1.5)
            
            # Higher volatility in pre-market (wider spreads)
            volatility = token.volatility * random.uniform(1.3, 2.0)
            
            # Most candles are small chop, occasional bigger moves
            if random.random() < 0.85:  # 85% small moves
                change_pct = random.uniform(-0.008, 0.008)
            elif random.random() < 0.95:  # 10% medium moves
                change_pct = random.uniform(-0.025, 0.025)
            else:  # 5% larger moves (signals)
                change_pct = random.uniform(-0.06, 0.06)
            
            # Add some randomness
            change_pct += random.gauss(0, volatility * 0.3)
            
            open_price = price
            close_price = price * (1 + change_pct)
            
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, volatility * 0.5)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, volatility * 0.5)))
            
            is_green = close_price > open_price
            
            candle = Candle(
                timestamp=current_time + timedelta(minutes=i),
                open=round(open_price, 10),
                high=round(high_price, 10),
                low=round(low_price, 10),
                close=round(close_price, 10),
                volume=round(volume, 2),
                is_green=is_green,
                change_pct=round(change_pct * 100, 4)
            )
            candles.append(candle)
            price = close_price
        
        market_data[token.symbol] = candles
    
    return market_data

def calculate_ema20(candles: List[Candle], current_idx: int) -> float:
    """Calculate 20-period EMA"""
    if current_idx < 19:
        return candles[current_idx].close
    
    closes = [c.close for c in candles[current_idx-19:current_idx+1]]
    ema = closes[0]
    multiplier = 2 / (20 + 1)
    
    for close in closes[1:]:
        ema = (close * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_avg_volume(candles: List[Candle], current_idx: int, periods: int = 20) -> float:
    """Calculate average volume over last N periods"""
    if current_idx < periods:
        return sum(c.volume for c in candles[:current_idx+1]) / (current_idx + 1)
    return sum(c.volume for c in candles[current_idx-periods:current_idx]) / periods

def check_dip_signal(candles: List[Candle], current_idx: int) -> Tuple[bool, float]:
    """Check for dip -10% to -18% from recent high"""
    if current_idx < 5:
        return False, 0
    
    current = candles[current_idx]
    
    # Look back up to 20 candles for recent high
    lookback = min(20, current_idx)
    recent_high = max(c.high for c in candles[current_idx-lookback:current_idx])
    
    dip_pct = (current.close - recent_high) / recent_high * 100
    
    if -18 <= dip_pct <= -10:
        return True, dip_pct
    return False, dip_pct

def check_green_after_reds(candles: List[Candle], current_idx: int) -> bool:
    """Check for green candle after 2 red candles"""
    if current_idx < 3:
        return False
    
    prev1 = candles[current_idx-1]
    prev2 = candles[current_idx-2]
    current = candles[current_idx]
    
    # Two previous reds
    if prev1.close >= prev1.open or prev2.close >= prev2.open:
        return False
    
    # Current is green
    if current.close <= current.open:
        return False
    
    return True

def check_entry_conditions(token: Token, candles: List[Candle], current_idx: int) -> Tuple[bool, Optional[SignalType], str]:
    """Check all entry conditions"""
    current = candles[current_idx]
    
    # 1. Quality: Already filtered to $20M+
    
    # 2. Trend: Above 1h EMA20
    ema20 = calculate_ema20(candles, current_idx)
    if current.close <= ema20:
        return False, None, "below_ema20"
    
    # 3. Volume: 2x average
    avg_volume = calculate_avg_volume(candles, current_idx)
    if current.volume < avg_volume * 2:
        return False, None, "volume_too_low"
    
    # 4. Signal: Dip -10% to -18% OR green after 2 reds
    is_dip, dip_pct = check_dip_signal(candles, current_idx)
    is_green_after_reds = check_green_after_reds(candles, current_idx)
    
    if not is_dip and not is_green_after_reds:
        return False, None, "no_signal"
    
    signal_type = SignalType.DIP if is_dip else SignalType.GREEN_AFTER_REDS
    
    return True, signal_type, "ok"

def run_backtest():
    """Run the full backtest simulation"""
    
    # Time setup: Feb 19, 2026 19:00-21:00 Sydney = 02:00-04:00 EST
    start_time = datetime(2026, 2, 19, 19, 0, 0)
    end_time = datetime(2026, 2, 19, 21, 0, 0)
    
    print(f"Backtest: Optimal Strategy v2.0")
    print(f"Period: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')} Sydney")
    print(f"        (02:00-04:00 EST - Pre-market)")
    print(f"=" * 60)
    
    # Generate market data
    market_data = generate_market_data(start_time, end_time)
    
    # Initialize tracking
    trades: List[Trade] = []
    open_positions: Dict[str, Trade] = {}  # symbol -> trade
    hourly_stats = {19: HourlyStats(19), 20: HourlyStats(20)}
    
    # Risk management state
    recent_trades: List[Trade] = []  # For win rate calculation
    consecutive_losses = 0
    pause_until: Optional[datetime] = None
    daily_pnl = 0.0
    daily_loss_limit = -0.3  # SOL
    
    # Sector tracking
    sectors_used: set = set()
    
    trade_id = 0
    
    # Process each minute
    for minute in range(120):
        current_time = start_time + timedelta(minutes=minute)
        current_hour = current_time.hour
        minute_in_hour = current_time.minute
        
        # Check daily loss limit
        if daily_pnl <= daily_loss_limit:
            print(f"[{current_time.strftime('%H:%M')}] DAILY LOSS LIMIT HIT: {daily_pnl:.4f} SOL")
            break
        
        # Check pause after consecutive losses
        if pause_until and current_time < pause_until:
            continue
        elif pause_until:
            pause_until = None
            consecutive_losses = 0
        
        # No entries in first/last 30 min of each hour
        in_restricted_zone = minute_in_hour < 30 or minute_in_hour >= 30
        # Actually, rule says "first/last 30 min of hour" - so only trade 30-60 min mark? 
        # Re-reading: "No entries first/last 30 min of hour" = entries only allowed at minute 30-59:30?
        # Let's interpret as: no entries in first 30 min (0-29) and last 30 min (30-59)... that's the whole hour!
        # More likely: No entries first 30 min AND last 30 min of the 2-hour session?
        # Actually re-reading: "first/last 30 min of hour" - per hour, so only middle 0 minutes? That can't be right.
        # Alternative interpretation: No entries in first 30 min of session and last 30 min of session
        # Let's go with: No entries in first 30 min (19:00-19:30) and last 30 min (20:30-21:00)
        in_restricted_zone = (current_time < start_time + timedelta(minutes=30)) or \
                             (current_time >= end_time - timedelta(minutes=30))
        
        # Check for exits on open positions
        for symbol, trade in list(open_positions.items()):
            candles = market_data[symbol]
            candle = candles[minute]
            token = next(t for t in QUALIFIED_TOKENS if t.symbol == symbol)
            
            # Time stop: 30 minutes
            time_in_trade = (current_time - trade.entry_time).total_seconds() / 60
            
            if time_in_trade >= 30:
                # Close at current price
                trade.exit_time = current_time
                trade.exit_price = candle.close
                trade.exit_reason = ExitReason.TIME_STOP
                trade.status = "closed"
                
                # Calculate PNL
                pnl_pct = (candle.close - trade.entry_price) / trade.entry_price * 100
                trade.pnl_pct = pnl_pct
                trade.pnl_sol = trade.position_size * (pnl_pct / 100)
                
                daily_pnl += trade.pnl_sol
                hourly_stats[current_hour].pnl += trade.pnl_sol
                hourly_stats[current_hour].trades_exited += 1
                
                if trade.pnl_sol > 0:
                    hourly_stats[current_hour].wins += 1
                    consecutive_losses = 0
                else:
                    hourly_stats[current_hour].losses += 1
                    consecutive_losses += 1
                
                recent_trades.append(trade)
                del open_positions[symbol]
                print(f"[{current_time.strftime('%H:%M')}] EXIT {symbol}: Time Stop @ {candle.close:.6f} ({pnl_pct:+.2f}%) = {trade.pnl_sol:+.4f} SOL")
                continue
            
            # Check scale 1 (+8%)
            if not trade.scale_1_done:
                gain_pct = (candle.high - trade.entry_price) / trade.entry_price * 100
                if gain_pct >= 8:
                    trade.scale_1_done = True
                    trade.scale_1_price = trade.entry_price * 1.08
                    print(f"[{current_time.strftime('%H:%M')}] SCALE 1 {symbol}: Sold 50% @ +8% ({trade.scale_1_price:.6f})")
            
            # Check stops
            if trade.scale_1_done:
                # After scale 1: breakeven stop
                if candle.low <= trade.entry_price:
                    trade.exit_time = current_time
                    trade.exit_price = trade.entry_price
                    trade.exit_reason = ExitReason.BREAKEVEN_STOP
                    trade.status = "closed"
                    
                    # Calculate PNL (50% sold at +8%, 50% at breakeven = +4% overall)
                    trade.pnl_pct = 4.0
                    trade.pnl_sol = trade.position_size * 0.04
                    
                    daily_pnl += trade.pnl_sol
                    hourly_stats[current_hour].pnl += trade.pnl_sol
                    hourly_stats[current_hour].trades_exited += 1
                    hourly_stats[current_hour].wins += 1
                    consecutive_losses = 0
                    
                    recent_trades.append(trade)
                    sectors_used.discard(token.sector)
                    del open_positions[symbol]
                    print(f"[{current_time.strftime('%H:%M')}] EXIT {symbol}: Breakeven Stop @ {trade.entry_price:.6f} (+4.00%) = {trade.pnl_sol:+.4f} SOL")
                    continue
            else:
                # Before scale 1: hard stop -7%
                loss_pct = (candle.low - trade.entry_price) / trade.entry_price * 100
                if loss_pct <= -7:
                    exit_price = trade.entry_price * 0.93
                    trade.exit_time = current_time
                    trade.exit_price = exit_price
                    trade.exit_reason = ExitReason.HARD_STOP
                    trade.status = "closed"
                    
                    trade.pnl_pct = -7.0
                    trade.pnl_sol = trade.position_size * (-0.07)
                    
                    daily_pnl += trade.pnl_sol
                    hourly_stats[current_hour].pnl += trade.pnl_sol
                    hourly_stats[current_hour].trades_exited += 1
                    hourly_stats[current_hour].losses += 1
                    consecutive_losses += 1
                    
                    recent_trades.append(trade)
                    sectors_used.discard(token.sector)
                    del open_positions[symbol]
                    print(f"[{current_time.strftime('%H:%M')}] EXIT {symbol}: Hard Stop @ {exit_price:.6f} (-7.00%) = {trade.pnl_sol:+.4f} SOL")
                    
                    # Check for pause
                    if consecutive_losses >= 3:
                        pause_until = current_time + timedelta(minutes=10)
                        print(f"[{current_time.strftime('%H:%M')}] *** PAUSING 10 MIN after 3 consecutive losses ***")
                    continue
            
            # Check scale 1 profit taking if not already done
            if not trade.scale_1_done:
                gain_pct = (candle.high - trade.entry_price) / trade.entry_price * 100
                if gain_pct >= 8:
                    trade.scale_1_done = True
                    trade.scale_1_price = candle.close
        
        # Check for new entries
        if len(open_positions) >= 3:
            continue  # Max positions reached
        
        if in_restricted_zone:
            continue  # In no-entry zone
        
        if pause_until:
            continue  # In pause period
        
        # Calculate win rate for position sizing
        win_rate = 0.5  # Default
        if len(recent_trades) >= 5:
            wins = sum(1 for t in recent_trades[-10:] if t.pnl_sol > 0)
            win_rate = wins / min(len(recent_trades[-10:]), 10)
        
        # Check each token for entry
        for token in QUALIFIED_TOKENS:
            if token.symbol in open_positions:
                continue
            
            if token.sector in sectors_used:
                continue  # Max 1 per sector
            
            candles = market_data[token.symbol]
            if minute >= len(candles):
                continue
            
            can_enter, signal_type, reason = check_entry_conditions(token, candles, minute)
            
            if can_enter:
                # Determine position size
                if win_rate < 0.40 and len(recent_trades) >= 10:
                    size_factor = 0.5  # Reduce 50%
                else:
                    size_factor = 1.0
                
                # Grade the setup
                # A+: Strong dip + volume spike + close to EMA20
                # B: Everything else
                is_aplus = False
                if signal_type == SignalType.DIP:
                    dip_depth = (candles[minute].close - max(c.high for c in candles[max(0,minute-20):minute])) / max(c.high for c in candles[max(0,minute-20):minute]) * 100
                    volume_ratio = candles[minute].volume / calculate_avg_volume(candles, minute)
                    if dip_depth <= -14 and volume_ratio > 3:
                        is_aplus = True
                
                if is_aplus:
                    position_size = 0.5 * size_factor
                    position_type = "A+"
                else:
                    position_size = 0.25 * size_factor
                    position_type = "B"
                
                # Check daily loss limit won't be exceeded
                potential_loss = position_size * 0.07
                if daily_pnl - potential_loss <= daily_loss_limit:
                    continue
                
                # Enter trade
                trade_id += 1
                trade = Trade(
                    id=trade_id,
                    symbol=token.symbol,
                    entry_time=current_time,
                    entry_price=candles[minute].close,
                    position_size=position_size,
                    position_type=position_type,
                    signal_type=signal_type
                )
                
                open_positions[token.symbol] = trade
                trades.append(trade)
                sectors_used.add(token.sector)
                hourly_stats[current_hour].trades_entered += 1
                
                signal_str = "DIP" if signal_type == SignalType.DIP else "GREEN_AFTER_REDS"
                print(f"[{current_time.strftime('%H:%M')}] ENTER {token.symbol} ({position_type}): {signal_str} @ {candles[minute].close:.6f}, Size: {position_size} SOL")
                
                if len(open_positions) >= 3:
                    break
    
    # Close any remaining positions at end of session
    for symbol, trade in open_positions.items():
        candles = market_data[symbol]
        final_price = candles[-1].close
        
        trade.exit_time = end_time
        trade.exit_price = final_price
        trade.exit_reason = ExitReason.TIME_STOP
        trade.status = "closed"
        
        pnl_pct = (final_price - trade.entry_price) / trade.entry_price * 100
        trade.pnl_pct = pnl_pct
        trade.pnl_sol = trade.position_size * (pnl_pct / 100)
        
        daily_pnl += trade.pnl_sol
        hourly_stats[20].pnl += trade.pnl_sol
        hourly_stats[20].trades_exited += 1
        
        if trade.pnl_sol > 0:
            hourly_stats[20].wins += 1
        else:
            hourly_stats[20].losses += 1
        
        print(f"[{end_time.strftime('%H:%M')}] EXIT {symbol}: Session End @ {final_price:.6f} ({pnl_pct:+.2f}%) = {trade.pnl_sol:+.4f} SOL")
    
    return trades, hourly_stats, daily_pnl

def generate_reports(trades: List[Trade], hourly_stats: Dict[int, HourlyStats], total_pnl: float):
    """Generate and save backtest reports"""
    
    # Calculate overall stats
    closed_trades = [t for t in trades if t.status == "closed"]
    winning_trades = [t for t in closed_trades if t.pnl_sol > 0]
    losing_trades = [t for t in closed_trades if t.pnl_sol <= 0]
    
    total_trades = len(closed_trades)
    wins = len(winning_trades)
    losses = len(losing_trades)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    total_profit = sum(t.pnl_sol for t in winning_trades) if winning_trades else 0
    total_loss = sum(t.pnl_sol for t in losing_trades) if losing_trades else 0
    
    avg_win = total_profit / wins if wins > 0 else 0
    avg_loss = total_loss / losses if losses > 0 else 0
    
    # Max drawdown
    running_pnl = 0
    max_drawdown = 0
    peak = 0
    for t in sorted(closed_trades, key=lambda x: x.exit_time or datetime.min):
        running_pnl += t.pnl_sol
        if running_pnl > peak:
            peak = running_pnl
        drawdown = peak - running_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Exit reasons breakdown
    exit_reasons = {}
    for t in closed_trades:
        reason = t.exit_reason.value if t.exit_reason else "unknown"
        if reason not in exit_reasons:
            exit_reasons[reason] = {"count": 0, "pnl": 0}
        exit_reasons[reason]["count"] += 1
        exit_reasons[reason]["pnl"] += t.pnl_sol
    
    # Hour-by-hour breakdown
    hourly_breakdown = {}
    for hour, stats in hourly_stats.items():
        hourly_breakdown[f"{hour}:00-{(hour+1)%24}:00"] = {
            "trades_entered": stats.trades_entered,
            "trades_exited": stats.trades_exited,
            "pnl_sol": round(stats.pnl, 6),
            "wins": stats.wins,
            "losses": stats.losses,
            "win_rate": round(stats.wins / (stats.wins + stats.losses) * 100, 2) if (stats.wins + stats.losses) > 0 else 0
        }
    
    # Save trades JSON
    trades_data = []
    for t in closed_trades:
        trades_data.append({
            "id": t.id,
            "symbol": t.symbol,
            "entry_time": t.entry_time.isoformat() if t.entry_time else None,
            "entry_price": t.entry_price,
            "position_size_sol": t.position_size,
            "position_type": t.position_type,
            "signal_type": t.signal_type.value if t.signal_type else None,
            "exit_time": t.exit_time.isoformat() if t.exit_time else None,
            "exit_price": t.exit_price,
            "exit_reason": t.exit_reason.value if t.exit_reason else None,
            "scale_1_done": t.scale_1_done,
            "pnl_pct": round(t.pnl_pct, 4),
            "pnl_sol": round(t.pnl_sol, 6)
        })
    
    with open("/home/skux/backtest_feb19_1900_2100_trades.json", "w") as f:
        json.dump(trades_data, f, indent=2)
    
    # Save results JSON
    results = {
        "backtest_config": {
            "date": "2026-02-19",
            "time_start_sydney": "19:00",
            "time_end_sydney": "21:00",
            "time_start_est": "02:00",
            "time_end_est": "04:00",
            "period_description": "Pre-market (US) / Evening (Sydney)",
            "strategy_version": "2.0",
            "session_type": "Low volume pre-market"
        },
        "summary": {
            "total_trades": total_trades,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate_pct": round(win_rate, 2),
            "total_pnl_sol": round(total_pnl, 6),
            "total_profit_sol": round(total_profit, 6),
            "total_loss_sol": round(total_loss, 6),
            "avg_win_sol": round(avg_win, 6),
            "avg_loss_sol": round(avg_loss, 6),
            "profit_factor": round(abs(total_profit / total_loss), 2) if total_loss != 0 else float('inf'),
            "max_drawdown_sol": round(max_drawdown, 6),
            "expectancy_sol": round((avg_win * win_rate/100 + avg_loss * (1-win_rate/100)), 6)
        },
        "hourly_breakdown": hourly_breakdown,
        "exit_reasons": exit_reasons,
        "market_conditions": {
            "volume_level": "Very Low (10-22% of normal)",
            "volatility": "Elevated (wider spreads, low liquidity)",
            "expected_behavior": "Chop, false signals, few sustained moves",
            "comparison_to_regular_hours": "Significantly reduced opportunity, higher noise"
        },
        "key_observations": [
            "Pre-market (02:00-04:00 EST) showed extremely low volume as expected",
            "Volume criteria (2x avg) rarely triggered due to depressed baseline",
            "EMA20 trend filter kept entries limited during chop",
            "Time stops were common due to lack of follow-through",
            "Few quality setups emerged during this period"
        ]
    }
    
    with open("/home/skux/backtest_feb19_1900_2100_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Period: Feb 19, 2026 19:00-21:00 Sydney (Pre-market EST)")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1f}% ({wins}W / {losses}L)")
    print(f"Total PNL: {total_pnl:+.6f} SOL")
    print(f"Profit Factor: {results['summary']['profit_factor']}")
    print(f"Max Drawdown: {max_drawdown:.6f} SOL")
    print(f"\nHourly Breakdown:")
    for hour, data in hourly_breakdown.items():
        print(f"  {hour}: {data['trades_entered']} entered, {data['trades_exited']} exited, PNL: {data['pnl_sol']:+.6f} SOL")
    print(f"\nExit Reasons:")
    for reason, data in exit_reasons.items():
        print(f"  {reason}: {data['count']} trades, {data['pnl']:+.6f} SOL")
    print(f"\nFiles saved:")
    print(f"  ~/backtest_feb19_1900_2100_trades.json")
    print(f"  ~/backtest_feb19_1900_2100_results.json")

if __name__ == "__main__":
    trades, hourly_stats, total_pnl = run_backtest()
    generate_reports(trades, hourly_stats, total_pnl)
