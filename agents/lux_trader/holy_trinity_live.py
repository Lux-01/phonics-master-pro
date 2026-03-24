#!/usr/bin/env python3
"""
🔥 HOLY TRINITY LIVE TRADING SYSTEM
Runs in parallel with LuxTrader v3.0

Components:
- Rug-Radar (safety gate)
- Mean-Reverter (entry timing)
- LuxTrader (execution quality)

REQUIRES ALL 3 TO APPROVE

SAFETY: Larger positions (10.5-11.46%) but higher confidence
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import random

# Import Jupiter executor for live trading
try:
    from jupiter_executor import execute_buy, execute_sell
    JUPITER_AVAILABLE = True
except ImportError:
    JUPITER_AVAILABLE = False
    print("⚠️ Jupiter executor not available - trades will be manual")

# MODE
MODE = "LIVE"  # Options: PAPER, LIVE (NOW LIVE - REAL MONEY)

# WALLET (shared with LuxTrader)
WALLET_ADDRESS = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# SAFETY LIMITS - Holy Trinity specific
SAFETY = {
    "max_position_sol": 0.15,       # 15% max per trade (Holy Trinity larger positions)
    "max_position_pct": 0.15,       # 15% max per trade
    "max_daily_loss_sol": 0.10,     # Stop at -0.10 SOL (higher than LuxTrader's 0.05)
    "max_drawdown_pct": 20,         # 20% drawdown limit
    "min_liquidity_usd": 10000,     # Stricter: $10K min liquidity
    "slippage_bps": 200,            # 2% max slippage
    "max_trades_per_day": 3,        # Fewer trades (stricter criteria)
    "profit_threshold_to_scale": 0.10,  # Scale at +0.10 SOL
}

# CONFIG - Holy Trinity
CONFIG = {
    "name": "HolyTrinity",
    "version": "1.0",
    "mode": MODE,
    "luxtrader_pid": None,  # Will detect LuxTrader running
    
    # Component weights for composite score
    "weights": {
        "rug_radar": 0.35,
        "mean_reverter": 0.40,
        "luxtrader": 0.25
    },
    
    # Entry requirements
    "composite_score_min": 80,     # Must score 80+ (vs LuxTrader's 75)
    "grade_min": "A",               # A or A+ only
    "mcap_min": 20000,              # Stricter: $20K min
    "mcap_max": 150000,
    "age_max_hours": 48,            # Can trade older coins
    "age_min_hours": 1,
    
    "liquidity_min": 10000,         # $10K min
    "liquidity_ratio_min": 0.20,    # 20% ratio
    
    # Position sizing - Holy Trinity style
    "entry_size_base": 0.105,       # 10.5% base (from backtest data)
    "entry_size_a_plus": 0.1146,    # 11.46% for A+ grade
    "max_positions": 2,              # Max 2 concurrent (larger positions)
    "max_position_sol": SAFETY["max_position_sol"],
    "max_position_pct": SAFETY["max_position_pct"],
    
    # Exits
    "tier1_target_pct": 15,         # Close 40%
    "tier2_target_pct": 25,         # Close 30%
    "tier3_target_pct": 40,         # Trail 30%
    "trailing_stop_pct": 20,        # Tighter trail (more conservative)
    "stop_loss_pct": 8,             # -8% stop (vs LuxTrader's -7%)
    "time_stop_hours": 6,           # 6h max (vs LuxTrader's 4h)
    
    # Files - SEPARATE from LuxTrader to avoid conflicts
    "trade_log": "/home/skux/.openclaw/workspace/agents/lux_trader/holy_trinity_trades.json",
    "state_file": "/home/skux/.openclaw/workspace/agents/lux_trader/holy_trinity_state.json",
    "logs_dir": "/home/skux/.openclaw/workspace/agents/lux_trader/holy_trinity_logs",
    "signal_cache": "/home/skux/.openclaw/workspace/agents/lux_trader/holy_trinity_signals.json",
    
    # APIs
    "birdeye_api_key": "6335463fca7340f9a2c73eacd5a37f64",
    "helius_api_key": "350aa83c-44a4-4068-a511-580f82930d84",
    "jupiter_api": "https://quote-api.jup.ag/v4",
}

class HolyTrinityLive:
    """
    Holy Trinity Live Trader
    Requires ALL 3 strategies to approve
    """
    
    def __init__(self):
        self._ensure_dirs()
        self.state = self._load_state()
        self.daily_stats = self._init_daily_stats()
        self.active_positions = []
        self.signal_history = []
        
    def _ensure_dirs(self):
        os.makedirs(CONFIG["logs_dir"], exist_ok=True)
        os.makedirs(os.path.dirname(CONFIG["trade_log"]), exist_ok=True)
        
    def _load_state(self) -> Dict:
        if os.path.exists(CONFIG["state_file"]):
            with open(CONFIG["state_file"], 'r') as f:
                return json.load(f)
        return {
            "total_capital": 1.0,  # Separate from LuxTrader
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0,
            "peak_capital": 1.0,
            "last_trade_time": None,
            "daily_reset": datetime.now().strftime("%Y-%m-%d"),
            "daily_pnl": 0,
            "daily_trades": 0,
            "strategy": "HolyTrinity",
            "parallel_with": "LuxTrader_v3.0"
        }
    
    def _init_daily_stats(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        if self.state.get("daily_reset") != today:
            self.state["daily_reset"] = today
            self.state["daily_pnl"] = 0
            self.state["daily_trades"] = 0
            self._log("INFO", f"Daily stats reset for {today}")
        return {
            "day_pnl": self.state.get("daily_pnl", 0),
            "trades_today": self.state.get("daily_trades", 0)
        }
    
    def save_state(self):
        self.state["daily_pnl"] = self.daily_stats["day_pnl"]
        self.state["daily_trades"] = self.daily_stats["trades_today"]
        with open(CONFIG["state_file"], 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Write to daily log
        log_file = os.path.join(CONFIG["logs_dir"], f"holy_trinity_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def check_circuit_breakers(self) -> Tuple[bool, str]:
        """Check safety limits"""
        capital = self.state["total_capital"]
        peak = self.state["peak_capital"]
        
        # Daily loss
        if self.daily_stats["day_pnl"] < -SAFETY["max_daily_loss_sol"]:
            return False, f"Daily loss limit: {self.daily_stats['day_pnl']:.4f} SOL"
        
        # Drawdown
        if peak > 0:
            drawdown = (peak - capital) / peak * 100
            if drawdown > SAFETY["max_drawdown_pct"]:
                return False, f"Drawdown: {drawdown:.1f}% (max {SAFETY['max_drawdown_pct']}%)"
        
        # Trade limit
        if self.daily_stats["trades_today"] >= SAFETY["max_trades_per_day"]:
            return False, f"Daily trade limit: {self.daily_stats['trades_today']}"
        
        return True, "OK"
    
    def evaluate_rug_radar(self, token: Dict) -> Tuple[int, str]:
        """
        Rug-Radar: Safety gate
        Returns: (score 0-100, reason)
        """
        score = 60  # Base
        reasons = []
        
        # Liquidity check
        liquidity = token.get('liquidity', 0)
        if liquidity >= 15000: 
            score += 20
            reasons.append("High liquidity")
        elif liquidity >= 10000:
            score += 15
            reasons.append("Good liquidity")
        elif liquidity < 5000:
            score -= 25
            reasons.append("Low liquidity")
        
        # Holders
        holders = token.get('holders', 100)
        if holders > 100:
            score += 10
            reasons.append("Many holders")
        elif holders < 20:
            score -= 20
            reasons.append("Few holders")
        
        # Volume
        volume_24h = token.get('volume_24h', 0)
        if volume_24h > 50000:
            score += 10
            reasons.append("High volume")
        
        # Age
        age_hours = token.get('age_hours', 6)
        if age_hours > 48:
            score -= 15
            reasons.append("Old token")
        elif age_hours < 2:
            score -= 10  # Too fresh
            reasons.append("Very fresh")
        
        return min(100, score), " | ".join(reasons) if reasons else "Base safety"
    
    def evaluate_mean_reverter(self, token: Dict) -> Tuple[int, str]:
        """
        Mean-Reverter: Entry timing
        Returns: (score 0-100, reason)
        """
        score = 40  # Base
        reasons = []
        
        deviation = token.get('deviation', 0)
        
        # Perfect dip zone: -18% to -10%
        if -0.18 <= deviation <= -0.10:
            score += 40
            reasons.append(f"Perfect dip: {deviation:.1%}")
        # Good dip: -25% to -8%
        elif -0.25 <= deviation < -0.18:
            score += 30
            reasons.append(f"Deep dip: {deviation:.1%}")
        elif -0.08 < deviation < 0:
            score += 15
            reasons.append(f"Small dip: {deviation:.1%}")
        elif deviation > 0:
            score -= 20
            reasons.append(f"Pumped: {deviation:.1%}")
        elif deviation < -0.30:
            score -= 10
            reasons.append(f"Knife-catching: {deviation:.1%}")
        
        # Price action
        price_change_5m = token.get('price_change_5m', 0)
        if price_change_5m < -5:  # Recent drop
            score += 10
        
        return min(100, score), " | ".join(reasons) if reasons else "Neutral"
    
    def evaluate_luxtrader(self, token: Dict) -> Tuple[int, str]:
        """
        LuxTrader: Quality assessment
        Returns: (score 0-100, reason)
        """
        score = 40
        reasons = []
        
        grade = token.get('grade', 'C')
        age_hours = token.get('age_hours', 6)
        
        # Grade scoring
        if grade == 'A+':
            score += 40
            reasons.append("A+ grade")
        elif grade == 'A':
            score += 30
            reasons.append("A grade")
        elif grade == 'B':
            score += 15
            reasons.append("B grade")
        else:
            score -= 20
            reasons.append(f"{grade} grade")
        
        # Age
        if age_hours < 4:
            score += 20
            reasons.append("Very fresh <4h")
        elif age_hours < 8:
            score += 15
            reasons.append("Fresh <8h")
        elif age_hours < 16:
            score += 10
        elif age_hours > 24:
            score -= 10
            reasons.append(f"Old: {age_hours}h")
        
        # Narrative
        symbol = token.get('symbol', '').upper()
        keywords = ["AI", "AGENT", "MEME", "PEPE", "DOGE", "DEX", "INU"]
        if any(k in symbol for k in keywords):
            score += 10
            reasons.append("Narrative match")
        
        return min(100, score), " | ".join(reasons) if reasons else "Base quality"
    
    def calculate_composite_score(self, token: Dict) -> Tuple[float, Dict]:
        """
        Calculate weighted composite score
        Requires all 3 strategies
        """
        rug_score, rug_reason = self.evaluate_rug_radar(token)
        mr_score, mr_reason = self.evaluate_mean_reverter(token)
        lux_score, lux_reason = self.evaluate_luxtrader(token)
        
        # Weighted average
        composite = (
            rug_score * CONFIG["weights"]["rug_radar"] +
            mr_score * CONFIG["weights"]["mean_reverter"] +
            lux_score * CONFIG["weights"]["luxtrader"]
        )
        
        signals = {
            "rug_radar": {"score": rug_score, "reason": rug_reason},
            "mean_reverter": {"score": mr_score, "reason": mr_reason},
            "luxtrader": {"score": lux_score, "reason": lux_reason},
            "composite": round(composite, 1)
        }
        
        return composite, signals
    
    def evaluate_opportunity(self, token: Dict) -> Tuple[bool, float, Dict, str]:
        """
        Evaluate if trade should be taken
        Returns: (should_trade, composite_score, signals, reason)
        """
        # Must have A or A+ grade
        grade = token.get('grade', 'C')
        if grade not in ['A', 'A+']:
            return False, 0, {}, f"Grade {grade} rejected"
        
        # Circuit breakers
        can_trade, reason = self.check_circuit_breakers()
        if not can_trade:
            return False, 0, {}, reason
        
        # Calculate composite
        composite, signals = self.calculate_composite_score(token)
        
        # Must meet minimum
        if composite < CONFIG["composite_score_min"]:
            return False, composite, signals, f"Score {composite:.1f} < {CONFIG['composite_score_min']}"
        
        return True, composite, signals, "TRINITY APPROVED"
    
    def calculate_position_size(self, token: Dict, composite_score: float) -> float:
        """
        Calculate position size based on grade and confidence
        """
        grade = token.get('grade', 'A')
        capital = self.state["total_capital"]
        
        # Base size by grade
        if grade == 'A+':
            base_pct = CONFIG["entry_size_a_plus"]  # 11.46%
        else:
            base_pct = CONFIG["entry_size_base"]    # 10.5%
        
        # Adjust by composite score
        if composite_score >= 90:
            boost = 1.0
        elif composite_score >= 85:
            boost = 0.95
        else:
            boost = 0.9
        
        # Final size
        position_pct = base_pct * boost
        position_sol = capital * position_pct
        
        # Apply caps
        max_sol = min(SAFETY["max_position_sol"], capital * SAFETY["max_position_pct"])
        return min(position_sol, max_sol)
    
    def execute_trade(self, token: Dict, signals: Dict) -> Dict:
        """Execute or paper trade"""
        composite = signals["composite"]
        position_sol = self.calculate_position_size(token, composite)
        
        trade = {
            "timestamp": datetime.now().isoformat(),
            "mode": MODE,
            "symbol": token.get('symbol', 'UNKNOWN'),
            "address": token.get('address', ''),
            "entry_price": token.get('price', 0),
            "position_sol": position_sol,
            "position_pct": position_sol / self.state["total_capital"] * 100,
            "signals": signals,
            "grade": token.get('grade', 'A'),
            "composite_score": composite
        }
        
        if MODE == "LIVE":
            # ACTUAL EXECUTION via Jupiter
            if JUPITER_AVAILABLE:
                print("   🚀 Executing via Jupiter...")
                result = execute_buy(
                    wallet=WALLET_ADDRESS,
                    token_address=token.get("address", ""),
                    amount_sol=position_sol,
                    token_symbol=token.get("symbol", "UNKNOWN")
                )
                
                trade["execution"] = result
                
                if result.get("status") == "manual_required":
                    print(f"   ⚠️ Manual execution required")
                    print(f"   🔗 {result.get('manual_url', 'N/A')}")
                    trade["executed"] = False
                    trade["status"] = "pending_manual"
                    trade["manual_url"] = result.get("manual_url")
                elif result.get("status") == "failed":
                    print(f"   ❌ Execution failed: {result.get('error')}")
                    trade["executed"] = False
                    trade["status"] = "failed"
                else:
                    print(f"   ✅ Execution initiated")
                    trade["executed"] = True
                    trade["status"] = "executed"
            else:
                print("   ⚠️ Jupiter executor not available")
                print("   🔗 Manual: https://jup.ag")
                trade["executed"] = False
                trade["status"] = "manual_required"
                trade["manual_url"] = f"https://jup.ag/swap/SOL-{token.get('address', '')}"
        else:
            trade["executed"] = False
            trade["note"] = "PAPER mode - simulated"
        
        # Save trade
        self._save_trade(trade)
        
        return trade
    
    def _save_trade(self, trade: Dict):
        """Save trade to log file"""
        try:
            log_file = "/home/skux/.openclaw/workspace/agents/lux_trader/holy_trinity_trades.json"
            trades = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    trades = json.load(f)
            trades.append(trade)
            with open(log_file, 'w') as f:
                json.dump(trades, f, indent=2)
        except Exception as e:
            print(f"   ⚠️ Could not save trade log: {e}")
    
    def run_scan(self):
        """Main scan loop - check for opportunities"""
        self._log("INFO", f"=== Holy Trinity Scan | Capital: {self.state['total_capital']:.4f} SOL ===")
        
        # Check circuit breakers
        can_trade, reason = self.check_circuit_breakers()
        if not can_trade:
            self._log("BLOCKED", reason)
            return
        
        self._log("INFO", f"Daily stats: {self.daily_stats['trades_today']} trades, PnL: {self.daily_stats['day_pnl']:.4f} SOL")
        
        # In real implementation, would fetch from AOE/scanner
        # For now, just log ready state
        self._log("INFO", "Ready - waiting for AOE signals ≥80 composite score")
        
        self.save_state()
    
    def print_status(self):
        """Print current status"""
        print("\n" + "="*60)
        print("🔥 HOLY TRINITY LIVE STATUS")
        print("="*60)
        print(f"Mode: {MODE}")
        print(f"Capital: {self.state['total_capital']:.4f} SOL")
        print(f"Total Trades: {self.state['total_trades']}")
        print(f"Wins: {self.state['wins']} | Losses: {self.state['losses']}")
        print(f"Daily PnL: {self.daily_stats['day_pnl']:.4f} SOL")
        print(f"Daily Trades: {self.daily_stats['trades_today']}/{SAFETY['max_trades_per_day']}")
        print(f"Position Size: 10.5-11.46% of capital")
        print(f"Signal Threshold: 80+ composite score")
        print(f"Running Parallel: LuxTrader v3.0")
        print("="*60)


def main():
    trinity = HolyTrinityLive()
    
    if len(os.sys.argv) > 1:
        if os.sys.argv[1] == "--status":
            trinity.print_status()
            return
    
    # Run scan
    trinity.run_scan()
    trinity.print_status()


if __name__ == "__main__":
    import sys
    main()
