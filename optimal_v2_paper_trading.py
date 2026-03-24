#!/usr/bin/env python3
"""
Optimal Strategy v2.0 Paper Trading Simulation
2-hour simulation with realistic meme coin volatility
"""

import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

class SetupGrade(Enum):
    A_PLUS = "A+"  # Meets all criteria + strong trend
    B = "B"        # Missing one criterion
    C = "C"        # Missing 2+ criteria - SKIP

class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"  # Scale 1 hit, Scale 2 running

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    avg_volume: float = 0
    ema20: float = 0
    
    @property
    def change_pct(self):
        return ((self.close - self.open) / self.open) * 100
    
    @property
    def is_green(self):
        return self.close >= self.open

@dataclass
class Position:
    coin: str
    entry_price: float
    position_size: float  # in SOL
    entry_time: datetime
    scale1_price: float
    stop_loss: float
    trailing_stop: Optional[float] = None
    scale1_hit: bool = False
    scale2_size: float = 0
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    pnl_sol: float = 0
    status: TradeStatus = TradeStatus.OPEN
    setup_grade: str = ""
    entry_reason: str = ""

@dataclass
class Coin:
    symbol: str
    name: str
    market_cap: float
    sector: str
    base_price: float
    volatility: float
    volume_base: float
    candles: List[Candle] = field(default_factory=list)
    ema20: float = 0

# Approved coins with realistic parameters
APPROVED_COINS = {
    "WIF": Coin("WIF", "dogwifhat", 450_000_000, "dog", 1.85, 0.035, 15_000_000),
    "POPCAT": Coin("POPCAT", "Popcat", 380_000_000, "cat", 0.42, 0.028, 12_000_000),
    "BONK": Coin("BONK", "Bonk", 520_000_000, "dog", 0.000023, 0.025, 20_000_000),
    "BOME": Coin("BOME", "Book of Meme", 280_000_000, "meme", 0.0085, 0.040, 8_000_000),
    "SLERF": Coin("SLERF", "Slerf", 220_000_000, "meme", 0.15, 0.045, 6_000_000),
    "PENGU": Coin("PENGU", "Pudgy Penguins", 350_000_000, "nft", 0.025, 0.032, 10_000_000),
}

class PaperTradingSimulator:
    def __init__(self, start_capital: float = 1.0):
        self.start_capital = start_capital
        self.current_capital = start_capital
        self.locked_capital = 0.0  # Capital tied up in positions
        self.positions: List[Position] = []
        self.closed_trades: List[Position] = []
        self.current_time = datetime(2024, 2, 19, 14, 0, 0)  # Start 2:00 PM
        self.end_time = self.current_time + timedelta(hours=2)
        
        # Market regime tracking
        self.consecutive_losses = 0
        self.pause_until = None
        self.daily_pnl = 0
        self.trade_history_last10 = []  # Win = True, Loss = False
        self.max_drawdown = 0
        self.peak_capital = start_capital
        self.total_available_capital = start_capital  # For position sizing
        
        # Generate 2 hours of 1-minute candles for each coin
        self._generate_market_data()
        
    def _generate_market_data(self):
        """Generate realistic meme coin price action for 2 hours"""
        for coin in APPROVED_COINS.values():
            price = coin.base_price
            ema20 = price
            volume_history = []
            
            for i in range(120):  # 120 minutes
                timestamp = self.current_time + timedelta(minutes=i)
                
                # Create realistic volatility patterns
                trend_bias = 0.0005 if i < 60 else -0.0002  # Slight trend, then chop
                vol_factor = 1.0
                
                # Random volatility clusters (meme coin pumps/dumps)
                if random.random() < 0.08:  # 8% chance of volatility spike
                    vol_factor = random.uniform(2.5, 4.5)
                
                # Generate candle
                noise = random.gauss(trend_bias, coin.volatility * vol_factor)
                open_p = price
                close_p = price * (1 + noise)
                
                # High and low with wicks
                high_p = max(open_p, close_p) * (1 + random.uniform(0, coin.volatility * 0.5))
                low_p = min(open_p, close_p) * (1 - random.uniform(0, coin.volatility * 0.5))
                
                # Volume - spikes during moves
                vol_mult = 2.5 if abs(noise) > coin.volatility * 1.5 else random.uniform(0.7, 1.4)
                volume = coin.volume_base * vol_mult
                volume_history.append(volume)
                
                # Calculate avg volume (20-period)
                avg_vol = sum(volume_history[-20:]) / min(20, len(volume_history))
                
                # Update EMA20
                ema20 = close_p * 0.095 + ema20 * 0.905
                
                candle = Candle(
                    timestamp=timestamp,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=volume,
                    avg_volume=avg_vol,
                    ema20=ema20
                )
                coin.candles.append(candle)
                price = close_p
                
            coin.ema20 = ema20
    
    def _get_recent_high(self, coin: Coin, lookback: int = 20) -> float:
        """Get recent high from last N candles"""
        idx = self._get_current_candle_index()
        start_idx = max(0, idx - lookback)
        candles = coin.candles[start_idx:idx+1]
        return max(c.high for c in candles) if candles else coin.candles[0].high
    
    def _get_current_candle_index(self) -> int:
        """Get current candle index based on simulation time"""
        elapsed = (self.current_time - datetime(2024, 2, 19, 14, 0, 0)).total_seconds() // 60
        return int(min(elapsed, 119))
    
    def _get_current_candle(self, coin: Coin) -> Optional[Candle]:
        idx = self._get_current_candle_index()
        if idx < len(coin.candles):
            return coin.candles[idx]
        return None
    
    def _check_time_filter(self) -> bool:
        """No entries in first/last 30 min of each hour"""
        minute = self.current_time.minute
        return 30 <= minute <= 30  # Only trade in middle of hour (simplified)
    
    def _evaluate_setup(self, coin: Coin) -> tuple[SetupGrade, str]:
        """Evaluate if setup meets criteria"""
        candle = self._get_current_candle(coin)
        if not candle:
            return SetupGrade.C, "No candle data"
        
        criteria_met = []
        
        # 1. Quality Filter - Already approved
        criteria_met.append("Quality")
        
        # 2. Trend Filter - Price above 1h EMA20
        trend_ok = candle.close > candle.ema20
        if trend_ok:
            criteria_met.append("Trend")
        
        # 3. Volume Confirmation - 2x average
        volume_ok = candle.volume >= candle.avg_volume * 2
        if volume_ok:
            criteria_met.append("Volume")
        
        # 4. Entry Signal
        recent_high = self._get_recent_high(coin, 15)
        dip_pct = ((candle.close - recent_high) / recent_high) * 100
        
        # Check for mean reversion dip
        mean_reversion = -18 <= dip_pct <= -10
        
        # Check for momentum shift (green after 2 reds)
        idx = self._get_current_candle_index()
        momentum_shift = False
        if idx >= 2:
            prev1 = coin.candles[idx-1]
            prev2 = coin.candles[idx-2]
            momentum_shift = candle.is_green and not prev1.is_green and not prev2.is_green
        
        entry_signal = mean_reversion or momentum_shift
        if entry_signal:
            criteria_met.append("EntrySignal")
        
        # 5. No correlation - check separately
        
        # Grade the setup
        num_criteria = len(criteria_met)
        if num_criteria >= 4 and trend_ok and volume_ok:
            reason = f"A+ Setup: {', '.join(criteria_met)} | Dip: {dip_pct:.1f}%"
            return SetupGrade.A_PLUS, reason
        elif num_criteria >= 3:
            reason = f"B Setup: {', '.join(criteria_met)} | Dip: {dip_pct:.1f}%"
            return SetupGrade.B, reason
        else:
            reason = f"C Setup: Only {num_criteria}/4 criteria | Dip: {dip_pct:.1f}%"
            return SetupGrade.C, reason
    
    def _get_position_size(self, grade: SetupGrade) -> float:
        """Calculate position size based on setup grade and market regime"""
        base_size = 0.0
        if grade == SetupGrade.A_PLUS:
            base_size = 0.5
        elif grade == SetupGrade.B:
            base_size = 0.25
        
        # Win rate adjustment
        if len(self.trade_history_last10) >= 10:
            win_rate = sum(self.trade_history_last10[-10:]) / 10
            if win_rate < 0.4:
                base_size *= 0.5
        
        # Consecutive losses adjustment
        if self.consecutive_losses >= 3:
            return 0  # Paused
        
        # Daily loss limit
        if self.daily_pnl <= -0.3:
            return 0  # Stop trading
        
        # Check if we have enough available capital
        available = self.current_capital  # Free capital not locked in positions
        if base_size > available:
            return min(base_size, max(0, available - 0.05))  # Leave some buffer
        
        return base_size
    
    def _has_sector_position(self, sector: str) -> bool:
        """Check if we already have a position in this sector"""
        for pos in self.positions:
            if APPROVED_COINS[pos.coin].sector == sector:
                return True
        return False
    
    def _update_positions(self):
        """Update open positions - check exits"""
        for pos in self.positions[:]:
            if pos.status == TradeStatus.CLOSED:
                continue
                
            coin = APPROVED_COINS[pos.coin]
            candle = self._get_current_candle(coin)
            if not candle:
                continue
            
            current_price = candle.close
            pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
            
            # Check time stop (30 minutes)
            time_in_trade = (self.current_time - pos.entry_time).total_seconds() / 60
            if time_in_trade >= 30:
                # Close at market
                self._close_position(pos, current_price, "Time Stop (30min)")
                continue
            
            if not pos.scale1_hit:
                # Before Scale 1 - check targets
                if pnl_pct >= 8:
                    # Scale 1 hit - sell 50%
                    pos.scale1_hit = True
                    pos.status = TradeStatus.PARTIAL
                    pos.trailing_stop = pos.entry_price  # Move to breakeven
                    
                    # Realize 50% at +8%: return = 0.5 * size * 1.08
                    scale1_return = pos.position_size * 0.5 * 1.08
                    self.locked_capital -= pos.position_size * 0.5
                    self.current_capital += scale1_return
                    
                elif pnl_pct <= -7:
                    # Hard stop hit
                    self._close_position(pos, current_price, "Hard Stop (-7%)")
                    
            else:
                # After Scale 1 - trailing stop logic
                if pnl_pct >= 15:
                    # Tighten trailing stop to +5%
                    pos.trailing_stop = pos.entry_price * 1.05
                
                # Check trailing stop
                if current_price <= pos.trailing_stop:
                    self._close_position(pos, current_price, f"Trailing Stop ({pnl_pct:.1f}%)")
                elif pnl_pct >= 25:  # Let it run with wider trailing
                    # Move trailing stop to +15%
                    pos.trailing_stop = pos.entry_price * 1.15
    
    def _close_position(self, pos: Position, exit_price: float, reason: str):
        """Close a position and calculate PNL"""
        pos.exit_price = exit_price
        pos.exit_time = self.current_time
        pos.exit_reason = reason
        pos.status = TradeStatus.CLOSED
        
        pnl_pct = ((exit_price - pos.entry_price) / pos.entry_price) * 100
        
        if pos.scale1_hit:
            # Already realized 50% at +8%, now closing remaining 50%
            # Scale 1 gave us: 0.5 * size * 1.08 = 0.54 * size
            # Remaining 0.5 * size is now worth: 0.5 * size * (1 + pnl_pct/100)
            scale1_return = pos.position_size * 0.5 * 1.08
            scale2_return = pos.position_size * 0.5 * (1 + pnl_pct/100)
            total_return = scale1_return + scale2_return
            trade_pnl = total_return - pos.position_size
        else:
            # Full position closed at once
            total_return = pos.position_size * (1 + pnl_pct/100)
            trade_pnl = pos.position_size * (pnl_pct / 100)
        
        pos.pnl_sol = trade_pnl
        
        # Unlock capital + add profits
        self.locked_capital -= pos.position_size
        self.current_capital += total_return
        self.total_available_capital = self.current_capital + self.locked_capital
        self.daily_pnl += trade_pnl
        
        # Track win/loss
        is_win = trade_pnl > 0
        self.trade_history_last10.append(is_win)
        if len(self.trade_history_last10) > 20:
            self.trade_history_last10.pop(0)
        
        # Track consecutive losses
        if not is_win:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Move to closed trades
        self.closed_trades.append(pos)
        self.positions.remove(pos)
        
        # Update drawdown based on total available capital
        if self.total_available_capital > self.peak_capital:
            self.peak_capital = self.total_available_capital
        else:
            drawdown = (self.peak_capital - self.total_available_capital) / self.peak_capital
            self.max_drawdown = max(self.max_drawdown, drawdown)
    
    def _scan_for_entries(self):
        """Scan for new entry opportunities"""
        # Check time filter (avoid first/last 30 min of hour)
        minute = self.current_time.minute
        if minute < 5 or minute > 55:  # Conservative: only middle 50 min
            return
        
        # Check pause
        if self.pause_until and self.current_time < self.pause_until:
            return
        
        # Check max positions
        if len(self.positions) >= 3:
            return
        
        for symbol, coin in APPROVED_COINS.items():
            # Check if already in this coin
            if any(p.coin == symbol for p in self.positions):
                continue
            
            # Check sector correlation
            if self._has_sector_position(coin.sector):
                continue
            
            # Evaluate setup
            grade, reason = self._evaluate_setup(coin)
            if grade == SetupGrade.C:
                continue
            
            # Get position size
            size = self._get_position_size(grade)
            if size <= 0:
                continue
            
            # Enter position
            candle = self._get_current_candle(coin)
            pos = Position(
                coin=symbol,
                entry_price=candle.close,
                position_size=size,
                entry_time=self.current_time,
                scale1_price=candle.close * 1.08,
                stop_loss=candle.close * 0.93,
                setup_grade=grade.value,
                entry_reason=reason
            )
            self.positions.append(pos)
            self.locked_capital += size  # Lock up the capital
            self.total_available_capital = self.current_capital + self.locked_capital
            
            # Log entry
            print(f"🟢 ENTRY [{self.current_time.strftime('%H:%M')}] {symbol} @ ${candle.close:.6f}")
            print(f"   Grade: {grade.value} | Size: {size} SOL")
            print(f"   Reason: {reason}")
            
            if len(self.positions) >= 3:
                break
    
    def run_simulation(self):
        """Run the 2-hour simulation"""
        print("=" * 70)
        print("🚀 OPTIMAL STRATEGY v2.0 - PAPER TRADING SIMULATION")
        print("=" * 70)
        print(f"Start Capital: {self.start_capital} SOL")
        print(f"Duration: 2 hours ({self.current_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})")
        print("=" * 70)
        print()
        
        # Minute-by-minute simulation
        while self.current_time < self.end_time:
            # Update positions (check exits)
            self._update_positions()
            
            # Scan for entries
            self._scan_for_entries()
            
            # Advance time
            self.current_time += timedelta(minutes=1)
        
        # Close any remaining positions at market
        for pos in self.positions[:]:  # Copy list to avoid modification during iteration
            coin = APPROVED_COINS[pos.coin]
            last_candle = coin.candles[-1]
            self._close_position(pos, last_candle.close, "End of Simulation")
        
        self._generate_report()
    
    def _generate_report(self):
        """Generate final report and save to JSON"""
        print()
        print("=" * 70)
        print("📊 FINAL RESULTS - OPTIMAL STRATEGY v2.0")
        print("=" * 70)
        
        # Calculate final capital (free + locked)
        final_capital = self.current_capital + self.locked_capital
        total_pnl = final_capital - self.start_capital
        total_pnl_pct = (total_pnl / self.start_capital) * 100
        
        wins = [t for t in self.closed_trades if t.pnl_sol > 0]
        losses = [t for t in self.closed_trades if t.pnl_sol <= 0]
        
        win_rate = (len(wins) / len(self.closed_trades) * 100) if self.closed_trades else 0
        
        avg_winner = sum(t.pnl_sol for t in wins) / len(wins) if wins else 0
        avg_loser = sum(t.pnl_sol for t in losses) / len(losses) if losses else 0
        
        best_trade = max(self.closed_trades, key=lambda x: x.pnl_sol) if self.closed_trades else None
        worst_trade = min(self.closed_trades, key=lambda x: x.pnl_sol) if self.closed_trades else None
        
        print(f"\n💰 CAPITAL RESULTS:")
        print(f"   Start: {self.start_capital:.4f} SOL")
        print(f"   End:   {final_capital:.4f} SOL")
        print(f"   PNL:   {total_pnl:+.4f} SOL ({total_pnl_pct:+.2f}%)")
        print(f"   Max Drawdown: {self.max_drawdown*100:.2f}%")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades: {len(self.closed_trades)}")
        print(f"   Wins: {len(wins)} | Losses: {len(losses)}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Avg Winner: +{avg_winner:.4f} SOL")
        print(f"   Avg Loser: {avg_loser:.4f} SOL")
        
        if best_trade:
            print(f"\n🏆 BEST TRADE:")
            print(f"   {best_trade.coin} | +{best_trade.pnl_sol:.4f} SOL ({best_trade.exit_reason})")
        
        if worst_trade:
            print(f"\n💥 WORST TRADE:")
            print(f"   {worst_trade.coin} | {worst_trade.pnl_sol:.4f} SOL ({worst_trade.exit_reason})")
        
        print(f"\n📋 ALL TRADES:")
        print("-" * 70)
        for i, trade in enumerate(self.closed_trades, 1):
            emoji = "✅" if trade.pnl_sol > 0 else "❌"
            print(f"{i:2d}. {emoji} {trade.coin} | Entry: {trade.entry_time.strftime('%H:%M')} | "
                  f"PNL: {trade.pnl_sol:+.4f} SOL | {trade.exit_reason}")
        
        # Save to JSON
        trades_data = []
        for trade in self.closed_trades:
            trades_data.append({
                "coin": trade.coin,
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "position_size": trade.position_size,
                "pnl_sol": trade.pnl_sol,
                "exit_reason": trade.exit_reason,
                "setup_grade": trade.setup_grade,
                "entry_reason": trade.entry_reason,
                "scale1_hit": trade.scale1_hit
            })
        
        results_data = {
            "strategy": "Optimal Strategy v2.0",
            "start_capital": self.start_capital,
            "end_capital": final_capital,
            "total_pnl_sol": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "max_drawdown_pct": self.max_drawdown * 100,
            "total_trades": len(self.closed_trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": win_rate,
            "avg_winner_sol": avg_winner,
            "avg_loser_sol": avg_loser,
            "best_trade": {
                "coin": best_trade.coin if best_trade else None,
                "pnl_sol": best_trade.pnl_sol if best_trade else None,
                "exit_reason": best_trade.exit_reason if best_trade else None
            },
            "worst_trade": {
                "coin": worst_trade.coin if worst_trade else None,
                "pnl_sol": worst_trade.pnl_sol if worst_trade else None,
                "exit_reason": worst_trade.exit_reason if worst_trade else None
            },
            "daily_pnl": self.daily_pnl,
            "consecutive_losses": self.consecutive_losses,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("/home/skux/optimal_v2_trades.json", "w") as f:
            json.dump(trades_data, f, indent=2)
        
        with open("/home/skux/optimal_v2_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ Results saved to:")
        print("   ~/optimal_v2_trades.json")
        print("   ~/optimal_v2_results.json")
        print("=" * 70)

if __name__ == "__main__":
    # Set seed for reproducibility in testing (optional)
    # random.seed(42)
    
    sim = PaperTradingSimulator(start_capital=1.0)
    sim.run_simulation()
