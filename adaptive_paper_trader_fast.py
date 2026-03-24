#!/usr/bin/env python3
"""
Adaptive Paper Trading Bot - Fast Simulation Mode
Uses realistic crypto price simulation to demonstrate strategy performance.
Completes 10+ trades quickly for strategy analysis.
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
    PARTIAL_EXIT = "partial_exit"

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

@dataclass
class TradingSession:
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    initial_balance: float = 1.0
    final_balance: float = 1.0
    total_trades: int = 0
    dip_trades: int = 0
    breakout_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    dip_wins: int = 0
    breakout_wins: int = 0
    win_rate: float = 0.0
    dip_win_rate: float = 0.0
    breakout_win_rate: float = 0.0
    total_pnl_sol: float = 0.0
    total_pnl_percent: float = 0.0
    max_drawdown: float = 0.0
    trades: List[Dict] = field(default_factory=list)
    market_condition_history: List[Dict] = field(default_factory=list)


class RealisticCryptoSimulator:
    """
    Simulates realistic crypto price movements with:
    - Trending phases (up/down)
    - Ranging/choppy phases
    - Breakouts and breakdowns
    - Momentum bursts
    """
    
    COINS = {
        "BONK": {"base_price": 0.000012, "volatility": 0.08, "trend_bias": 0.02},
        "WIF": {"base_price": 1.85, "volatility": 0.06, "trend_bias": 0.03},
        "POPCAT": {"base_price": 0.42, "volatility": 0.09, "trend_bias": 0.01},
        "BOME": {"base_price": 0.0085, "volatility": 0.12, "trend_bias": 0.02},
        "SLERF": {"base_price": 0.15, "volatility": 0.11, "trend_bias": -0.01},
        "PONKE": {"base_price": 0.035, "volatility": 0.14, "trend_bias": 0.04},
        "MYRO": {"base_price": 0.045, "volatility": 0.10, "trend_bias": 0.03},
        "WEN": {"base_price": 0.000085, "volatility": 0.07, "trend_bias": 0.02},
        "TURBO": {"base_price": 0.0042, "volatility": 0.09, "trend_bias": 0.02},
        "GME": {"base_price": 0.012, "volatility": 0.15, "trend_bias": 0.05},
    }
    
    def __init__(self):
        self.prices = {name: data["base_price"] for name, data in self.COINS.items()}
        self.candle_history = {name: [] for name in self.COINS}
        self.market_regime = {name: "neutral" for name in self.COINS}  # bullish, bearish, ranging
        self.regime_duration = {name: 0 for name in self.COINS}
        
        # Initialize with some historical candles
        for name in self.COINS:
            for i in range(20):
                self._generate_candle(name, is_initial=True)
    
    def _generate_candle(self, coin: str, is_initial: bool = False):
        """Generate a realistic candle based on current market regime"""
        data = self.COINS[coin]
        current_price = self.prices[coin]
        
        # Regime transitions
        if not is_initial and random.random() < 0.05:  # 5% chance of regime change
            self.regime_duration[coin] = 0
            regimes = ["bullish", "bearish", "ranging"]
            weights = [0.35, 0.25, 0.4]  # Slightly bullish bias (crypto)
            self.market_regime[coin] = random.choices(regimes, weights)[0]
        
        regime = self.market_regime[coin]
        self.regime_duration[coin] += 1
        
        # Generate price movement based on regime
        if regime == "bullish":
            base_change = random.gauss(0.02, data["volatility"] * 0.5)  # Positive drift
        elif regime == "bearish":
            base_change = random.gauss(-0.015, data["volatility"] * 0.5)  # Negative drift
        else:  # ranging
            base_change = random.gauss(0, data["volatility"] * 0.4)  # No drift
        
        # Add trend bias
        base_change += data["trend_bias"] * 0.01
        
        # Occasional breakout/dump events (5% chance)
        if random.random() < 0.05:
            event_change = random.choice([-1, 1]) * random.uniform(0.05, 0.15)
            base_change += event_change
        
        # Intra-candle movement
        body_change = base_change 
        wick_factor = data["volatility"] * 0.6
        high_wick = abs(random.gauss(0, wick_factor))
        low_wick = abs(random.gauss(0, wick_factor))
        
        open_price = current_price
        close_price = current_price * (1 + body_change)
        high_price = max(open_price, close_price) * (1 + high_wick)
        low_price = min(open_price, close_price) * (1 - low_wick)
        
        # Volume correlated with volatility
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
        
        # Keep history manageable
        if len(self.candle_history[coin]) > 100:
            self.candle_history[coin].pop(0)
        
        return candle
    
    def update_all(self):
        """Generate new candles for all coins"""
        for coin in self.COINS:
            self._generate_candle(coin)
        return self.get_current_prices()
    
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices"""
        return self.prices.copy()
    
    def get_candles(self, coin: str, limit: int = 50) -> List[Candle]:
        """Get recent candles for a coin"""
        return self.candle_history[coin][-limit:] if coin in self.candle_history else []


class AdaptiveStrategy:
    """Adaptive strategy that switches between DIP and BREAKOUT modes"""
    
    def __init__(self, initial_capital: float = 1.0):
        self.initial_capital = initial_capital
        self.balance_sol = initial_capital
        self.peak_balance = initial_capital
        self.min_balance = initial_capital
        self.positions: Dict[str, Trade] = {}
        self.trades: List[Trade] = []
        self.trade_counter = 0
        self.session_start = datetime.now(timezone.utc).isoformat()
        
        # Strategy parameters
        self.ema_fast_period = 9
        self.ema_slow_period = 21
        self.scale_target = 0.20  # +20%
        self.trailing_stop_pct = 0.10  # -10% from peak
        self.hard_stop_pct = 0.07  # -7% hard stop
        
        # Mode performance tracking
        self.mode_performance = {
            Mode.DIP.value: {"trades": 0, "wins": 0, "pnl": 0.0},
            Mode.BREAKOUT.value: {"trades": 0, "wins": 0, "pnl": 0.0}
        }
        
        self.market_conditions: List[Dict] = []
        
    def generate_trade_id(self) -> str:
        self.trade_counter += 1
        return f"ADAPTIVE_{int(time.time())}_{self.trade_counter}"
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def detect_market_condition(self, candles: List[Candle]) -> Tuple[Mode, Dict]:
        """Detect market condition and return mode (DIP or BREAKOUT)"""
        if len(candles) < 20:
            return Mode.DIP, {"reason": "insufficient_data", "confidence": 0.3}
        
        closes = [c.close for c in candles]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, self.ema_fast_period)
        ema_slow = self.calculate_ema(closes, self.ema_slow_period)
        
        # Calculate trend metrics
        price_changes = [(closes[i] - closes[i-1]) / closes[i-1] * 100 
                        for i in range(1, len(closes))]
        
        recent_changes = price_changes[-10:]
        avg_recent_change = sum(recent_changes) / len(recent_changes)
        
        # Trend consistency
        higher_highs = sum(1 for i in range(-10, -1) 
                          if candles[i].high > candles[i-1].high)
        higher_lows = sum(1 for i in range(-10, -1) 
                         if candles[i].low > candles[i-1].low)
        
        # Volatility measurement
        volatility = statistics.stdev(price_changes[-15:]) if len(price_changes) >= 15 else 5.0
        
        # Calculate trend score
        trend_score = 0
        
        # EMA alignment (bullish = positive score)
        if ema_fast > ema_slow * 1.02:
            trend_score += 3
        elif ema_fast > ema_slow:
            trend_score += 1.5
        elif ema_fast < ema_slow * 0.98:
            trend_score -= 3
        elif ema_fast < ema_slow:
            trend_score -= 1.5
        
        # Recent momentum
        if avg_recent_change > 2.5:
            trend_score += 2.5
        elif avg_recent_change > 0.8:
            trend_score += 1
        elif avg_recent_change < -2.5:
            trend_score -= 2
        elif avg_recent_change < -0.8:
            trend_score -= 1
        
        # Pattern detection
        if higher_highs >= 6 and higher_lows >= 6:
            trend_score += 2
        elif higher_highs <= 3 and higher_lows <= 3:
            trend_score -= 2
        else:
            trend_score -= 0.5  # Choppy
        
        # Determine mode based on conditions
        if trend_score >= 2.5:
            mode = Mode.BREAKOUT
            confidence = min(trend_score / 5, 1.0)
            reason = "strong_uptrend"
        elif trend_score <= -2:
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
    
    def find_dip_entry(self, candles: List[Candle], coin: str) -> Optional[Dict]:
        """Find dip entry opportunities"""
        if len(candles) < 10:
            return None
        
        current = candles[-1]
        
        # Calculate pullback from recent high
        recent_high = max(c.high for c in candles[-10:])
        pullback_pct = (recent_high - current.close) / recent_high * 100
        
        # Dip entry criteria
        if not (3 <= pullback_pct <= 15):
            return None
        
        # Look for reversal signals
        is_reversal = False
        
        # Green candle (bullish close > open)
        if current.close > current.open:
            body_size = (current.close - current.open) / (current.high - current.low + 0.000001)
            if body_size > 0.3:
                is_reversal = True
        
        # Hammer candle (long lower wick)
        lower_wick = min(current.close, current.open) - current.low
        body_size = abs(current.close - current.open)
        if lower_wick > body_size * 1.5 and lower_wick > 0:
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
    
    def find_breakout_entry(self, candles: List[Candle], coin: str) -> Optional[Dict]:
        """Find breakout entry opportunities"""
        if len(candles) < 15:
            return None
        
        current = candles[-1]
        prev = candles[-2]
        
        # Recent resistance
        recent_candles = candles[-15:-1]
        resistance = max(c.high for c in recent_candles)
        
        # Breakout threshold
        breakout_pct = (current.close - resistance) / resistance * 100
        
        if breakout_pct < 3:  # Need at least 3% breakout
            return None
        
        # Volume confirmation
        recent_volume = sum(c.volume for c in candles[-3:]) / 3
        prev_volume = sum(c.volume for c in candles[-8:-3]) / 5
        volume_spike = recent_volume / prev_volume if prev_volume > 0 else 1
        
        if volume_spike < 1.3:
            return None
        
        # EMA confirmation
        closes = [c.close for c in candles]
        ema_fast = self.calculate_ema(closes, 9)
        
        if current.close < ema_fast * 0.98:
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
    
    def open_position(self, signal: Dict, mode: Mode) -> Optional[Trade]:
        """Open a position"""
        coin = signal["coin"]
        
        if coin in self.positions:
            return None
        
        # Position sizing (max 0.35 SOL per trade)
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
    
    def manage_position(self, trade: Trade, current_price: float) -> Optional[str]:
        """Manage position and return exit reason if closed"""
        entry = trade.entry_price
        
        # Update peak and trailing stop
        if current_price > trade.peak_price:
            trade.peak_price = current_price
            new_trailing = trade.peak_price * (1 - self.trailing_stop_pct)
            trade.trailing_stop_price = max(new_trailing, entry * (1 - self.hard_stop_pct))
        
        current_pnl_pct = (current_price - entry) / entry
        
        # Hard stop check (-7%)
        hard_stop_price = entry * (1 - self.hard_stop_pct)
        if current_price <= hard_stop_price:
            return "hard_stop"
        
        # Scale 50% at +20%
        if not trade.scaled and current_pnl_pct >= self.scale_target:
            return "scale_50"
        
        # Trailing stop check (-10% from peak)
        if current_price <= trade.trailing_stop_price:
            return "trailing_stop"
        
        return None
    
    def partial_scale_out(self, coin: str, exit_price: float, candles: List[Candle]) -> float:
        """Scale out 50% of position at +20%"""
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
    
    def close_position(self, coin: str, exit_price: float, reason: str) -> Trade:
        """Close position and calculate P&L"""
        trade = self.positions[coin]
        trade.exit_price = exit_price
        trade.exit_time = datetime.now(timezone.utc).isoformat()
        trade.exit_reason = reason
        
        # Calculate P&L
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        trade.pnl_sol = trade.position_size_sol * price_change_pct
        trade.pnl_percent = price_change_pct * 100
        
        # Set status
        if trade.pnl_sol > 0:
            trade.status = TradeStatus.TARGET_HIT
        else:
            trade.status = TradeStatus.STOPPED
        
        # Update balance
        self.balance_sol += trade.position_size_sol + trade.pnl_sol
        
        # Track mode performance
        mode_key = trade.mode.value
        self.mode_performance[mode_key]["trades"] += 1
        self.mode_performance[mode_key]["pnl"] += trade.pnl_sol
        if trade.pnl_sol > 0:
            self.mode_performance[mode_key]["wins"] += 1
        
        # Update peak/min balance tracking
        if self.balance_sol > self.peak_balance:
            self.peak_balance = self.balance_sol
        if self.balance_sol < self.min_balance:
            self.min_balance = self.balance_sol
        
        self.trades.append(trade)
        del self.positions[coin]
        
        return trade
    
    def get_session_results(self) -> TradingSession:
        """Get final results"""
        winning_trades = [t for t in self.trades if t.pnl_sol > 0]
        losing_trades = [t for t in self.trades if t.pnl_sol <= 0]
        
        dip_trades = [t for t in self.trades if t.mode == Mode.DIP]
        breakout_trades = [t for t in self.trades if t.mode == Mode.BREAKOUT]
        
        dip_wins = sum(1 for t in dip_trades if t.pnl_sol > 0)
        breakout_wins = sum(1 for t in breakout_trades if t.pnl_sol > 0)
        
        total_pnl = sum(t.pnl_sol for t in self.trades)
        max_drawdown = (self.peak_balance - self.min_balance) / self.initial_capital * 100
        
        return TradingSession(
            session_id=f"adaptive_{int(time.time())}",
            start_time=self.session_start,
            end_time=datetime.now(timezone.utc).isoformat(),
            initial_balance=self.initial_capital,
            final_balance=self.balance_sol,
            total_trades=len(self.trades),
            dip_trades=len(dip_trades),
            breakout_trades=len(breakout_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            dip_wins=dip_wins,
            breakout_wins=breakout_wins,
            win_rate=len(winning_trades) / len(self.trades) * 100 if self.trades else 0,
            dip_win_rate=dip_wins / len(dip_trades) * 100 if dip_trades else 0,
            breakout_win_rate=breakout_wins / len(breakout_trades) * 100 if breakout_trades else 0,
            total_pnl_sol=total_pnl,
            total_pnl_percent=(total_pnl / self.initial_capital) * 100,
            max_drawdown=max_drawdown,
            trades=[asdict(t) for t in self.trades],
            market_condition_history=self.market_conditions + [self.mode_performance]
        )


async def run_adaptive_paper_trading(target_trades: int = 10):
    """Run adaptive paper trading simulation"""
    
    print("\n" + "="*80)
    print("  ADAPTIVE PAPER TRADING BOT - Solana Meme Coins")
    print("  SIMULATION MODE (Realistic Market Conditions)")
    print("="*80)
    print("\n📊 Strategy Configuration:")
    print("   • Capital: 1.0 SOL")
    print("   • Mode Selection: Dynamic (DIP vs BREAKOUT)")
    print("   • Entry: EMA-based trend detection + confirmation")
    print("   • Exit: Scale 50% at +20%, Trail remainder at -10%")
    print("   • Stop Loss: Hard stop at -7%")
    print("   • Timeframe: 15m candles equivalent")
    print("   • Target: Minimum 10 trades")
    print(f"\n{'='*80}\n")
    
    # Initialize
    simulator = RealisticCryptoSimulator()
    strategy = AdaptiveStrategy(initial_capital=1.0)
    
    print("🚀 Starting adaptive paper trading simulation...")
    print("   Simulating 15m candles for 10 meme coins")
    print("   Realistic market regimes: bullish, bearish, ranging\n")
    
    iteration = 0
    
    while len(strategy.trades) < target_trades:
        iteration += 1
        
        # Update all coin prices
        simulator.update_all()
        
        # Process each coin
        for coin in simulator.COINS:
            candles = simulator.get_candles(coin)
            
            if len(candles) < 20:
                continue
            
            # Detect market condition
            mode, condition = strategy.detect_market_condition(candles)
            
            # Manage existing position
            if coin in strategy.positions:
                current_price = candles[-1].close
                exit_reason = strategy.manage_position(strategy.positions[coin], current_price)
                
                if exit_reason == "scale_50":
                    pnl = strategy.partial_scale_out(coin, current_price, candles)
                    trade = strategy.positions[coin]
                    print(f"  📊 SCALE 50% {coin} @ ${current_price:.8f} | "
                          f"Mode: {trade.mode.value.upper()} | "
                          f"PnL: {pnl:+.4f} SOL | "
                          f"Score: {condition['trend_score']:.1f}")
                
                elif exit_reason:
                    trade = strategy.close_position(coin, current_price, exit_reason)
                    emoji = "🟢" if trade.pnl_sol > 0 else "🔴"
                    print(f"  {emoji} CLOSE {coin} @ ${current_price:.8f} | "
                          f"{exit_reason.upper()} | "
                          f"Mode: {trade.mode.value.upper()} | "
                          f"PnL: {trade.pnl_sol:+.4f} SOL ({trade.pnl_percent:+.2f}%)")
                    print(f"      Balance: {strategy.balance_sol:.4f} SOL | "
                          f"Trades: {len(strategy.trades)}/{target_trades}")
            
            # Look for new entry (max 3 positions)
            elif len(strategy.positions) < 3:
                signal = None
                
                if mode == Mode.BREAKOUT:
                    signal = strategy.find_breakout_entry(candles, coin)
                    signal_type = "🚀 BREAKOUT"
                else:
                    signal = strategy.find_dip_entry(candles, coin)
                    signal_type = "📉 DIP"
                
                if signal:
                    trade = strategy.open_position(signal, mode)
                    if trade:
                        print(f"  {signal_type} ENTRY {coin} @ ${trade.entry_price:.8f}")
                        print(f"      Mode: {mode.value.upper()} | Score: {condition['trend_score']:.1f} | "
                              f"Size: {trade.position_size_sol:.4f} SOL")
        
        # Store market condition
        strategy.market_conditions.append({
            "iteration": iteration,
            "active_positions": len(strategy.positions),
            "closed_trades": len(strategy.trades),
            "balance": strategy.balance_sol
        })
        
        # Periodically print status
        if iteration % 20 == 0 and strategy.positions:
            print(f"\n  {'-'*60}")
            print(f"  Status: Iteration {iteration} | Trades: {len(strategy.trades)}/{target_trades}")
            print(f"  Balance: {strategy.balance_sol:.4f} SOL | Positions: {len(strategy.positions)}")
            for c, t in strategy.positions.items():
                current_price = simulator.get_current_prices()[c]
                pnl_pct = (current_price - t.entry_price) / t.entry_price * 100
                print(f"    {c}: Entry ${t.entry_price:.8f} | Current ${current_price:.8f} | "
                      f"PnL: {pnl_pct:+.2f}% | Scaled: {t.scaled}")
            print(f"  {'-'*60}\n")
        
        await asyncio.sleep(0.05)  # Fast simulation
    
    # Close any remaining positions
    print(f"\n{'='*80}")
    print("  FINALIZING ADAPTIVE PAPER TRADING SESSION")
    print(f"{'='*80}\n")
    
    for coin in list(strategy.positions.keys()):
        current_price = simulator.get_current_prices()[coin]
        trade = strategy.close_position(coin, current_price, "session_end")
        emoji = "🟢" if trade.pnl_sol > 0 else "🔴"
        print(f"  {emoji} CLOSE {coin} @ ${current_price:.8f} (Session End) | "
              f"PnL: {trade.pnl_sol:+.4f} SOL")
    
    # Generate final results
    results = strategy.get_session_results()
    
    # Save to file
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_file = f"/home/skux/.openclaw/workspace/adaptive_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(asdict(results), f, indent=2, default=str)
    
    # Print final report
    print(f"\n{'='*80}")
    print("  FINAL RESULTS - ADAPTIVE STRATEGY")
    print(f"{'='*80}\n")
    
    print(f"📊 CAPITAL PERFORMANCE:")
    print(f"   Initial:  {results.initial_balance:.4f} SOL")
    print(f"   Final:    {results.final_balance:.4f} SOL")
    print(f"   P&L:      {results.total_pnl_sol:+.4f} SOL ({results.total_pnl_percent:+.2f}%)")
    print(f"   Max DD:   {results.max_drawdown:.2f}%")
    
    print(f"\n📈 TRADE STATISTICS:")
    print(f"   Total:  {results.total_trades} trades")
    print(f"   Win Rate: {results.win_rate:.1f}%")
    print(f"   Wins:   {results.winning_trades}")
    print(f"   Losses: {results.losing_trades}")
    
    print(f"\n🔀 MODE COMPARISON:")
    print(f"   DIP Mode ({results.dip_trades} trades):")
    print(f"     Win Rate: {results.dip_win_rate:.1f}% ({results.dip_wins}W)")
    print(f"     P&L:      {strategy.mode_performance[Mode.DIP.value]['pnl']:+.4f} SOL")
    print(f"     Avg/Trade: {strategy.mode_performance[Mode.DIP.value]['pnl']/results.dip_trades if results.dip_trades > 0 else 0:+.4f} SOL")
    
    print(f"   BREAKOUT Mode ({results.breakout_trades} trades):")
    print(f"     Win Rate: {results.breakout_win_rate:.1f}% ({results.breakout_wins}W)")
    print(f"     P&L:      {strategy.mode_performance[Mode.BREAKOUT.value]['pnl']:+.4f} SOL")
    print(f"     Avg/Trade: {strategy.mode_performance[Mode.BREAKOUT.value]['pnl']/results.breakout_trades if results.breakout_trades > 0 else 0:+.4f} SOL")
    
    # Determine winner mode
    if results.dip_trades >= 2 and results.breakout_trades >= 2:
        if results.dip_win_rate > results.breakout_win_rate and results.breakout_trades > 0:
            winner = "DIP"
            reason = f"Higher win rate ({results.dip_win_rate:.0f}% vs {results.breakout_win_rate:.0f}%)"
        elif results.breakout_win_rate > results.dip_win_rate:
            winner = "BREAKOUT"
            reason = f"Higher win rate ({results.breakout_win_rate:.0f}% vs {results.dip_win_rate:.0f}%)"
        elif strategy.mode_performance[Mode.DIP.value]['pnl'] > strategy.mode_performance[Mode.BREAKOUT.value]['pnl']:
            winner = "DIP"
            reason = "Better P&L performance"
        else:
            winner = "BREAKOUT"
            reason = "Better P&L performance"
        
        print(f"\n🏆 BETTER MODE: {winner} Strategy")
        print(f"   Reason: {reason}")
    else:
        print(f"\n⚠️  INSUFFICIENT MODE DATA:")
        print(f"   Need 2+ trades in each mode for comparison")
    
    print(f"\n{'='*80}\n")
    
    return results


if __name__ == "__main__":
    target_trades = int(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 10
    asyncio.run(run_adaptive_paper_trading(target_trades=target_trades))