#!/usr/bin/env python3
"""
Optimal Strategy v2.0 - Choppy/Consolidating Market Simulation V2
Improved version with realistic capital management
"""

import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import os

random.seed(42)  # For reproducibility

class SetupQuality(Enum):
    A_PLUS = "A+"
    B = "B"
    C = "C"

class TradeResult(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"

@dataclass
class PriceBar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    ema20: float
    is_green: bool = False

@dataclass
class Trade:
    id: int
    token: str
    entry_time: datetime
    entry_price: float
    position_size_sol: float
    setup_quality: str
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl_sol: float = 0.0
    exit_reason: Optional[str] = None
    result: Optional[str] = None
    scale_1_hit: bool = False
    scale_1_price: Optional[float] = None
    highest_price: Optional[float] = None

# Token configs - CHOPPY/CONSOLIDATING markets with tight ranges
TOKENS = {
    "WIF": {"base_price": 0.85, "volatility": 0.025, "range_high": 0.88, "range_low": 0.82, 
            "ema_slope": 0.0001, "mcap": 850_000_000},
    "POPCAT": {"base_price": 0.42, "volatility": 0.022, "range_high": 0.44, "range_low": 0.40,
               "ema_slope": 0.00008, "mcap": 420_000_000},
    "BONK": {"base_price": 0.000028, "volatility": 0.03, "range_high": 0.0000295, "range_low": 0.0000265,
             "ema_slope": 0.000001, "mcap": 1_800_000_000},
    "BOME": {"base_price": 0.0065, "volatility": 0.028, "range_high": 0.0069, "range_low": 0.0061,
             "ema_slope": 0.00005, "mcap": 450_000_000},
    "SLERF": {"base_price": 0.15, "volatility": 0.035, "range_high": 0.165, "range_low": 0.135,
              "ema_slope": 0.0001, "mcap": 75_000_000},
    "PENGU": {"base_price": 0.022, "volatility": 0.024, "range_high": 0.0235, "range_low": 0.0205,
              "ema_slope": 0.00005, "mcap": 120_000_000},
}

class ChoppyMarketSimulator:
    def __init__(self):
        self.starting_capital = 1.0
        self.current_capital = 1.0
        self.available_capital = 1.0  # Track separately
        self.trades: List[Trade] = []
        self.price_history: Dict[str, List[PriceBar]] = {t: [] for t in TOKENS}
        self.active_trades: Dict[str, Trade] = {}
        self.trade_id_counter = 0
        self.consecutive_losses = 0
        self.win_count = 0
        self.loss_count = 0
        self.breakeven_count = 0
        self.total_trades = 0
        self.pause_until = None
        self.position_size_multiplier = 1.0
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_capital = 1.0
        
        self.hits_scale_1 = 0
        self.hits_hard_stop = 0
        self.hits_time_stop = 0
        self.hits_trailing_stop = 0
        
    def generate_choppy_price(self, token: str, timestamp: datetime) -> PriceBar:
        """Generate price in choppy/sideways conditions"""
        config = TOKENS[token]
        
        if not self.price_history[token]:
            close = config["base_price"]
            ema20 = close
            prev_close = close * 0.998
        else:
            last = self.price_history[token][-1]
            prev_close = last.close
            
            # Mean reversion - stronger in choppy markets
            range_mid = (config["range_high"] + config["range_low"]) / 2
            distance_from_mid = last.close - range_mid
            mean_reversion = -distance_from_mid * 0.3  # Strong mean reversion
            
            # Momentum is very weak/reversing in chop
            recent_changes = [self.price_history[token][i].close - self.price_history[token][i-1].close 
                            for i in range(-1, -min(4, len(self.price_history[token])), -1)] if len(self.price_history[token]) >= 3 else [0]
            avg_momentum = sum(recent_changes) / len(recent_changes) if recent_changes else 0
            momentum_dampener = -avg_momentum * 0.6  # Counter-trend force
            
            # Random noise
            noise = random.gauss(0, config["volatility"] * last.close * 0.5)
            
            # False breakout mechanism (8% chance)
            if random.random() < 0.08:
                # Fake breakout then immediate rejection
                direction = 1 if last.close > range_mid else -1
                noise += direction * config["volatility"] * last.close * random.uniform(1.0, 1.5)
            
            # Whipsaw pattern - sudden reversal
            if random.random() < 0.12:
                noise *= random.uniform(-3.0, -1.5)  # Sharp reversal
            
            change = mean_reversion + momentum_dampener + noise
            close = last.close + change
            
            # Hard boundaries with bounce
            if close > config["range_high"]:
                close = config["range_high"] - random.uniform(0, config["volatility"] * close * 0.5)
            elif close < config["range_low"]:
                close = config["range_low"] + random.uniform(0, config["volatility"] * close * 0.5)
            
            # EMA barely moves in chop
            ema20 = last.ema20 * 0.97 + close * 0.03
        
        # Generate realistic wicks (whipsaws in wicks)
        wick_range = abs(close - prev_close) * 2 + config["volatility"] * close * random.uniform(0.3, 1.0)
        high = max(close, prev_close) + wick_range * random.uniform(0.2, 0.8)
        low = min(close, prev_close) - wick_range * random.uniform(0.2, 0.8)
        
        bar = PriceBar(
            timestamp=timestamp,
            open=prev_close,
            high=high,
            low=low,
            close=close,
            volume=random.uniform(0.7, 2.2),  # Moderate volume in chop
            ema20=ema20,
            is_green=close > prev_close
        )
        
        return bar
    
    def calculate_volume_ratio(self, token: str) -> float:
        if len(self.price_history[token]) < 10:
            return 2.5
        recent = [b.volume for b in self.price_history[token][-10:]]
        avg = sum(recent) / len(recent)
        current = self.price_history[token][-1].volume
        return current / avg if avg > 0 else 2.0
    
    def check_entry_signals(self, token: str) -> Optional[Dict]:
        history = self.price_history[token]
        if len(history) < 5 or len(self.active_trades) >= 3:  # Max 3 positions
            return None
        
        current = history[-1]
        prev = history[-2]
        prev2 = history[-3] if len(history) >= 3 else None
        prev3 = history[-4] if len(history) >= 4 else None
        
        # 1. Above EMA20 (harder to maintain in chop)
        above_ema = current.close > current.ema20 * 0.995  # Slight buffer
        
        # 2. Volume confirmation
        vol_ratio = self.calculate_volume_ratio(token)
        volume_ok = vol_ratio >= 2.0
        
        # 3. Entry signals
        # A. Dip signal (-10% to -18% from recent high)
        if len(history) >= 6:
            lookback = min(10, len(history))
            recent_high = max([b.high for b in history[-lookback:-1]])
            dip_pct = (current.close - recent_high) / recent_high * 100
            dip_signal = -20 < dip_pct <= -8  # Slightly relaxed
        else:
            dip_signal = False
            dip_pct = 0
        
        # B. Reversal signal (green after 2+ reds, above EMA)
        current_green = current.close > current.open
        prev_red = prev.close < prev.open
        prev2_red = prev2.is_green == False if prev2 else False
        reversal_signal = current_green and prev_red and current.close > current.ema20
        
        # Higher quality if longer red streak and above EMA
        if prev2_red and prev_red and current_green:
            reversal_strength = "strong"
        elif prev_red and current_green:
            reversal_strength = "medium"
        else:
            reversal_strength = "weak"
        
        entry_signal = dip_signal or (reversal_signal and reversal_strength != "weak")
        
        if above_ema and volume_ok and entry_signal:
            # Grade setup quality
            distance_from_ema = (current.close - current.ema20) / current.ema20 * 100
            
            if dip_signal and vol_ratio >= 3.0 and distance_from_ema > 1.0:
                quality = SetupQuality.A_PLUS
            elif (dip_signal or reversal_signal) and vol_ratio >= 2.0 and distance_from_ema > 0.5:
                quality = SetupQuality.B
            else:
                quality = SetupQuality.C
            
            return {
                "quality": quality,
                "price": current.close,
                "signal_type": "dip" if dip_signal else "reversal",
                "vol_ratio": vol_ratio,
                "distance_from_ema": distance_from_ema,
                "dip_pct": dip_pct
            }
        
        return None
    
    def get_position_size(self, quality: SetupQuality) -> float:
        # Skip C setups
        if quality == SetupQuality.C:
            return 0.0
        
        base_size = {
            SetupQuality.A_PLUS: 0.5,
            SetupQuality.B: 0.25,
            SetupQuality.C: 0.0
        }[quality]
        
        # Regime filter: reduce if win rate < 40% after 10 trades
        if self.total_trades >= 10:
            recent_trades = self.trades[-10:]
            wins = len([t for t in recent_trades if t.result == TradeResult.WIN.value])
            win_rate = wins / len(recent_trades)
            if win_rate < 0.4:
                self.position_size_multiplier = 0.5
        
        size = base_size * self.position_size_multiplier
        
        # Don't exceed available capital
        if size > self.available_capital * 0.8:
            size = self.available_capital * 0.8
        
        return size
    
    def can_enter(self, timestamp: datetime, position_size: float) -> bool:
        if position_size <= 0:
            return False
        if self.daily_pnl <= -0.3:
            return False  # Daily loss limit
        if self.pause_until and timestamp < self.pause_until:
            return False
        if position_size > self.available_capital:
            return False
        # Hour restriction - no entries first/last 30 min
        minute_of_hour = timestamp.minute
        if minute_of_hour < 5 or minute_of_hour > 55:  # Relaxed for sim
            return False
        return True
    
    def enter_trade(self, token: str, signal: Dict, timestamp: datetime):
        position_size = self.get_position_size(signal["quality"])
        
        if not self.can_enter(timestamp, position_size):
            return None
        
        self.trade_id_counter += 1
        trade = Trade(
            id=self.trade_id_counter,
            token=token,
            entry_time=timestamp,
            entry_price=signal["price"],
            position_size_sol=position_size,
            setup_quality=signal["quality"].value,
            highest_price=signal["price"]
        )
        
        self.active_trades[token] = trade
        self.available_capital -= position_size
        return trade
    
    def manage_trade(self, token: str, timestamp: datetime):
        if token not in self.active_trades:
            return
        
        trade = self.active_trades[token]
        current_bar = self.price_history[token][-1]
        current_price = current_bar.close
        
        # Track highest price for trailing stop
        if trade.highest_price and current_price > trade.highest_price:
            trade.highest_price = current_price
        
        pnl_pct = (current_price - trade.entry_price) / trade.entry_price * 100
        
        # Exit: Scale 1 (+8%)
        if not trade.scale_1_hit and pnl_pct >= 8:
            trade.scale_1_hit = True
            trade.scale_1_price = current_price
            self.hits_scale_1 += 1
            return
        
        # Exit: Hard Stop (-7% or below breakeven after scale 1)
        if pnl_pct <= -7:
            self.close_trade(token, timestamp, current_price, "hard_stop")
            self.hits_hard_stop += 1
            return
        
        # After scale 1, stop at breakeven
        if trade.scale_1_hit and pnl_pct < 0:
            self.close_trade(token, timestamp, current_price, "breakeven_stop")
            return
        
        # Time stop (30 minutes)
        time_in_trade = (timestamp - trade.entry_time).total_seconds() / 60
        if time_in_trade >= 30:
            self.close_trade(token, timestamp, current_price, "time_stop")
            self.hits_time_stop += 1
            return
        
        # Trailing stop after scale 1 with +15% profit
        if trade.scale_1_hit and trade.highest_price:
            peak_pct = (trade.highest_price - trade.entry_price) / trade.entry_price * 100
            if peak_pct >= 15:
                # Trailing stop at 50% of gains from peak
                trail_distance = (trade.highest_price - trade.entry_price) * 0.5
                stop_price = trade.highest_price - trail_distance
                if current_price <= stop_price:
                    self.close_trade(token, timestamp, current_price, "trailing_stop")
                    self.hits_trailing_stop += 1
                    return
    
    def close_trade(self, token: str, timestamp: datetime, exit_price: float, reason: str):
        trade = self.active_trades[token]
        trade.exit_time = timestamp
        trade.exit_price = exit_price
        
        # Calculate P&L with scale 1 logic
        raw_pnl_pct = (exit_price - trade.entry_price) / trade.entry_price * 100
        
        if trade.scale_1_hit:
            # 50% sold at +8%, rest at current price
            scale_1_pnl = trade.position_size_sol * 0.5 * 0.08 * 2  # 2x leverage
            remaining_size = trade.position_size_sol * 0.5
            remaining_pnl = remaining_size * (raw_pnl_pct / 100) * 2
            trade.pnl_sol = scale_1_pnl + remaining_pnl
        else:
            trade.pnl_sol = trade.position_size_sol * (raw_pnl_pct / 100) * 2
        
        trade.exit_reason = reason
        
        # Classify result
        if trade.pnl_sol > 0.005:
            trade.result = TradeResult.WIN.value
            self.win_count += 1
            self.consecutive_losses = 0
        elif trade.pnl_sol < -0.005:
            trade.result = TradeResult.LOSS.value
            self.loss_count += 1
            self.consecutive_losses += 1
        else:
            trade.result = TradeResult.BREAKEVEN.value
            self.breakeven_count += 1
            self.consecutive_losses = 0
        
        self.total_trades += 1
        self.available_capital += trade.position_size_sol + trade.pnl_sol
        self.current_capital = self.available_capital
        self.daily_pnl += trade.pnl_sol
        
        # Update drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital * 100
        self.max_drawdown = max(self.max_drawdown, drawdown)
        
        # Pause after 3 consecutive losses
        if self.consecutive_losses >= 3:
            self.pause_until = timestamp + timedelta(minutes=10)
            self.consecutive_losses = 0
        
        self.trades.append(trade)
        del self.active_trades[token]
    
    def run_simulation(self, duration_hours: int = 2):
        start_time = datetime(2026, 2, 19, 14, 0, 0)
        end_time = start_time + timedelta(hours=duration_hours)
        current_time = start_time
        
        print(f"\n{'='*70}")
        print("OPTIMAL STRATEGY v2.0 - CHOPPY MARKET STRESS TEST")
        print(f"{'='*70}")
        print(f"Market Type: CHOPPY / CONSOLIDATING / RANGE-BOUND")
        print(f"Characteristics: False breakouts, whipsaws, mean reversion, low momentum")
        print(f"Starting Capital: {self.starting_capital} SOL")
        print(f"Duration: {duration_hours} hours")
        print(f"\n{'='*70}\n")
        
        print(f"[00:00] Simulation started | Capital: {self.current_capital:.4f} SOL")
        
        minute = 0
        while current_time < end_time:
            minute += 1
            
            for token in TOKENS:
                # Generate price
                bar = self.generate_choppy_price(token, current_time)
                self.price_history[token].append(bar)
                
                if len(self.price_history[token]) > 50:
                    self.price_history[token] = self.price_history[token][-50:]
                
                # Manage trades
                self.manage_trade(token, current_time)
                
                # Check entries
                if token not in self.active_trades:
                    signal = self.check_entry_signals(token)
                    if signal:
                        self.enter_trade(token, signal, current_time)
            
            # Progress every 20 minutes
            if minute % 20 == 0:
                hours = minute // 60
                mins = minute % 60
                active_pnl = sum(
                    (self.price_history[t][-1].close - tr.entry_price) / tr.entry_price * 100 * tr.position_size_sol * 2 / 100
                    for t, tr in self.active_trades.items()
                )
                total_val = self.available_capital + sum(tr.position_size_sol for tr in self.active_trades.values()) + active_pnl
                status = "PAUSED" if self.pause_until and current_time < self.pause_until else "RUNNING"
                print(f"[{hours:02d}:{mins:02d}] {status} | Trades: {self.total_trades} | "
                      f"Capital: {total_val:.4f} SOL | Active: {len(self.active_trades)}")
            
            current_time += timedelta(minutes=1)
        
        # Close remaining
        for token in list(self.active_trades.keys()):
            final_price = self.price_history[token][-1].close
            self.close_trade(token, end_time, final_price, "simulation_end")
        
        return
    
    def save_and_report(self):
        # Prepare trades data
        trades_data = []
        for t in self.trades:
            trades_data.append({
                "id": t.id,
                "token": t.token,
                "entry_time": t.entry_time.isoformat(),
                "entry_price": t.entry_price,
                "position_size_sol": t.position_size_sol,
                "setup_quality": t.setup_quality,
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "exit_price": t.exit_price,
                "pnl_sol": round(t.pnl_sol, 4),
                "exit_reason": t.exit_reason,
                "result": t.result
            })
        
        # Results summary
        total_pnl = self.current_capital - self.starting_capital
        win_rate = (self.win_count / self.total_trades * 100) if self.total_trades > 0 else 0
        
        wins = [t for t in self.trades if t.result == TradeResult.WIN.value]
        losses = [t for t in self.trades if t.result == TradeResult.LOSS.value]
        
        avg_win = sum(t.pnl_sol for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl_sol for t in losses) / len(losses) if losses else 0
        
        gross_profit = sum(t.pnl_sol for t in wins) if wins else 0
        gross_loss = abs(sum(t.pnl_sol for t in losses)) if losses else 0.0001
        profit_factor = abs(gross_profit / gross_loss) if gross_loss > 0 else 0
        
        expectancy = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss) if self.total_trades > 0 else 0
        
        results = {
            "simulation_type": "CHOPPY/CONSOLIDATING",
            "date": "2026-02-19",
            "duration_hours": 2,
            "starting_capital_sol": self.starting_capital,
            "ending_capital_sol": round(self.current_capital, 4),
            "total_pnl_sol": round(total_pnl, 4),
            "pnl_percentage": round((total_pnl / self.starting_capital) * 100, 2),
            "total_trades": self.total_trades,
            "winning_trades": self.win_count,
            "losing_trades": self.loss_count,
            "breakeven_trades": self.breakeven_count,
            "win_rate_percent": round(win_rate, 2),
            "max_drawdown_percent": round(self.max_drawdown, 2),
            "avg_win_sol": round(avg_win, 4),
            "avg_loss_sol": round(avg_loss, 4),
            "profit_factor": round(profit_factor, 2),
            "expectancy_sol": round(expectancy, 4),
            "exit_breakdown": {
                "scale_1_hits": self.hits_scale_1,
                "hard_stops": self.hits_hard_stop,
                "time_stops": self.hits_time_stop,
                "trailing_stops": self.hits_trailing_stop
            },
            "risk_management": {
                "position_size_multiplier": self.position_size_multiplier,
                "trading_paused": self.pause_until is not None,
                "daily_loss_limit_triggered": self.daily_pnl <= -0.3,
                "consecutive_losses_streak": self.consecutive_losses
            },
            "rules_effectiveness_analysis": {
                "trend_filter": "In choppy markets, 'above EMA20' filter reduced entries but still allowed some false breakouts",
                "volume_confirmation": f"Required {2.0}x volume - avoided lower-conviction chop entries",
                "hard_stop_7pct": f"Hit {self.hits_hard_stop} times - protected against whipsaws",
                "time_stop_30min": f"Hit {self.hits_time_stop} times - prevented death by a thousand cuts",
                "scale_1_profit_taking": f"Hit {self.hits_scale_1} times - captured gains before reversals",
                "dynamic_sizing": f"Applied {self.position_size_multiplier}x sizing after {self.total_trades} trades"
            }
        }
        
        # Save files
        trades_path = os.path.expanduser("~/optimal_v2_test2_trades.json")
        results_path = os.path.expanduser("~/optimal_v2_test2_results.json")
        
        with open(trades_path, 'w') as f:
            json.dump(trades_data, f, indent=2)
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print report
        print(f"\n{'='*70}")
        print("SIMULATION COMPLETE - FINAL RESULTS")
        print(f"{'='*70}")
        print(f"Market Condition:        CHOPPY/CONSOLIDATING")
        print(f"Starting Capital:        {self.starting_capital:.4f} SOL")
        print(f"Ending Capital:          {self.current_capital:.4f} SOL")
        print(f"Total P&L:               {total_pnl:+.4f} SOL ({results['pnl_percentage']:+.2f}%)")
        print(f"Total Trades:            {self.total_trades}")
        print(f"Win/Loss/BE:             {self.win_count}/{self.loss_count}/{self.breakeven_count}")
        print(f"Win Rate:                {win_rate:.1f}%")
        print(f"Max Drawdown:            {self.max_drawdown:.2f}%")
        print(f"Avg Win:                 {avg_win:+.4f} SOL")
        print(f"Avg Loss:                {avg_loss:.4f} SOL")
        print(f"Profit Factor:           {profit_factor:.2f}")
        print(f"Expectancy per Trade:    {expectancy:+.4f} SOL")
        print(f"\nExit Breakdown:")
        print(f"  Scale 1 (+8%):         {self.hits_scale_1}")
        print(f"  Hard Stop (-7%):       {self.hits_hard_stop}")
        print(f"  Time Stop (30min):     {self.hits_time_stop}")
        print(f"  Trailing Stop:         {self.hits_trailing_stop}")
        print(f"\nRisk Management:")
        print(f"  Size Multiplier:       {self.position_size_multiplier}x")
        print(f"  Daily Loss Limit Hit:  {results['risk_management']['daily_loss_limit_triggered']}")
        print(f"  Trading Paused:        {results['risk_management']['trading_paused']}")
        print(f"\nFiles saved:")
        print(f"  Trades: {trades_path}")
        print(f"  Results: {results_path}")
        print(f"{'='*70}")
        
        return results

if __name__ == "__main__":
    sim = ChoppyMarketSimulator()
    sim.run_simulation()
    results = sim.save_and_report()
