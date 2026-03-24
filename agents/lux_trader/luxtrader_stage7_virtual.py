#!/usr/bin/env python3
"""
✨ LUXTRADER STAGE 7 - VIRTUAL PAPER TRADING
Fully automated paper trading with virtual funds for pattern learning

Features:
- Virtual portfolio: 10 SOL starting balance
- Simulated execution with real market data
- All trades logged to ALOE for pattern learning
- No real money at risk
- Auto-execute on Grade A+ signals
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import random
import requests

# Add workspace to path
sys.path.insert(0, '/home/skux/.openclaw/workspace')

# Import trading outcome tracker
try:
    from skills.outcome_tracker.trading_outcome_tracker import TradingOutcomeTracker
    OUTCOME_TRACKER = TradingOutcomeTracker()
    HAS_TRACKER = True
except ImportError:
    OUTCOME_TRACKER = None
    HAS_TRACKER = False

# CONFIGURATION
VIRTUAL_PORTFOLIO_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/virtual_portfolio.json"
TRADE_HISTORY_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/virtual_trades.json"
SIGNALS_DIR = "/home/skux/.openclaw/workspace/agents/lux_trader/signals"
LOG_DIR = "/home/skux/.openclaw/workspace/agents/lux_trader/logs"

# Virtual portfolio settings
VIRTUAL_CONFIG = {
    "starting_capital": 10.0,  # 10 SOL virtual
    "max_positions": 5,
    "position_size_base": 0.5,  # 0.5 SOL per trade
    "position_size_max": 2.0,  # Max 2 SOL per position
    "stop_loss_pct": 7,
    "take_profit_pct": 15,
    "time_stop_hours": 4,
    "min_grade": "A",  # A or A+
    "mcap_min": 15000,
    "mcap_max": 100000,
    "liquidity_min": 8000,
}

# Birdeye API
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BIRDEYE_BASE = "https://public-api.birdeye.so"

class VirtualPortfolio:
    """Manages virtual SOL balance and token positions."""
    
    def __init__(self):
        self.portfolio_file = Path(VIRTUAL_PORTFOLIO_FILE)
        self.trades_file = Path(TRADE_HISTORY_FILE)
        self.ensure_files()
        self.load_portfolio()
    
    def ensure_files(self):
        """Create files if they don't exist."""
        for dir_path in [SIGNALS_DIR, LOG_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        if not self.portfolio_file.exists():
            self.reset_portfolio()
        
        if not self.trades_file.exists():
            with open(self.trades_file, 'w') as f:
                json.dump({"trades": []}, f)
    
    def reset_portfolio(self):
        """Reset to starting capital."""
        portfolio = {
            "virtual_sol": VIRTUAL_CONFIG["starting_capital"],
            "starting_capital": VIRTUAL_CONFIG["starting_capital"],
            "realized_pnl_sol": 0.0,
            "open_positions": {},  # token -> position data
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "created_at": datetime.now().isoformat(),
        }
        self.save_portfolio(portfolio)
    
    def load_portfolio(self):
        """Load current portfolio state."""
        with open(self.portfolio_file) as f:
            self.portfolio = json.load(f)
    
    def save_portfolio(self, portfolio=None):
        """Save portfolio state."""
        if portfolio:
            self.portfolio = portfolio
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def get_available_sol(self) -> float:
        """Get available SOL for new positions."""
        committed = sum(
            p["entry_sol"] for p in self.portfolio["open_positions"].values()
        )
        return self.portfolio["virtual_sol"] - committed
    
    def get_position(self, token: str) -> Optional[Dict]:
        """Get position for a token."""
        return self.portfolio["open_positions"].get(token)
    
    def has_position(self, token: str) -> bool:
        """Check if we have an open position."""
        return token in self.portfolio["open_positions"]
    
    def get_open_position_count(self) -> int:
        """Count open positions."""
        return len(self.portfolio["open_positions"])

class VirtualExecutor:
    """Simulates trade execution with real market data."""
    
    def __init__(self, portfolio: VirtualPortfolio):
        self.portfolio = portfolio
    
    def get_token_price(self, token_address: str) -> Optional[float]:
        """Get current price from Birdeye."""
        try:
            url = f"{BIRDEYE_BASE}/defi/price?address={token_address}"
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if data.get("success") and data.get("data"):
                return float(data["data"]["value"])
            return None
        except Exception as e:
            print(f"⚠️ Price fetch error: {e}")
            return None
    
    def simulate_buy(self, token_address: str, token_symbol: str, 
                     entry_sol: float) -> Optional[Dict]:
        """Simulate a buy order."""
        
        price = self.get_token_price(token_address)
        if not price:
            print(f"❌ Cannot get price for {token_symbol}")
            return None
        
        # Calculate token amount (minus 1% fee)
        fee = entry_sol * 0.01
        actual_sol = entry_sol - fee
        token_amount = actual_sol / price
        
        position = {
            "token_address": token_address,
            "token_symbol": token_symbol,
            "entry_price": price,
            "entry_sol": entry_sol,
            "actual_sol": actual_sol,
            "fee_sol": fee,
            "token_amount": token_amount,
            "entry_time": datetime.now().isoformat(),
            "stop_loss": price * (1 - VIRTUAL_CONFIG["stop_loss_pct"] / 100),
            "take_profit": price * (1 + VIRTUAL_CONFIG["take_profit_pct"] / 100),
            "status": "open",
        }
        
        print(f"\n🟢 VIRTUAL BUY: {token_symbol}")
        print(f"   Entry: ${price:.6f}")
        print(f"   Size: {entry_sol:.3f} SOL")
        print(f"   Tokens: {token_amount:.2f}")
        print(f"   Stop: ${position['stop_loss']:.6f} (-{VIRTUAL_CONFIG['stop_loss_pct']}%)")
        print(f"   Target: ${position['take_profit']:.6f} (+{VIRTUAL_CONFIG['take_profit_pct']}%)")
        
        return position
    
    def simulate_sell(self, position: Dict, exit_type: str = "manual") -> Dict:
        """Simulate a sell order."""
        
        token_address = position["token_address"]
        current_price = self.get_token_price(token_address)
        
        if not current_price:
            print(f"⚠️ Cannot get exit price, using entry price")
            current_price = position["entry_price"]
        
        # Calculate P&L
        token_amount = position["token_amount"]
        exit_value = token_amount * current_price
        fee = exit_value * 0.01
        net_sol = exit_value - fee
        
        pnl_sol = net_sol - position["entry_sol"]
        pnl_pct = (pnl_sol / position["entry_sol"]) * 100
        
        result = {
            "token_address": token_address,
            "token_symbol": position["token_symbol"],
            "entry_price": position["entry_price"],
            "exit_price": current_price,
            "entry_sol": position["entry_sol"],
            "exit_sol": net_sol,
            "pnl_sol": pnl_sol,
            "pnl_pct": pnl_pct,
            "entry_time": position["entry_time"],
            "exit_time": datetime.now().isoformat(),
            "exit_type": exit_type,
            "status": "closed",
        }
        
        icon = "🟢" if pnl_sol > 0 else "🔴"
        print(f"\n{icon} VIRTUAL SELL: {position['token_symbol']}")
        print(f"   Exit: ${current_price:.6f}")
        print(f"   PnL: {pnl_sol:+.3f} SOL ({pnl_pct:+.1f}%)")
        print(f"   Type: {exit_type}")
        
        return result

class Stage7Trader:
    """Stage 7: Virtual paper trading with ALOE learning."""
    
    def __init__(self):
        self.portfolio = VirtualPortfolio()
        self.executor = VirtualExecutor(self.portfolio)
        self.running = False
    
    def check_signals(self) -> List[Dict]:
        """Check for new Grade A+ signals."""
        signals = []
        signals_path = Path(SIGNALS_DIR)
        
        if not signals_path.exists():
            return signals
        
        for signal_file in sorted(signals_path.glob("signal_*.json"), reverse=True)[:10]:
            try:
                with open(signal_file) as f:
                    signal = json.load(f)
                    # Only take recent signals (last hour)
                    signal_time = datetime.fromisoformat(signal.get("timestamp", "2000-01-01"))
                    if datetime.now() - signal_time < timedelta(hours=1):
                        if signal.get("grade") in ["A", "A+", "A-"]:
                            signals.append(signal)
            except:
                pass
        
        return signals
    
    def evaluate_signal(self, signal: Dict) -> bool:
        """Check if signal meets entry criteria."""
        # Check grade
        if signal.get("grade") not in ["A", "A+", "A-"]:
            return False
        
        # Check mcap
        mcap = signal.get("market_cap", 0)
        if not (VIRTUAL_CONFIG["mcap_min"] <= mcap <= VIRTUAL_CONFIG["mcap_max"]):
            return False
        
        # Check if already in position
        if self.portfolio.has_position(signal.get("token_address", "")):
            return False
        
        # Check position limit
        if self.portfolio.get_open_position_count() >= VIRTUAL_CONFIG["max_positions"]:
            return False
        
        # Check available capital
        available = self.portfolio.get_available_sol()
        if available < VIRTUAL_CONFIG["position_size_base"]:
            return False
        
        return True
    
    def open_position(self, signal: Dict) -> bool:
        """Open a virtual position."""
        token_address = signal.get("token_address")
        token_symbol = signal.get("token", "Unknown")
        
        if not token_address:
            print(f"❌ No token address for {token_symbol}")
            return False
        
        # Calculate position size
        position_size = VIRTUAL_CONFIG["position_size_base"]
        
        # Simulate buy
        position = self.executor.simulate_buy(token_address, token_symbol, position_size)
        if not position:
            return False
        
        # Update portfolio
        self.portfolio.portfolio["open_positions"][token_address] = position
        self.portfolio.portfolio["total_trades"] += 1
        self.portfolio.save_portfolio()
        
        # Log to outcome tracker
        self.log_entry_to_aloe(signal, position)
        
        return True
    
    def close_position(self, token_address: str, exit_type: str = "manual") -> bool:
        """Close a virtual position."""
        position = self.portfolio.get_position(token_address)
        if not position:
            return False
        
        # Simulate sell
        result = self.executor.simulate_sell(position, exit_type)
        
        # Update portfolio
        pnl_sol = result["pnl_sol"]
        self.portfolio.portfolio["realized_pnl_sol"] += pnl_sol
        self.portfolio.portfolio["virtual_sol"] += pnl_sol
        
        if pnl_sol > 0:
            self.portfolio.portfolio["wins"] += 1
        else:
            self.portfolio.portfolio["losses"] += 1
        
        del self.portfolio.portfolio["open_positions"][token_address]
        self.portfolio.save_portfolio()
        
        # Save to trade history
        self.save_trade(result)
        
        # Log outcome to ALOE
        self.log_outcome_to_aloe(result)
        
        return True
    
    def check_exits(self):
        """Check all positions for exit conditions."""
        for token_address, position in list(self.portfolio.portfolio["open_positions"].items()):
            current_price = self.executor.get_token_price(token_address)
            if not current_price:
                continue
            
            entry_price = position["entry_price"]
            pct_change = ((current_price - entry_price) / entry_price) * 100
            
            # Check stop loss
            if current_price <= position["stop_loss"]:
                print(f"\n🛑 STOP LOSS HIT: {position['token_symbol']}")
                self.close_position(token_address, "stop_loss")
                continue
            
            # Check take profit
            if current_price >= position["take_profit"]:
                print(f"\n🎯 TAKE PROFIT HIT: {position['token_symbol']}")
                self.close_position(token_address, "take_profit")
                continue
            
            # Check time stop
            entry_time = datetime.fromisoformat(position["entry_time"])
            if datetime.now() - entry_time > timedelta(hours=VIRTUAL_CONFIG["time_stop_hours"]):
                print(f"\n⏰ TIME STOP: {position['token_symbol']}")
                self.close_position(token_address, "time_stop")
    
    def log_entry_to_aloe(self, signal: Dict, position: Dict):
        """Log entry to ALOE for pattern learning."""
        if HAS_TRACKER and OUTCOME_TRACKER:
            try:
                OUTCOME_TRACKER.log_signal(
                    token_ca=signal.get("token_address", ""),
                    token_name=signal.get("token", "Unknown"),
                    scanner_version="Stage7_Virtual",
                    grade=signal.get("grade", "C"),
                    score=signal.get("score", 0),
                    age_hours=signal.get("age_hours", 0),
                    top10_pct=signal.get("top10_pct", 0),
                    mcap=signal.get("market_cap", 0),
                    liq=signal.get("liquidity", 0),
                    vol24=signal.get("volume_24h", 0)
                )
            except Exception as e:
                print(f"⚠️ ALOE entry log error: {e}")
    
    def log_outcome_to_aloe(self, result: Dict):
        """Log trade outcome to ALOE for learning."""
        if HAS_TRACKER and OUTCOME_TRACKER:
            try:
                outcome = "PROFIT" if result["pnl_sol"] > 0 else "LOSS"
                OUTCOME_TRACKER.update_outcome(
                    signal_id=result["token_address"],  # Use token address as ID
                    outcome_status=outcome,
                    pnl_percent=result.get("pnl_pct", 0),
                    outcome_data={
                        "exit_price": result["exit_price"],
                        "exit_time": result["exit_time"],
                        "pnl_sol": result["pnl_sol"],
                        "pnl_pct": result["pnl_pct"],
                        "exit_type": result["exit_type"],
                    }
                )
            except Exception as e:
                print(f"⚠️ ALOE outcome log error: {e}")
    
    def save_trade(self, result: Dict):
        """Save trade to history."""
        with open(self.portfolio.trades_file) as f:
            history = json.load(f)
        
        history["trades"].append(result)
        
        with open(self.portfolio.trades_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get trading statistics."""
        p = self.portfolio.portfolio
        total = p["total_trades"]
        wins = p["wins"]
        losses = p["losses"]
        
        return {
            "virtual_sol": p["virtual_sol"],
            "starting_capital": p["starting_capital"],
            "total_pnl": p["virtual_sol"] - p["starting_capital"],
            "pnl_pct": ((p["virtual_sol"] - p["starting_capital"]) / p["starting_capital"]) * 100,
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / total * 100) if total > 0 else 0,
            "open_positions": len(p["open_positions"]),
        }
    
    def print_portfolio(self):
        """Display current portfolio status."""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("✨ STAGE 7: VIRTUAL PORTFOLIO STATUS")
        print("=" * 60)
        print(f"💰 Virtual SOL: {stats['virtual_sol']:.3f} / {stats['starting_capital']:.3f}")
        print(f"📊 Total PnL: {stats['total_pnl']:+.3f} SOL ({stats['pnl_pct']:+.1f}%)")
        print(f"🎯 Win Rate: {stats['win_rate']:.0f}% ({stats['wins']}W / {stats['losses']}L)")
        print(f"📈 Total Trades: {stats['total_trades']}")
        print(f"🔄 Open Positions: {stats['open_positions']} / {VIRTUAL_CONFIG['max_positions']}")
        
        if self.portfolio.portfolio["open_positions"]:
            print("\n📋 OPEN POSITIONS:")
            for addr, pos in self.portfolio.portfolio["open_positions"].items():
                current = self.executor.get_token_price(addr)
                if current:
                    pnl_pct = ((current - pos['entry_price']) / pos['entry_price']) * 100
                    icon = "🟢" if pnl_pct > 0 else "🔴"
                    print(f"   {icon} {pos['token_symbol']}: {pnl_pct:+.1f}%")
        
        print("=" * 60)
    
    def run_cycle(self):
        """Run one trading cycle."""
        print(f"\n{'='*60}")
        print(f"🔄 CYCLE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Check exits
        self.check_exits()
        
        # Check for new signals
        signals = self.check_signals()
        if signals:
            print(f"\n📡 Found {len(signals)} Grade A signals")
            for signal in signals[:3]:  # Max 3 per cycle
                if self.evaluate_signal(signal):
                    self.open_position(signal)
                    time.sleep(1)  # Rate limit
        else:
            print("\n📡 No new signals")
        
        # Show portfolio
        self.print_portfolio()
    
    def run_continuous(self, interval_minutes: int = 5):
        """Run continuous trading loop."""
        print("\n" + "=" * 60)
        print("✨ STAGE 7 VIRTUAL TRADER STARTED")
        print("=" * 60)
        print(f"Starting Capital: {VIRTUAL_CONFIG['starting_capital']} SOL")
        print(f"Position Size: {VIRTUAL_CONFIG['position_size_base']} SOL")
        print(f"Check Interval: {interval_minutes} minutes")
        print(f"Mode: PAPER (Virtual Funds)")
        print("=" * 60 + "\n")
        
        self.running = True
        
        try:
            while self.running:
                self.run_cycle()
                print(f"\n⏳ Sleeping {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n👋 Stage 7 trader stopped")
            self.print_portfolio()
    
    def run_once(self):
        """Run single cycle."""
        self.run_cycle()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stage 7: Virtual Paper Trading")
    parser.add_argument("--mode", choices=["once", "continuous"], default="once",
                       help="Run mode: once or continuous")
    parser.add_argument("--interval", type=int, default=5,
                       help="Check interval in minutes (continuous mode)")
    parser.add_argument("--reset", action="store_true",
                       help="Reset virtual portfolio")
    parser.add_argument("--stats", action="store_true",
                       help="Show portfolio stats only")
    
    args = parser.parse_args()
    
    trader = Stage7Trader()
    
    if args.reset:
        trader.portfolio.reset_portfolio()
        print("✅ Virtual portfolio reset")
        return
    
    if args.stats:
        trader.print_portfolio()
        return
    
    if args.mode == "continuous":
        trader.run_continuous(args.interval)
    else:
        trader.run_once()

if __name__ == "__main__":
    main()
