#!/usr/bin/env python3
"""
Adaptive (Hybrid) Paper Trading Bot for Solana Meme Coins
Switches between DIP and BREAKOUT modes based on market conditions detected in real-time.

Strategy:
- If market trending UP -> use BREAKOUT (buy momentum)
- If market choppy/ranging -> use DIP (buy dips)
- Entry: Dynamically adjust based on EMA trend
- Exit: Scale 50% at +20%, trail remaining at -10% from peak
- Stop: Hard stop -7%
- Timeframe: 15m candles

Tracks: Win rate, P&L, trade count, which mode worked better
"""

import json
import time
import asyncio
import aiohttp
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum
import statistics

# Birdeye API Configuration
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BIRDEYE_BASE_URL = "https://public-api.birdeye.so"

# Solana Meme Coins for Paper Trading
MEME_COINS = {
    "BONK": {
        "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "decimals": 5,
        "symbol": "BONK"
    },
    "WIF": {
        "address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "decimals": 6,
        "symbol": "WIF"
    },
    "POPCAT": {
        "address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "decimals": 9,
        "symbol": "POPCAT"
    },
    "BOME": {
        "address": "ukHH6c7mMyiWCf1b9pnWe25TSpkddtuaLquVFmFwYNL",
        "decimals": 6,
        "symbol": "BOME"
    },
    "SLERF": {
        "address": "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3",
        "decimals": 9,
        "symbol": "SLERF"
    },
    "PONKE": {
        "address": "5z3EqYQo9TvGMWgEovD86zTX9T3dsTuzotWj7b6JHRnQ",
        "decimals": 9,
        "symbol": "PONKE"
    },
    "MYRO": {
        "address": "MYROrGBDSZR4zPwsbg55ihPjFy2iKgrWY4hA5V5Z9wK",
        "decimals": 9,
        "symbol": "MYRO"
    },
    "WEN": {
        "address": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
        "decimals": 5,
        "symbol": "WEN"
    },
    "TURBO": {
        "address": "8n8WWeE9r4AjsC6Fx4jPNUZg1tP2qSHTsJh6pMFX1xtb",
        "decimals": 6,
        "symbol": "TURBO"
    },
    "GME": {
        "address": "8wXtPeU6557ETkp9WHFY1n1EcRTNo1KLVBFRv7EZe6jK",
        "decimals": 9,
        "symbol": "GME"
    }
}


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
    mode: Mode  # BREAKOUT or DIP
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
    
    def __post_init__(self):
        if self.peak_price == 0.0:
            self.peak_price = self.entry_price
        if self.trailing_stop_price == 0.0:
            self.trailing_stop_price = self.entry_price * 0.93  # -7% hard stop


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


class BirdeyeDataFetcher:
    """Fetch OHLCV data from Birdeye API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": api_key,
            "Accept": "application/json"
        }
    
    async def fetch_ohlcv(self, token_address: str, timeframe: str = "15m", 
                        limit: int = 100) -> List[Candle]:
        """Fetch OHLCV data from Birdeye"""
        url = f"{BIRDEYE_BASE_URL}/defi/ohlcv"
        params = {
            "address": token_address,
            "type": timeframe,
            "time_from": int(time.time()) - (limit * 900),  # 15min intervals
            "time_to": int(time.time())
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success") and "data" in data:
                            items = data["data"].get("items", [])
                            candles = []
                            for item in items:
                                candles.append(Candle(
                                    timestamp=item.get("unixTime", 0),
                                    open=item.get("o", 0),
                                    high=item.get("h", 0),
                                    low=item.get("l", 0),
                                    close=item.get("c", 0),
                                    volume=item.get("v", 0)
                                ))
                            return candles
            return []
        except Exception as e:
            print(f"Error fetching OHLCV: {e}")
            return []
    
    async def fetch_price(self, token_address: str) -> Optional[float]:
        """Fetch current price"""
        url = f"{BIRDEYE_BASE_URL}/defi/price"
        params = {"address": token_address}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success"):
                            return data["data"].get("value")
            return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None


class AdaptiveStrategy:
    """
    Adaptive strategy that switches between DIP and BREAKOUT modes
    based on real-time market conditions.
    """
    
    def __init__(self, initial_capital: float = 1.0):
        self.initial_capital = initial_capital
        self.balance_sol = initial_capital
        self.peak_balance = initial_capital
        self.positions: Dict[str, Trade] = {}
        self.trades: List[Trade] = []
        self.trade_counter = 0
        self.session_start = datetime.now(timezone.utc).isoformat()
        
        # Market condition tracking
        self.market_trend_score = 0  # Positive = uptrend, Negative = downtrend
        self.volatility_regime = None  # "low", "normal", "high"
        self.current_mode = None  # Will be set by detect_market_condition
        
        # Strategy parameters
        self.ema_fast_period = 9
        self.ema_slow_period = 21
        self.atr_period = 14
        
        # Exit parameters
        self.scale_target = 0.20  # +20%
        self.trailing_stop_pct = 0.10  # -10% from peak
        self.hard_stop_pct = 0.07  # -7% hard stop
        
        # Results tracking
        self.mode_performance = {
            Mode.DIP.value: {"trades": 0, "wins": 0, "pnl": 0.0},
            Mode.BREAKOUT.value: {"trades": 0, "wins": 0, "pnl": 0.0}
        }
    
    def generate_trade_id(self) -> str:
        self.trade_counter += 1
        return f"ADAPTIVE_{int(time.time())}_{self.trade_counter}"
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA for given prices"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_atr(self, candles: List[Candle], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return 0
        
        tr_values = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i-1].close
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            tr_values.append(max(tr1, tr2, tr3))
        
        return sum(tr_values[-period:]) / min(period, len(tr_values))
    
    def detect_market_condition(self, candles: List[Candle]) -> Tuple[Mode, Dict]:
        """
        Detect market condition and return current mode.
        
        Returns:
            Tuple of (Mode, condition_details_dict)
        """
        if len(candles) < 30:
            return Mode.DIP, {"reason": "insufficient_data", "confidence": 0}
        
        closes = [c.close for c in candles]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(closes, self.ema_fast_period)
        ema_slow = self.calculate_ema(closes, self.ema_slow_period)
        
        # Calculate trend strength
        price_changes = [(closes[i] - closes[i-1]) / closes[i-1] * 100 
                        for i in range(1, len(closes))]
        
        # Recent trend (last 10 candles)
        recent_changes = price_changes[-10:]
        avg_recent_change = sum(recent_changes) / len(recent_changes)
        
        # Overall trend (last 30 candles)
        overall_changes = price_changes[-30:]
        avg_overall_change = sum(overall_changes) / len(overall_changes)
        
        # Volatility
        volatility = statistics.stdev(price_changes[-20:]) if len(price_changes) >= 20 else 0
        
        # Trend consistency (are we consistently making higher highs/lows?)
        higher_highs = sum(1 for i in range(-10, -1) 
                          if candles[i].high > candles[i-1].high)
        higher_lows = sum(1 for i in range(-10, -1) 
                         if candles[i].low > candles[i-1].low)
        
        trend_score = 0
        
        # EMA alignment
        if ema_fast > ema_slow * 1.02:  # Fast EMA 2% above slow
            trend_score += 3
        elif ema_fast > ema_slow:
            trend_score += 1
        elif ema_fast < ema_slow * 0.98:  # Fast EMA 2% below slow
            trend_score -= 3
        elif ema_fast < ema_slow:
            trend_score -= 1
        
        # Recent momentum
        if avg_recent_change > 2:
            trend_score += 2
        elif avg_recent_change > 0.5:
            trend_score += 1
        elif avg_recent_change < -2:
            trend_score -= 2
        elif avg_recent_change < -0.5:
            trend_score -= 1
        
        # Pattern detection
        if higher_highs >= 6 and higher_lows >= 6:
            trend_score += 2  # Strong uptrend pattern
        elif higher_highs <= 3 and higher_lows <= 3:
            trend_score -= 2  # Downtrend pattern
        else:
            trend_score -= 0.5  # Choppy/ranging
        
        # Determine mode
        if trend_score >= 3:
            mode = Mode.BREAKOUT
            confidence = min(trend_score / 5, 1.0)
        elif trend_score <= -2:
            mode = Mode.DIP  # Buy dips in downtrend
            confidence = min(abs(trend_score) / 5, 1.0)
        else:
            mode = Mode.DIP  # Default to DIP in choppy/ranging markets
            confidence = 0.5
        
        condition_details = {
            "mode": mode.value,
            "trend_score": trend_score,
            "confidence": confidence,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "avg_recent_change": avg_recent_change,
            "volatility": volatility,
            "higher_highs": higher_highs,
            "higher_lows": higher_lows,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return mode, condition_details
    
    def find_dip_entry(self, candles: List[Candle], coin: str) -> Optional[Dict]:
        """
        Find dip entry opportunities.
        Criteria:
        - Price has pulled back from recent high
        - Bullish reversal candle pattern
        - Within uptrend context or strong support
        """
        if len(candles) < 10:
            return None
        
        current = candles[-1]
        prev = candles[-2]
        
        # Calculate pullback from recent high
        recent_high = max(c.high for c in candles[-10:])
        pullback_pct = (recent_high - current.close) / recent_high * 100
        
        # Check for dip criteria
        is_dip = False
        
        # Criteria 1: Significant pullback (5-20%)
        if 3 <= pullback_pct <= 20:
            # Criteria 2: Recent candle shows reversal/bottoming
            if current.close > current.open:  # Green candle
                body_pct = (current.close - current.open) / (current.high - current.low) * 100
                if body_pct > 30:  # Decent bullish body
                    is_dip = True
            
            # Criteria 3: Hammer pattern (long lower wick)
            lower_wick = min(current.close, current.open) - current.low
            body = abs(current.close - current.open)
            if lower_wick > body * 2:  # Long lower wick
                is_dip = True
        
        if not is_dip:
            return None
        
        # Calculate entry parameters
        entry_price = current.close
        
        # ATR-based stop loss
        atr = self.calculate_atr(candles, 10)
        stop_distance = max(atr * 1.5, entry_price * 0.03)  # 1.5x ATR or 3%
        stop_loss = entry_price - stop_distance
        
        # Ensure hard stop is respected
        hard_stop = entry_price * (1 - self.hard_stop_pct)
        stop_loss = max(stop_loss, hard_stop)
        
        return {
            "coin": coin,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": entry_price * 1.25,  # 25% target
            "signal": "dip_reversal",
            "pullback_pct": pullback_pct,
            "confidence": min(pullback_pct / 15, 1.0)
        }
    
    def find_breakout_entry(self, candles: List[Candle], coin: str) -> Optional[Dict]:
        """
        Find breakout entry opportunities.
        Criteria:
        - Breaking above recent resistance
        - Volume confirmation
        - EMA support
        """
        if len(candles) < 15:
            return None
        
        current = candles[-1]
        prev = candles[-2]
        
        # Calculate recent resistance
        recent_candles = candles[-15:-1]
        resistance = max(c.high for c in recent_candles)
        
        # Breakout criteria
        breakout_threshold = resistance * 1.02  # 2% breakout
        
        if current.close < breakout_threshold:
            return None
        
        # Volume check
        recent_volume = sum(c.volume for c in candles[-5:]) / 5
        prev_volume = sum(c.volume for c in candles[-10:-5]) / 5
        volume_spike = recent_volume / prev_volume if prev_volume > 0 else 1
        
        if volume_spike < 1.3:  # Need 30% volume increase
            return None
        
        # EMA confirmation
        closes = [c.close for c in candles]
        ema_fast = self.calculate_ema(closes, 9)
        
        if current.close < ema_fast * 0.98:  # Should be above EMA
            return None
        
        # Calculate entry parameters
        entry_price = current.close
        stop_loss = entry_price * (1 - self.hard_stop_pct)  # Hard stop
        
        return {
            "coin": coin,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": entry_price * 1.20,  # 20% target
            "signal": "momentum_breakout",
            "volume_spike": volume_spike,
            "confidence": min(volume_spike / 3, 1.0)
        }
    
    def open_position(self, signal: Dict, mode: Mode) -> Optional[Trade]:
        """Open a new paper position"""
        coin = signal["coin"]
        
        # Check if already in position
        if coin in self.positions:
            return None
        
        # Calculate position size (max 0.4 SOL per trade)
        position_size = min(self.balance_sol * 0.4, self.balance_sol - 0.1)
        if position_size < 0.1:
            return None
        
        entry_price = signal["entry_price"]
        stop_loss = signal["stop_loss"]
        
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
        """
        Manage open position and return exit reason if closed.
        Returns exit reason or None if position remains open.
        """
        entry = trade.entry_price
        
        # Update peak price
        if current_price > trade.peak_price:
            trade.peak_price = current_price
            # Update trailing stop
            new_trailing = trade.peak_price * (1 - self.trailing_stop_pct)
            trade.trailing_stop_price = max(new_trailing, trade.trailing_stop_price)
        
        current_pnl_pct = (current_price - entry) / entry
        
        # Check hard stop first
        hard_stop_price = entry * (1 - self.hard_stop_pct)
        if current_price <= hard_stop_price:
            return "hard_stop"
        
        # Check for scale out at +20%
        if not trade.scaled and current_pnl_pct >= self.scale_target:
            return "scale_50"
        
        # Check trailing stop
        if current_price <= trade.trailing_stop_price:
            return "trailing_stop"
        
        return None
    
    def close_position(self, coin: str, exit_price: float, reason: str) -> Trade:
        """Close a position and calculate P&L"""
        if coin not in self.positions:
            return None
        
        trade = self.positions[coin]
        trade.exit_price = exit_price
        trade.exit_time = datetime.now(timezone.utc).isoformat()
        trade.exit_reason = reason
        
        # Calculate P&L
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        trade.pnl_sol = trade.position_size_sol * price_change_pct
        trade.pnl_percent = price_change_pct * 100
        
        # Update status
        if trade.pnl_sol > 0:
            trade.status = TradeStatus.TARGET_HIT
        else:
            trade.status = TradeStatus.STOPPED
        
        # Return funds to balance
        self.balance_sol += trade.position_size_sol + trade.pnl_sol
        
        # Track mode performance
        mode_key = trade.mode.value
        self.mode_performance[mode_key]["trades"] += 1
        self.mode_performance[mode_key]["pnl"] += trade.pnl_sol
        if trade.pnl_sol > 0:
            self.mode_performance[mode_key]["wins"] += 1
        
        # Track peak balance and drawdown
        if self.balance_sol > self.peak_balance:
            self.peak_balance = self.balance_sol
        current_drawdown = (self.peak_balance - self.balance_sol) / self.peak_balance * 100
        
        self.trades.append(trade)
        del self.positions[coin]
        
        return trade
    
    def partial_scale_out(self, coin: str, exit_price: float) -> float:
        """Scale out 50% of position at +20%"""
        if coin not in self.positions:
            return 0
        
        trade = self.positions[coin]
        trade.scaled = True
        
        # Calculate 50% position value
        half_position = trade.position_size_sol * 0.5
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        pnl = half_position * price_change_pct
        
        # Return 50% to balance
        self.balance_sol += half_position + pnl
        trade.position_size_sol -= half_position
        
        return pnl
    
    def get_session_results(self) -> TradingSession:
        """Get trading session results"""
        winning_trades = [t for t in self.trades if t.pnl_sol > 0]
        losing_trades = [t for t in self.trades if t.pnl_sol <= 0]
        
        dip_trades = [t for t in self.trades if t.mode == Mode.DIP]
        breakout_trades = [t for t in self.trades if t.mode == Mode.BREAKOUT]
        
        dip_wins = sum(1 for t in dip_trades if t.pnl_sol > 0)
        breakout_wins = sum(1 for t in breakout_trades if t.pnl_sol > 0)
        
        total_pnl = sum(t.pnl_sol for t in self.trades)
        max_drawdown = (self.peak_balance - min(
            self.balance_sol, 
            self.peak_balance - max((t.pnl_sol for t in self.trades), default=0)
        )) / self.peak_balance * 100 if self.peak_balance > 0 else 0
        
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
            market_condition_history=self.mode_performance
        )
    
    def print_status(self):
        """Print current portfolio status"""
        print(f"\n{'='*70}")
        print(f"PORTFOLIO STATUS | {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        print(f"{'='*70}")
        print(f"Balance: {self.balance_sol:.4f} SOL")
        print(f"Peak Balance: {self.peak_balance:.4f} SOL")
        print(f"Current Drawdown: {((self.peak_balance - self.balance_sol) / self.peak_balance * 100):.2f}%")
        print(f"Open Positions: {len(self.positions)}")
        print(f"Closed Trades: {len(self.trades)}")
        
        if self.trades:
            wins = sum(1 for t in self.trades if t.pnl_sol > 0)
            pnl = sum(t.pnl_sol for t in self.trades)
            print(f"Win Rate: {wins}/{len(self.trades)} ({wins/len(self.trades)*100:.1f}%)")
            print(f"Total P&L: {pnl:+.4f} SOL")
        
        if self.positions:
            print(f"\n{'-'*70}")
            print("OPEN POSITIONS:")
            print(f"{'-'*70}")
            for coin, trade in self.positions.items():
                print(f"  {coin} | Mode: {trade.mode.value.upper()} | Entry: ${trade.entry_price:.6f}")
                print(f"       Size: {trade.position_size_sol:.4f} SOL | Scaled: {trade.scaled}")
                print(f"       Peak: ${trade.peak_price:.6f} | Trail Stop: ${trade.trailing_stop_price:.6f}")
        
        print(f"{'='*70}\n")


async def run_adaptive_paper_trading(target_trades: int = 10, max_duration_hours: float = 6):
    """
    Run adaptive paper trading until target trades reached or max duration exceeded.
    """
    print("\n" + "="*80)
    print("  ADAPTIVE PAPER TRADING BOT - Solana Meme Coins")
    print("="*80)
    print("\n📊 Strategy Configuration:")
    print("   • Capital: 1.0 SOL")
    print("   • Mode Selection: Dynamic (DIP vs BREAKOUT based on market conditions)")
    print("   • Entry: EMA-based trend detection + signal confirmation")
    print("   • Exit: Scale 50% at +20%, Trail remainder at -10% from peak")
    print("   • Stop Loss: Hard stop at -7%")
    print("   • Timeframe: 15m candles")
    print("   • Target: Minimum 10 trades")
    print(f"\n{'='*80}\n")
    
    # Initialize
    fetcher = BirdeyeDataFetcher(BIRDEYE_API_KEY)
    strategy = AdaptiveStrategy(initial_capital=1.0)
    
    start_time = time.time()
    max_duration_seconds = max_duration_hours * 3600
    
    # Trading loop
    iteration = 0
    
    print("🚀 Starting adaptive paper trading...")
    print("   Fetching real OHLCV data from Birdeye API")
    print("   Processing 15m candles for 10 meme coins\n")
    
    try:
        while (len(strategy.trades) < target_trades and 
               time.time() - start_time < max_duration_seconds):
            
            iteration += 1
            
            # Update each coin
            for coin_name, coin_data in MEME_COINS.items():
                address = coin_data["address"]
                
                # Fetch OHLCV data
                candles = await fetcher.fetch_ohlcv(address, timeframe="15m", limit=50)
                
                if len(candles) < 20:
                    continue
                
                # Detect market condition for this coin
                mode, condition = strategy.detect_market_condition(candles)
                
                # Manage existing position
                if coin_name in strategy.positions:
                    current_price = candles[-1].close
                    exit_reason = strategy.manage_position(strategy.positions[coin_name], current_price)
                    
                    if exit_reason == "scale_50":
                        pnl = strategy.partial_scale_out(coin_name, current_price)
                        trade = strategy.positions[coin_name]
                        print(f"  📊 SCALE 50% {coin_name} @ ${current_price:.6f} | "
                              f"Mode: {trade.mode.value.upper()} | PnL: {pnl:+.4f} SOL")
                    
                    elif exit_reason:
                        trade = strategy.close_position(coin_name, current_price, exit_reason)
                        emoji = "🟢" if trade.pnl_sol > 0 else "🔴"
                        print(f"  {emoji} CLOSE {coin_name} @ ${current_price:.6f} | "
                              f"Reason: {exit_reason} | "
                              f"Mode: {trade.mode.value.upper()} | "
                              f"PnL: {trade.pnl_sol:+.4f} SOL ({trade.pnl_percent:+.2f}%)")
                
                # Look for new entry (max 3 positions)
                elif len(strategy.positions) < 3:
                    signal = None
                    
                    if mode == Mode.BREAKOUT:
                        signal = strategy.find_breakout_entry(candles, coin_name)
                        signal_type = "🚀 BREAKOUT"
                    else:
                        signal = strategy.find_dip_entry(candles, coin_name)
                        signal_type = "📉 DIP"
                    
                    if signal:
                        trade = strategy.open_position(signal, mode)
                        if trade:
                            print(f"  {signal_type} ENTRY {coin_name} @ ${trade.entry_price:.6f} | "
                                  f"Mode: {mode.value.upper()} | "
                                  f"Size: {trade.position_size_sol:.4f} SOL | "
                                  f"Stop: ${trade.trailing_stop_price:.6f}")
                
                # Small delay between coins
                await asyncio.sleep(0.2)
            
            # Print status every 10 iterations (roughly every 2-3 min)
            if iteration % 10 == 0:
                strategy.print_status()
                
                # Print progress
                elapsed = (time.time() - start_time) / 60
                trades_done = len(strategy.trades)
                print(f"  ⏱️  Elapsed: {elapsed:.1f} min | Trades: {trades_done}/{target_trades} | "
                      f"Mode Stats: DIP={strategy.mode_performance[Mode.DIP.value]['trades']}, "
                      f"BREAKOUT={strategy.mode_performance[Mode.BREAKOUT.value]['trades']}")
            
            # Wait before next iteration
            await asyncio.sleep(15)  # 15 second loop interval
    
    except KeyboardInterrupt:
        print("\n⚠️ Trading interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error in trading loop: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close any remaining positions at current market price
        print(f"\n{'='*80}")
        print("  FINALIZING PAPER TRADING SESSION")
        print(f"{'='*80}\n")
        
        for coin_name, coin_data in list(MEME_COINS.items()):
            if coin_name in strategy.positions:
                try:
                    price = await fetcher.fetch_price(coin_data["address"])
                    if price:
                        trade = strategy.close_position(coin_name, price, "session_end")
                        print(f"  🔚 CLOSED {coin_name} @ ${price:.6f} (Session End) | "
                              f"PnL: {trade.pnl_sol:+.4f} SOL")
                except Exception as e:
                    print(f"  ⚠️ Could not close {coin_name}: {e}")
        
        # Generate and save results
        results = strategy.get_session_results()
        
        # Save to file
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        results_file = f"/home/skux/.openclaw/workspace/adaptive_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        # Print final results
        print(f"\n{'='*80}")
        print("  FINAL RESULTS - ADAPTIVE STRATEGY")
        print(f"{'='*80}\n")
        
        print(f"📊 PERFORMANCE SUMMARY:")
        print(f"   Session ID: {results.session_id}")
        print(f"   Duration: {(time.time() - start_time) / 60:.1f} minutes")
        print(f"   Initial Balance: {results.initial_balance:.4f} SOL")
        print(f"   Final Balance: {results.final_balance:.4f} SOL")
        print(f"   Total P&L: {results.total_pnl_sol:+.4f} SOL ({results.total_pnl_percent:+.2f}%)")
        print(f"   Max Drawdown: {results.max_drawdown:.2f}%")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades: {results.total_trades}")
        print(f"   Win Rate: {results.win_rate:.1f}% ({results.winning_trades}W / {results.losing_trades}L)")
        
        print(f"\n🔀 MODE PERFORMANCE:")
        print(f"   DIP Mode:")
        print(f"     • Trades: {results.dip_trades}")
        print(f"     • Win Rate: {results.dip_win_rate:.1f}%")
        print(f"     • P&L: {strategy.mode_performance[Mode.DIP.value]['pnl']:+.4f} SOL")
        print(f"   BREAKOUT Mode:")
        print(f"     • Trades: {results.breakout_trades}")
        print(f"     • Win Rate: {results.breakout_win_rate:.1f}%")
        print(f"     • P&L: {strategy.mode_performance[Mode.BREAKOUT.value]['pnl']:+.4f} SOL")
        
        # Determine which mode worked better
        if results.dip_trades >= 3 and results.breakout_trades >= 3:
            if results.dip_win_rate > results.breakout_win_rate:
                better_mode = "DIP"
                reason = f"higher win rate ({results.dip_win_rate:.1f}% vs {results.breakout_win_rate:.1f}%)"
            elif results.breakout_win_rate > results.dip_win_rate:
                better_mode = "BREAKOUT"
                reason = f"higher win rate ({results.breakout_win_rate:.1f}% vs {results.dip_win_rate:.1f}%)"
            elif strategy.mode_performance[Mode.DIP.value]['pnl'] > strategy.mode_performance[Mode.BREAKOUT.value]['pnl']:
                better_mode = "DIP"
                reason = "better P&L performance"
            else:
                better_mode = "BREAKOUT"
                reason = "better P&L performance"
            
            print(f"\n🏆 BETTER MODE: {better_mode}")
            print(f"   Reason: {reason}")
        else:
            print(f"\n🔍 INSUFFICIENT DATA:")
            print(f"   Need at least 3 trades in each mode to compare")
        
        print(f"\n💾 Results saved to: {results_file}")
        print(f"{'='*80}\n")
        
        return results


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    target_trades = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    max_hours = float(sys.argv[2]) if len(sys.argv) > 2 else 6
    
    # Run the adaptive paper trader
    asyncio.run(run_adaptive_paper_trading(
        target_trades=target_trades,
        max_duration_hours=max_hours
    ))