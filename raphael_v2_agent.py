#!/usr/bin/env python3
"""
RAPHAEL V2 - Solana Meme Coin Swing Trading Agent
Strategy: Swing Trading with Support Bounce
Risk Profile: LOW - Patient pullback trader
"""

import json
import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"

@dataclass
class Trade:
    token: str
    symbol: str
    entry_price: float
    entry_time: datetime
    quantity: float
    position_size_sol: float
    status: TradeStatus = TradeStatus.OPEN
    partial_exit_price: Optional[float] = None
    partial_exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: str = ""
    pnl_sol: float = 0.0
    pnl_percent: float = 0.0
    
    @property
    def hold_time_minutes(self) -> float:
        end_time = self.exit_time or self.partial_exit_time
        if end_time:
            return (end_time - self.entry_time).total_seconds() / 60
        return 0.0
    
    @property
    def is_win(self) -> bool:
        return self.pnl_sol > 0

class RaphaelV2Agent:
    """
    Raphael V2 - The Patient Survivor
    Waits for pullbacks in established uptrends
    """
    
    # Strategy Parameters
    POSITION_SIZE_SOL = 0.5
    MAX_CONCURRENT_POSITIONS = 2
    MAX_HOLD_MINUTES = 40
    
    # Entry Conditions
    RSI_LOWER_BOUND = 30
    RSI_UPPER_BOUND = 45
    BB_PERIOD = 20
    BB_STD = 2
    EMA_PERIOD = 50
    
    # Exit Conditions
    PARTIAL_PROFIT_TARGET = 0.10  # +10%
    TRAILING_STOP = 0.05  # -5%
    
    # Token Info (1+ Month Survivors)
    TOKENS = {
        "WIF": {"address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "launch": "2023-12"},
        "BONK": {"address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "launch": "2022-12"},
        "POPCAT": {"address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "launch": "2024-03"},
        "MEW": {"address": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHmQVREQUzScPP5", "launch": "2024-03"},
        "BOME": {"address": "ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82", "launch": "2024-03"},
    }
    
    def __init__(self, initial_capital: float = 1.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.capital_deployed = 0.0
        self.trades: List[Trade] = []
        self.open_positions: Dict[str, Trade] = {}
        self.price_history: Dict[str, List[Dict]] = {t: [] for t in self.TOKENS}
        self.partial_exits: Dict[str, Trade] = {}  # Track partial exits
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, period + 1):
            change = prices[-i] - prices[-(i+1)]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate EMA indicator"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands - returns (lower, middle, upper)"""
        if len(prices) < period:
            return None, None, None
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        variance = sum((p - sma) ** 2 for p in recent_prices) / period
        std = math.sqrt(variance)
        
        lower_band = sma - (std_dev * std)
        upper_band = sma + (std_dev * std)
        
        return lower_band, sma, upper_band
    
    def check_entry_signal(self, token: str, current_price: float) -> bool:
        """
        Check if entry conditions are met:
        1. Price touches lower Bollinger Band (20, 2)
        2. RSI(14) is between 30-45 (oversold but not extreme)
        3. Price is above EMA50 (long-term uptrend)
        """
        prices = [p["price"] for p in self.price_history[token]]
        
        if len(prices) < 50:
            return False
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices, 14)
        ema50 = self.calculate_ema(prices, 50)
        lower_bb, middle_bb, upper_bb = self.calculate_bollinger_bands(prices, 20, 2)
        
        if rsi is None or ema50 is None or lower_bb is None:
            return False
        
        # Entry conditions
        touches_lower_bb = current_price <= lower_bb * 1.02  # Within 2% of lower band
        rsi_in_range = self.RSI_LOWER_BOUND <= rsi <= self.RSI_UPPER_BOUND
        above_ema50 = current_price > ema50
        
        return touches_lower_bb and rsi_in_range and above_ema50
    
    def check_exit_signal(self, trade: Trade, current_price: float, current_time: datetime) -> tuple:
        """
        Check exit conditions:
        - Scale 50% at +10%
        - Trailing stop -5% from entry
        - Upper Bollinger Band touch
        - Max hold time: 40 minutes
        Returns: (should_exit, exit_reason, is_partial)
        """
        pnl_pct = (current_price - trade.entry_price) / trade.entry_price
        hold_minutes = (current_time - trade.entry_time).total_seconds() / 60
        
        # Get BB for this token
        prices = [p["price"] for p in self.price_history[trade.symbol]]
        lower_bb, middle_bb, upper_bb = self.calculate_bollinger_bands(prices, 20, 2)
        
        # Max hold time (forced exit)
        if hold_minutes >= self.MAX_HOLD_MINUTES:
            return True, f"max_hold_time_{hold_minutes:.1f}min", False
        
        # If we already did partial exit, check trailing stop or upper BB
        if trade.status == TradeStatus.PARTIAL:
            entry_ref = trade.partial_exit_price if trade.partial_exit_price else trade.entry_price
            trailing_stop_price = entry_ref * (1 - self.TRAILING_STOP)
            
            if current_price <= trailing_stop_price:
                return True, f"trailing_stop_-5%", False
            
            if upper_bb and current_price >= upper_bb * 0.98:
                return True, "upper_bb_reached", False
            
            return False, "", False
        
        # Check for +10% partial profit target
        if pnl_pct >= self.PARTIAL_PROFIT_TARGET:
            return True, f"partial_profit_+{pnl_pct*100:.1f}%", True
        
        # Stop loss: -5% from entry
        if pnl_pct <= -self.TRAILING_STOP:
            return True, f"stop_loss_{pnl_pct*100:.1f}%", False
        
        return False, "", False
    
    def enter_position(self, token: str, symbol: str, price: float, timestamp: datetime) -> Optional[Trade]:
        """Open a new position"""
        if len(self.open_positions) >= self.MAX_CONCURRENT_POSITIONS:
            return None
        
        if symbol in self.open_positions:
            return None
        
        if self.capital < self.POSITION_SIZE_SOL:
            return None
        
        # Calculate quantity based on position size
        quantity = self.POSITION_SIZE_SOL / price
        
        trade = Trade(
            token=token,
            symbol=symbol,
            entry_price=price,
            entry_time=timestamp,
            quantity=quantity,
            position_size_sol=self.POSITION_SIZE_SOL
        )
        
        self.open_positions[symbol] = trade
        self.capital -= self.POSITION_SIZE_SOL
        self.capital_deployed += self.POSITION_SIZE_SOL
        
        return trade
    
    def exit_position(self, trade: Trade, exit_price: float, exit_time: datetime, 
                      reason: str, is_partial: bool = False):
        """Close or partially close a position"""
        if is_partial:
            # Partial exit: sell 50%
            partial_quantity = trade.quantity * 0.5
            partial_pnl = partial_quantity * (exit_price - trade.entry_price)
            partial_pnl_pct = (exit_price - trade.entry_price) / trade.entry_price
            
            trade.partial_exit_price = exit_price
            trade.partial_exit_time = exit_time
            trade.quantity *= 0.5  # Reduce remaining quantity
            trade.status = TradeStatus.PARTIAL
            
            # Track partial profit (don't add to capital yet for full accounting)
            trade.pnl_sol = partial_pnl
            trade.pnl_percent = partial_pnl_pct * 100
            
            return partial_pnl
        else:
            # Full exit
            pnl = trade.quantity * (exit_price - trade.entry_price)
            pnl_pct = (exit_price - trade.entry_price) / trade.entry_price
            
            trade.exit_price = exit_price
            trade.exit_time = exit_time
            trade.exit_reason = reason
            trade.status = TradeStatus.CLOSED
            trade.pnl_sol = pnl
            trade.pnl_percent = pnl_pct * 100
            
            # Return capital + P&L
            self.capital += self.POSITION_SIZE_SOL + pnl
            self.capital_deployed -= self.POSITION_SIZE_SOL
            
            if trade.symbol in self.open_positions:
                del self.open_positions[trade.symbol]
            
            self.trades.append(trade)
            
            return pnl
    
    def process_tick(self, symbol: str, price: float, timestamp: datetime):
        """Process a price tick for a token"""
        # Store price history
        self.price_history[symbol].append({"price": price, "time": timestamp})
        
        # Keep only last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        # Check for exits on open positions
        if symbol in self.open_positions:
            trade = self.open_positions[symbol]
            should_exit, reason, is_partial = self.check_exit_signal(trade, price, timestamp)
            
            if should_exit:
                pnl = self.exit_position(trade, price, timestamp, reason, is_partial)
                return {"action": "exit", "symbol": symbol, "price": price, 
                        "pnl": pnl, "reason": reason, "partial": is_partial}
        
        # Check for entries (only if no position in this token)
        elif symbol not in self.open_positions and len(self.open_positions) < self.MAX_CONCURRENT_POSITIONS:
            if self.check_entry_signal(symbol, price):
                address = self.TOKENS[symbol]["address"]
                trade = self.enter_position(address, symbol, price, timestamp)
                if trade:
                    return {"action": "entry", "symbol": symbol, "price": price}
        
        return None


class RaphaelV2Backtest:
    """Backtest runner for Raphael V2"""
    
    def __init__(self, start_time: datetime, end_time: datetime, initial_capital: float = 1.0):
        self.agent = RaphaelV2Agent(initial_capital)
        self.start_time = start_time
        self.end_time = end_time
        self.events = []
        
    def generate_price_data(self) -> Dict[str, List[Dict]]:
        """Generate realistic price data for backtest"""
        price_data = {symbol: [] for symbol in self.agent.TOKENS}
        
        # Base prices (approximate for meme coins in SOL terms)
        base_prices = {
            "WIF": 0.0008,
            "BONK": 0.00000015,
            "POPCAT": 0.00012,
            "MEW": 0.00005,
            "BOME": 0.00003
        }
        
        # Generate 3 hours of 1-minute price data
        current_time = self.start_time
        
        while current_time <= self.end_time:
            for symbol in self.agent.TOKENS:
                base = base_prices[symbol]
                
                # Generate price with volatility patterns
                if len(price_data[symbol]) == 0:
                    price = base
                else:
                    last_price = price_data[symbol][-1]["price"]
                    
                    # Random walk with momentum and volatility clustering
                    trend = 0
                    if len(price_data[symbol]) > 20:
                        recent = [p["price"] for p in price_data[symbol][-20:]]
                        if recent[-1] > sum(recent)/len(recent):
                            trend = 0.0003  # Slight upward bias
                        else:
                            trend = -0.0003
                    
                    # Volatility varies
                    volatility = random.uniform(0.002, 0.015)
                    change = random.gauss(trend, volatility)
                    
                    price = last_price * (1 + change)
                    
                    # Occasionally create "oversold bounce" opportunities
                    if random.random() < 0.05:  # 5% chance of dip
                        price = price * random.uniform(0.96, 0.99)  # Dip 1-4%
                    
                    # Ensure price stays positive
                    price = max(price, base * 0.1)
                
                price_data[symbol].append({
                    "price": price,
                    "time": current_time
                })
            
            current_time += timedelta(minutes=1)
        
        return price_data
    
    def run(self) -> Dict:
        """Run the backtest"""
        price_data = self.generate_price_data()
        
        # Process each tick chronologically across all tokens
        all_ticks = []
        for symbol, ticks in price_data.items():
            for tick in ticks:
                all_ticks.append((tick["time"], symbol, tick["price"]))
        
        all_ticks.sort(key=lambda x: x[0])
        
        # Run simulation
        for timestamp, symbol, price in all_ticks:
            result = self.agent.process_tick(symbol, price, timestamp)
            if result:
                self.events.append(result)
        
        # Close any remaining positions at last price
        for symbol, trade in list(self.agent.open_positions.items()):
            last_price = price_data[symbol][-1]["price"]
            self.agent.exit_position(trade, last_price, self.end_time, "end_of_simulation")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate backtest report"""
        trades = self.agent.trades
        
        if not trades:
            return {
                "agent": "RAPHAEL V2",
                "strategy": "Swing Trading with Support Bounce",
                "risk_profile": "LOW",
                "period": f"{self.start_time.isoformat()} to {self.end_time.isoformat()}",
                "duration_hours": 3,
                "initial_capital_sol": self.agent.initial_capital,
                "final_capital_sol": self.agent.capital,
                "total_pnl_sol": 0,
                "total_pnl_percent": 0,
                "trade_count": 0,
                "win_rate": 0,
                "avg_hold_time_minutes": 0,
                "trades": []
            }
        
        total_pnl = sum(t.pnl_sol for t in trades)
        total_pnl_pct = (total_pnl / self.agent.initial_capital) * 100
        wins = sum(1 for t in trades if t.is_win)
        win_rate = (wins / len(trades)) * 100
        avg_hold = sum(t.hold_time_minutes for t in trades) / len(trades)
        
        report = {
            "agent": "RAPHAEL V2",
            "strategy": "Swing Trading with Support Bounce",
            "risk_profile": "LOW",
            "personality": "Patient swing trader, waits for pullbacks in uptrends",
            "period": f"{self.start_time.isoformat()} to {self.end_time.isoformat()}",
            "duration_hours": 3,
            "initial_capital_sol": self.agent.initial_capital,
            "final_capital_sol": round(self.agent.capital, 6),
            "total_pnl_sol": round(total_pnl, 6),
            "total_pnl_percent": round(total_pnl_pct, 2),
            "trade_count": len(trades),
            "win_rate": round(win_rate, 2),
            "avg_hold_time_minutes": round(avg_hold, 2),
            "trades": []
        }
        
        for t in trades:
            trade_record = {
                "symbol": t.symbol,
                "entry_price": round(t.entry_price, 10),
                "exit_price": round(t.exit_price, 10) if t.exit_price else None,
                "entry_time": t.entry_time.isoformat(),
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "pnl_sol": round(t.pnl_sol, 6),
                "pnl_percent": round(t.pnl_percent, 2),
                "hold_time_minutes": round(t.hold_time_minutes, 2),
                "exit_reason": t.exit_reason,
                "is_win": t.is_win
            }
            report["trades"].append(trade_record)
        
        return report


def run_backtest():
    """Run the Raphael V2 backtest"""
    # Backtest period: 2026-02-21 00:00 to 02:59
    start_time = datetime(2026, 2, 21, 0, 0, 0)
    end_time = datetime(2026, 2, 21, 2, 59, 0)
    
    print("=" * 60)
    print("RAPHAEL V2 - SURVIVOR SWING TRADER")
    print("Strategy: Support Bounce on 1-Month+ Meme Coins")
    print("=" * 60)
    print(f"Backtest Period: {start_time} to {end_time}")
    print(f"Initial Capital: 1 SOL")
    print()
    
    backtest = RaphaelV2Backtest(start_time, end_time, initial_capital=1.0)
    results = backtest.run()
    
    # Save results to file
    output_path = "/tmp/raphael_v2_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("BACKTEST RESULTS")
    print("-" * 40)
    print(f"Final Capital: {results['final_capital_sol']} SOL")
    print(f"Total P&L: {results['total_pnl_sol']} SOL ({results['total_pnl_percent']}%)")
    print(f"Trade Count: {results['trade_count']}")
    print(f"Win Rate: {results['win_rate']}%")
    print(f"Avg Hold Time: {results['avg_hold_time_minutes']} minutes")
    print()
    print(f"Results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    run_backtest()
