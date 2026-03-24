#!/usr/bin/env python3
"""
Solana Meme Coin Paper Trading System
Simulates real-time trading with price tracking and P&L calculation
"""

import json
import time
import random
import asyncio
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    STOPPED = "stopped"
    TARGET_HIT = "target_hit"

@dataclass
class Trade:
    id: str
    strategy: str
    coin: str
    entry_price: float
    position_size_sol: float
    stop_loss: float
    profit_target: float
    entry_time: str
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    status: TradeStatus = TradeStatus.OPEN
    pnl_sol: float = 0.0
    pnl_percent: float = 0.0
    exit_reason: str = ""
    partial_exits: List[Dict] = field(default_factory=list)

@dataclass
class StrategyResult:
    strategy_name: str
    start_time: str
    end_time: str
    initial_balance: float
    final_balance: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl_sol: float
    total_pnl_percent: float
    max_drawdown: float
    trades: List[Dict] = field(default_factory=list)

class PaperTrader:
    def __init__(self, strategy_name: str, initial_sol: float = 1.0):
        self.strategy_name = strategy_name
        self.balance_sol = initial_sol
        self.initial_sol = initial_sol
        self.trades: List[Trade] = []
        self.positions: Dict[str, Trade] = {}
        self.trade_counter = 0
        self.start_time = datetime.now().isoformat()
        self.peak_balance = initial_sol
        self.max_drawdown = 0.0
        
    def generate_trade_id(self) -> str:
        self.trade_counter += 1
        return f"{self.strategy_name}_{int(time.time())}_{self.trade_counter}"
    
    def open_position(self, coin: str, entry_price: float, position_size_sol: float, 
                      stop_loss: float, profit_target: float) -> Trade:
        """Open a new paper position"""
        if position_size_sol > self.balance_sol:
            return None
            
        trade = Trade(
            id=self.generate_trade_id(),
            strategy=self.strategy_name,
            coin=coin,
            entry_price=entry_price,
            position_size_sol=position_size_sol,
            stop_loss=stop_loss,
            profit_target=profit_target,
            entry_time=datetime.now().isoformat()
        )
        
        self.trades.append(trade)
        self.positions[coin] = trade
        self.balance_sol -= position_size_sol
        
        return trade
    
    def close_position(self, coin: str, exit_price: float, reason: str) -> Trade:
        """Close a position and calculate P&L"""
        if coin not in self.positions:
            return None
            
        trade = self.positions[coin]
        trade.exit_price = exit_price
        trade.exit_time = datetime.now().isoformat()
        trade.exit_reason = reason
        
        # Calculate P&L
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        trade.pnl_sol = trade.position_size_sol * price_change_pct
        trade.pnl_percent = price_change_pct * 100
        
        if trade.pnl_sol > 0:
            trade.status = TradeStatus.TARGET_HIT
        else:
            trade.status = TradeStatus.STOPPED if "stop" in reason.lower() else TradeStatus.CLOSED
            
        # Return funds to balance
        self.balance_sol += trade.position_size_sol + trade.pnl_sol
        
        # Update peak and drawdown
        if self.balance_sol > self.peak_balance:
            self.peak_balance = self.balance_sol
        current_drawdown = (self.peak_balance - self.balance_sol) / self.peak_balance * 100
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
            
        del self.positions[coin]
        return trade
    
    def partial_exit(self, coin: str, exit_price: float, percent_to_close: float, reason: str):
        """Close partial position (for scaling out)"""
        if coin not in self.positions:
            return None
            
        trade = self.positions[coin]
        amount_to_close = trade.position_size_sol * (percent_to_close / 100)
        
        price_change_pct = (exit_price - trade.entry_price) / trade.entry_price
        pnl = amount_to_close * price_change_pct
        
        trade.partial_exits.append({
            "exit_price": exit_price,
            "percent_closed": percent_to_close,
            "amount": amount_to_close,
            "pnl": pnl,
            "reason": reason,
            "time": datetime.now().isoformat()
        })
        
        trade.position_size_sol -= amount_to_close
        self.balance_sol += amount_to_close + pnl
        
        return trade
    
    def check_positions(self, current_prices: Dict[str, float]):
        """Check all open positions against stop/target"""
        closed = []
        for coin, trade in list(self.positions.items()):
            if coin not in current_prices:
                continue
                
            current_price = current_prices[coin]
            
            # Check stop loss
            if current_price <= trade.stop_loss:
                self.close_position(coin, current_price, "Stop Loss Hit")
                closed.append(coin)
                
            # Check profit target
            elif current_price >= trade.profit_target:
                self.close_position(coin, current_price, "Profit Target Hit")
                closed.append(coin)
                
        return closed
    
    def get_result(self) -> StrategyResult:
        """Get final strategy results"""
        winning = [t for t in self.trades if t.pnl_sol > 0]
        losing = [t for t in self.trades if t.pnl_sol <= 0]
        
        total_pnl = sum(t.pnl_sol for t in self.trades)
        
        return StrategyResult(
            strategy_name=self.strategy_name,
            start_time=self.start_time,
            end_time=datetime.now().isoformat(),
            initial_balance=self.initial_sol,
            final_balance=self.balance_sol,
            total_trades=len(self.trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=len(winning) / len(self.trades) * 100 if self.trades else 0,
            total_pnl_sol=total_pnl,
            total_pnl_percent=(total_pnl / self.initial_sol) * 100,
            max_drawdown=self.max_drawdown,
            trades=[asdict(t) for t in self.trades]
        )
    
    def save_results(self, filepath: str):
        """Save results to JSON"""
        result = self.get_result()
        with open(filepath, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        return filepath


class SolanaMemeCoinData:
    """Simulated meme coin data for paper trading"""
    
    # Popular Solana meme coins with realistic volatility profiles
    COINS = {
        "BONK": {"base_price": 0.000012, "volatility": 0.15, "market_cap": 850_000_000},
        "WIF": {"base_price": 1.85, "volatility": 0.12, "market_cap": 1_800_000_000},
        "POPCAT": {"base_price": 0.42, "volatility": 0.18, "market_cap": 420_000_000},
        "BOME": {"base_price": 0.0085, "volatility": 0.25, "market_cap": 580_000_000},
        "SLERF": {"base_price": 0.15, "volatility": 0.22, "market_cap": 75_000_000},
        "PONKE": {"base_price": 0.035, "volatility": 0.20, "market_cap": 25_000_000},
        "MYRO": {"base_price": 0.045, "volatility": 0.19, "market_cap": 40_000_000},
        "WEN": {"base_price": 0.000085, "volatility": 0.16, "market_cap": 55_000_000},
        "TURBO": {"base_price": 0.0042, "volatility": 0.21, "market_cap": 280_000_000},
        "GME": {"base_price": 0.012, "volatility": 0.28, "market_cap": 12_000_000},
    }
    
    def __init__(self):
        self.prices = {coin: data["base_price"] for coin, data in self.COINS.items()}
        self.price_history = {coin: [data["base_price"]] for coin, data in self.COINS.items()}
        self.candle_history = {coin: [] for coin in self.COINS}
        
    def update_prices(self):
        """Simulate price movements with realistic crypto volatility"""
        for coin, data in self.COINS.items():
            # Random walk with momentum
            volatility = data["volatility"]
            change = random.gauss(0, volatility * 0.3)
            
            # Add occasional large moves (breakouts/dumps)
            if random.random() < 0.08:  # 8% chance of big move
                change += random.choice([-1, 1]) * random.uniform(0.08, 0.25)
                
            new_price = self.prices[coin] * (1 + change)
            self.prices[coin] = max(new_price, data["base_price"] * 0.1)  # Floor at 10% of base
            self.price_history[coin].append(self.prices[coin])
            
            # Keep history manageable
            if len(self.price_history[coin]) > 100:
                self.price_history[coin].pop(0)
                
        return self.prices
    
    def get_candle_data(self, coin: str, periods: int = 3) -> List[Dict]:
        """Get recent candle data for pattern detection"""
        history = self.price_history[coin][-periods:]
        candles = []
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            change = (curr - prev) / prev * 100
            candles.append({
                "price": curr,
                "change_pct": change,
                "is_green": change > 0,
                "is_red": change < 0
            })
        return candles
    
    def get_dip_candidates(self, min_dip: float = -10, max_dip: float = -20) -> List[Dict]:
        """Find coins that have dipped significantly"""
        candidates = []
        for coin, data in self.COINS.items():
            history = self.price_history[coin]
            if len(history) >= 5:
                recent_high = max(history[-5:])
                current = self.prices[coin]
                dip_pct = (current - recent_high) / recent_high * 100
                if min_dip >= dip_pct >= max_dip:
                    candidates.append({
                        "coin": coin,
                        "current_price": current,
                        "dip_pct": dip_pct,
                        "market_cap": data["market_cap"]
                    })
        return candidates
    
    def get_breakout_candidates(self, min_green: float = 20) -> List[Dict]:
        """Find coins with big green candles (breakouts)"""
        candidates = []
        for coin in self.COINS:
            candles = self.get_candle_data(coin, periods=3)
            if candles and candles[-1]["is_green"]:
                change = candles[-1]["change_pct"]
                if change >= min_green:
                    # Check if breaking "resistance" (recent high)
                    history = self.price_history[coin][-10:-1]
                    if history:
                        recent_resistance = max(history)
                        if self.prices[coin] > recent_resistance * 1.05:
                            candidates.append({
                                "coin": coin,
                                "current_price": self.prices[coin],
                                "breakout_pct": change,
                                "market_cap": self.COINS[coin]["market_cap"]
                            })
        return candidates
    
    def get_momentum_dip_candidates(self) -> List[Dict]:
        """Find coins with first green after 2+ reds (momentum shift)"""
        candidates = []
        for coin in self.COINS:
            candles = self.get_candle_data(coin, periods=4)
            if len(candles) >= 3:
                # Last 2 were red, current is green
                if (candles[-3]["is_red"] and candles[-2]["is_red"] and candles[-1]["is_green"]):
                    candidates.append({
                        "coin": coin,
                        "current_price": self.prices[coin],
                        "momentum_shift": True,
                        "market_cap": self.COINS[coin]["market_cap"]
                    })
        return candidates


async def run_strategy_a(duration_minutes: int = 3):
    """Aggressive Breakout Strategy"""
    print(f"\n🚀 Starting Strategy A: Aggressive Breakout ({duration_minutes}min)")
    
    trader = PaperTrader("Strategy_A_Breakout", initial_sol=1.0)
    data = SolanaMemeCoinData()
    
    start_time = time.time()
    iterations = 0
    
    while time.time() - start_time < duration_minutes * 60:
        iterations += 1
        
        # Update market data
        prices = data.update_prices()
        
        # Check existing positions
        trader.check_positions(prices)
        
        # Look for breakout entries (max 3 positions)
        if len(trader.positions) < 3:
            candidates = data.get_breakout_candidates(min_green=20)
            for candidate in candidates:
                coin = candidate["coin"]
                if coin not in trader.positions:
                    entry = prices[coin]
                    stop = entry * 0.95  # 5% stop
                    target = entry * 1.10  # 10% profit
                    size = trader.balance_sol / (3 - len(trader.positions)) if trader.balance_sol > 0.1 else 0
                    
                    if size > 0.05:  # Minimum position size
                        trade = trader.open_position(coin, entry, size, stop, target)
                        if trade:
                            print(f"  📈 OPEN {coin} @ ${entry:.6f} | Size: {size:.3f} SOL | Stop: {stop:.6f} | Target: {target:.6f}")
        
        # Status update every 2 minutes
        if iterations % 20 == 0:
            elapsed = (time.time() - start_time) / 60
            print(f"  ⏱️  {elapsed:.1f}min | Balance: {trader.balance_sol:.3f} SOL | Positions: {len(trader.positions)}")
        
        await asyncio.sleep(0.1)  # 0.1 second intervals (30x speedup)
    
    # Close any remaining positions at current market price
    for coin in list(trader.positions.keys()):
        trader.close_position(coin, prices[coin], "Time Exit")
        print(f"  🔚 CLOSED {coin} @ ${prices[coin]:.6f} (Time Exit)")
    
    result = trader.save_results("/home/skux/phase1_strategy_A.json")
    print(f"  ✅ Strategy A Complete: {trader.get_result().total_pnl_sol:.3f} SOL P&L")
    return trader.get_result()


async def run_strategy_b(duration_minutes: int = 3):
    """Mean Reversion Strategy (Skylar's Winner)"""
    print(f"\n📉 Starting Strategy B: Mean Reversion ({duration_minutes}min)")
    
    trader = PaperTrader("Strategy_B_MeanReversion", initial_sol=1.0)
    data = SolanaMemeCoinData()
    
    start_time = time.time()
    iterations = 0
    
    while time.time() - start_time < duration_minutes * 60:
        iterations += 1
        
        prices = data.update_prices()
        
        # Check existing positions for exits
        for coin, trade in list(trader.positions.items()):
            current = prices[coin]
            entry = trade.entry_price
            
            # Check for scale out at +8%
            if current >= entry * 1.08 and not any(p["reason"] == "Scale 50% @ +8%" for p in trade.partial_exits):
                trader.partial_exit(coin, current, 50, "Scale 50% @ +8%")
                print(f"  📊 SCALE OUT 50% {coin} @ ${current:.6f} (+8%)")
                
            # Check for full exit at +15% or stop at -8%
            if current >= entry * 1.15:
                trader.close_position(coin, current, "Profit Target +15%")
                print(f"  ✅ TARGET HIT {coin} @ ${current:.6f} (+15%)")
            elif current <= entry * 0.92:
                trader.close_position(coin, current, "Stop Loss -8%")
                print(f"  ⛔ STOPPED {coin} @ ${current:.6f} (-8%)")
        
        # Look for dip entries (max 2 positions, 0.4 SOL each)
        if len(trader.positions) < 2:
            candidates = data.get_dip_candidates(min_dip=-20, max_dip=-10)
            for candidate in candidates:
                coin = candidate["coin"]
                # Only $10M+ market cap
                if candidate["market_cap"] >= 10_000_000 and coin not in trader.positions:
                    entry = prices[coin]
                    stop = entry * 0.92  # 8% stop
                    target = entry * 1.15  # 15% target
                    size = 0.4  # Fixed 0.4 SOL per position
                    
                    if trader.balance_sol >= size:
                        trade = trader.open_position(coin, entry, size, stop, target)
                        if trade:
                            print(f"  🎯 DIP ENTRY {coin} @ ${entry:.6f} | Dip: {candidate['dip_pct']:.1f}% | Size: {size:.3f} SOL")
        
        if iterations % 20 == 0:
            elapsed = (time.time() - start_time) / 60
            print(f"  ⏱️  {elapsed:.1f}min | Balance: {trader.balance_sol:.3f} SOL | Positions: {len(trader.positions)}")
        
        await asyncio.sleep(0.1)
    
    # Close remaining
    for coin in list(trader.positions.keys()):
        trade = trader.positions[coin]
        # Calculate final P&L
        current = prices[coin]
        trader.close_position(coin, current, "Time Exit")
        print(f"  🔚 CLOSED {coin} @ ${current:.6f} (Time Exit)")
    
    result = trader.save_results("/home/skux/phase1_strategy_B.json")
    print(f"  ✅ Strategy B Complete: {trader.get_result().total_pnl_sol:.3f} SOL P&L")
    return trader.get_result()


async def run_strategy_c(duration_minutes: int = 3):
    """Hybrid Momentum-Dip Strategy"""
    print(f"\n⚡ Starting Strategy C: Hybrid Momentum-Dip ({duration_minutes}min)")
    
    trader = PaperTrader("Strategy_C_Hybrid", initial_sol=1.0)
    data = SolanaMemeCoinData()
    
    start_time = time.time()
    iterations = 0
    
    while time.time() - start_time < duration_minutes * 60:
        iterations += 1
        
        prices = data.update_prices()
        trader.check_positions(prices)
        
        # Look for momentum-dip entries (max 2 positions)
        if len(trader.positions) < 2:
            candidates = data.get_momentum_dip_candidates()
            # Mix of quality (high cap) and momentum (any)
            quality_candidates = [c for c in candidates if data.COINS[c["coin"]]["market_cap"] > 100_000_000]
            momentum_candidates = [c for c in candidates if data.COINS[c["coin"]]["market_cap"] <= 100_000_000]
            
            # Prioritize quality but allow momentum
            selected = quality_candidates[:1] + momentum_candidates[:1]
            
            for candidate in selected:
                coin = candidate["coin"]
                if coin not in trader.positions:
                    entry = prices[coin]
                    stop = entry * 0.93  # 7% stop
                    target = entry * 1.12  # 12% profit
                    size = trader.balance_sol / 2 if trader.balance_sol > 0.2 else 0
                    
                    if size > 0.1:
                        trade = trader.open_position(coin, entry, size, stop, target)
                        if trade:
                            mc = data.COINS[coin]["market_cap"]
                            tier = "🔷 QUALITY" if mc > 100_000_000 else "🔸 MOMENTUM"
                            print(f"  {tier} ENTRY {coin} @ ${entry:.6f} | Size: {size:.3f} SOL")
        
        if iterations % 20 == 0:
            elapsed = (time.time() - start_time) / 60
            print(f"  ⏱️  {elapsed:.1f}min | Balance: {trader.balance_sol:.3f} SOL | Positions: {len(trader.positions)}")
        
        await asyncio.sleep(0.1)
    
    for coin in list(trader.positions.keys()):
        trader.close_position(coin, prices[coin], "Time Exit")
        print(f"  🔚 CLOSED {coin} @ ${prices[coin]:.6f} (Time Exit)")
    
    result = trader.save_results("/home/skux/phase1_strategy_C.json")
    print(f"  ✅ Strategy C Complete: {trader.get_result().total_pnl_sol:.3f} SOL P&L")
    return trader.get_result()


async def run_optimal_strategy(duration_minutes: int = 6, strategy_config: dict = None):
    """Run the optimized strategy"""
    print(f"\n👑 Starting OPTIMAL Strategy ({duration_minutes}min)")
    
    config = strategy_config or {}
    trader = PaperTrader("Optimal_Strategy", initial_sol=1.0)
    data = SolanaMemeCoinData()
    
    start_time = time.time()
    iterations = 0
    
    # Optimal parameters
    max_positions = config.get("max_positions", 3)
    position_size_pct = config.get("position_size_pct", 0.25)  # 25% of available balance
    
    while time.time() - start_time < duration_minutes * 60:
        iterations += 1
        
        prices = data.update_prices()
        
        # Dynamic exit management
        for coin, trade in list(trader.positions.items()):
            current = prices[coin]
            entry = trade.entry_price
            pnl_pct = (current - entry) / entry * 100
            
            # Scale out rules
            scale_1_target = config.get("scale_1", 8)
            scale_2_target = config.get("scale_2", 15)
            stop = config.get("stop", 7)
            
            # First scale out
            if pnl_pct >= scale_1_target and not any(p["reason"] == f"Scale 50% @ +{scale_1_target}%" for p in trade.partial_exits):
                trader.partial_exit(coin, current, 50, f"Scale 50% @ +{scale_1_target}%")
                print(f"  📊 SCALE 50% {coin} @ ${current:.6f} (+{scale_1_target}%)")
            
            # Second exit or full close
            if pnl_pct >= scale_2_target:
                trader.close_position(coin, current, f"Target +{scale_2_target}%")
                print(f"  ✅ TARGET {coin} @ ${current:.6f} (+{scale_2_target}%)")
            elif pnl_pct <= -stop:
                trader.close_position(coin, current, f"Stop -{stop}%")
                print(f"  ⛔ STOP {coin} @ ${current:.6f} (-{stop}%)")
        
        # Entry logic - combine best of all strategies
        if len(trader.positions) < max_positions:
            all_candidates = []
            
            # Mean reversion candidates (quality only)
            dip_candidates = data.get_dip_candidates(-18, -8)
            for c in dip_candidates:
                if c["market_cap"] >= 20_000_000:
                    all_candidates.append({**c, "signal": "dip", "score": abs(c["dip_pct"])})
            
            # Momentum shift candidates
            mom_candidates = data.get_momentum_dip_candidates()
            for c in mom_candidates:
                mc = data.COINS[c["coin"]]["market_cap"]
                score = 15 if mc > 100_000_000 else 12
                all_candidates.append({**c, "signal": "momentum_shift", "score": score})
            
            # Breakout candidates (conservative)
            breakout_candidates = data.get_breakout_candidates(min_green=15)
            for c in breakout_candidates:
                if c["market_cap"] > 50_000_000:  # Only quality breakouts
                    all_candidates.append({**c, "signal": "breakout", "score": c["breakout_pct"]})
            
            # Sort by score and take best
            all_candidates.sort(key=lambda x: x["score"], reverse=True)
            
            for candidate in all_candidates[:max_positions - len(trader.positions)]:
                coin = candidate["coin"]
                if coin not in trader.positions:
                    entry = prices[coin]
                    
                    # Dynamic stop/target based on signal type
                    if candidate["signal"] == "dip":
                        stop = entry * 0.93  # 7% stop
                        target = entry * 1.18  # 18% target
                    elif candidate["signal"] == "momentum_shift":
                        stop = entry * 0.94  # 6% stop
                        target = entry * 1.14  # 14% target
                    else:  # breakout
                        stop = entry * 0.95  # 5% stop
                        target = entry * 1.12  # 12% target
                    
                    size = min(trader.balance_sol * position_size_pct, 0.35)
                    
                    if size >= 0.1 and trader.balance_sol >= size:
                        trade = trader.open_position(coin, entry, size, stop, target)
                        if trade:
                            sig = candidate["signal"].upper()
                            print(f"  🎯 {sig} ENTRY {coin} @ ${entry:.6f} | Size: {size:.3f} SOL")
        
        if iterations % 40 == 0:  # Every ~2 minutes
            elapsed = (time.time() - start_time) / 60
            open_pnl = sum(
                ((prices.get(c, t.entry_price) - t.entry_price) / t.entry_price * t.position_size_sol)
                for c, t in trader.positions.items()
            )
            total_val = trader.balance_sol + sum(t.position_size_sol for t in trader.positions.values()) + open_pnl
            print(f"  ⏱️  {elapsed:.1f}min | Balance: {trader.balance_sol:.3f} SOL | Open P&L: {open_pnl:.3f} | Total Value: {total_val:.3f} SOL")
        
        await asyncio.sleep(0.1)
    
    # Close all at market
    for coin in list(trader.positions.keys()):
        trade = trader.positions[coin]
        current = prices[coin]
        trader.close_position(coin, current, "Final Exit")
        print(f"  🔚 CLOSED {coin} @ ${current:.6f}")
    
    result = trader.get_result()
    
    # Save both summary and detailed trades
    with open("/home/skux/optimal_strategy_results.json", 'w') as f:
        json.dump(asdict(result), f, indent=2, default=str)
    
    with open("/home/skux/optimal_strategy_trades.json", 'w') as f:
        json.dump(result.trades, f, indent=2, default=str)
    
    print(f"  ✅ OPTIMAL Strategy Complete: {result.total_pnl_sol:.3f} SOL P&L | Win Rate: {result.win_rate:.1f}%")
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python paper_trader.py <A|B|C|OPTIMAL>")
        sys.exit(1)
    
    cmd = sys.argv[1].upper()
    
    if cmd == "A":
        asyncio.run(run_strategy_a(15))
    elif cmd == "B":
        asyncio.run(run_strategy_b(18))
    elif cmd == "C":
        asyncio.run(run_strategy_c(17))
    elif cmd == "OPTIMAL":
        config = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        asyncio.run(run_optimal_strategy(60, config))
    else:
        print(f"Unknown strategy: {cmd}")
