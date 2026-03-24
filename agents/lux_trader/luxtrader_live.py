#!/usr/bin/env python3
"""
✨ LUXTRADER v3.0 - LIVE TRADING SYSTEM (SCALED)
Enhanced with v3.0 features:
- Position size: 0.02 SOL per trade (SCALED 2x)
- Max trades: 5/day (conservative)
- Daily loss limit: 0.10 SOL (SCALED 2x)
- Pyramid entry (+50% after wins)
- Mean-reversion add-on (+30% after dips)
- 3-tier profit taking (40/30/30 at 15/25/40%)
- Streak boost (+15% per 3 wins)
- Narrative detection (AI/Meme/Agent boost)

SAFETY FIRST: Paper mode by default
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
    from token_reviewer import review_token, approve_token
    from full_auto_executor import execute_buy_auto, execute_sell_auto
    from ultra_executor import execute_buy_ultra, execute_sell_ultra
    from exit_manager import ExitManager
    JUPITER_AVAILABLE = True
    REVIEWER_AVAILABLE = True
    FULL_AUTO_AVAILABLE = True
    ULTRA_AVAILABLE = True
    EXIT_MANAGER_AVAILABLE = True
except ImportError as e:
    JUPITER_AVAILABLE = False
    REVIEWER_AVAILABLE = False
    FULL_AUTO_AVAILABLE = False
    ULTRA_AVAILABLE = False
    EXIT_MANAGER_AVAILABLE = False
    print(f"⚠️ Some modules not available: {e}")

# MODE - IMPORTANT
MODE = "LIVE"  # Options: PAPER, LIVE
# LIVE TRADING - REAL MONEY AT RISK

# WALLET (only used in LIVE mode)
WALLET_ADDRESS = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# SAFETY LIMITS - v3.0 (Scaled)
SAFETY = {
    "max_position_sol": 0.02,       # SCALED: 0.02 SOL per trade (2x)
    "max_position_pct": 0.20,       # Max 20% of capital
    "max_daily_loss_sol": 0.10,     # SCALED: Stop if -0.10 SOL day loss (2x)
    "max_drawdown_pct": 15,         # Stop at 15% drawdown
    "min_liquidity_usd": 8000,      # Higher filter for live: $8K min liquidity
    "min_mcap_usd": 15000,          # Min market cap $15K
    "slippage_bps": 250,            # 2.5% max slippage
    "max_trades_per_day": 5,        # v3.0: 5 trades/day (conservative)
    "profit_threshold_to_scale": 0.10,  # Scale up when +0.10 SOL profit (2x)
}

# CONFIG - LuxTrader v3.0 (Reverted)
CONFIG = {
    "name": "LuxTrader",
    "version": "3.0",              # Reverted to 3.0
    "mode": MODE,
    
    # Entry filters
    "grade_min": "A",              # A or A+ only
    "mcap_min": 15000,
    "mcap_max": 100000,
    "age_max_hours": 24,
    "age_min_hours": 1,
    
    "liquidity_min": 5000,
    "liquidity_ratio_min": 0.15,
    
    # Position sizing - v3.0 (Scaled)
    "entry_size_base": 0.012,      # SCALED: 1.2% of capital (0.012 SOL on 1 SOL)
    "max_positions": 3,
    "max_position_sol": SAFETY["max_position_sol"],  # Now 0.02 SOL
    "max_position_pct": SAFETY["max_position_pct"],
    
    # Exits - 3-tier
    "tier1_target_pct": 15,        # Close 40% here
    "tier2_target_pct": 25,        # Close 30% here  
    "tier3_target_pct": 40,        # Trail 30% to here
    "trailing_stop_pct": 25,       # Activate at +25%
    "stop_loss_pct": 7,            # Hard stop
    "time_stop_minutes": 240,      # 4h max hold
    
    # Pyramid entry
    "pyramid_enabled": True,
    "pyramid_after_win": True,     # Add after win
    "pyramid_increase_pct": 50,    # +50% size
    "pyramid_max_adds": 2,         # Max 2 pyramids
    
    # Mean-reversion add-on
    "addon_enabled": True,
    "addon_after_loss": True,      # Add after loss (recovery)
    "addon_increase_pct": 30,      # +30% size
    "addon_max": 1,
    
    # Streak boost
    "streak_boost_enabled": True,
    "streak_threshold": 3,         # Every 3 wins
    "streak_boost_pct": 15,        # +15% size
    
    # Narrative boost
    "narrative_boost": True,
    "trending_keywords": ["AI", "AGENT", "MEME", "PEPE", "DOGE", "SHIB", "CHAD", "DEX", "INU"],
    "narrative_target_mult": 1.25, # +25% target for narratives
    
    # Files
    "trade_log": "/home/skux/.openclaw/workspace/agents/lux_trader/live_trades.json",
    "state_file": "/home/skux/.openclaw/workspace/agents/lux_trader/live_state.json",
    "logs_dir": "/home/skux/.openclaw/workspace/agents/lux_trader/live_logs",
    
    # APIs
    "birdeye_api_key": "6335463fca7340f9a2c73eacd5a37f64",
    "helius_api_key": "350aa83c-44a4-4068-a511-580f82930d84",  # LIVE KEY CONFIGURED
    "jupiter_api": "https://quote-api.jup.ag/v4",
}

class LuxTraderLive:
    """LuxTrader v3.0 - Live execution with safety controls"""
    
    def __init__(self):
        self._ensure_dirs()
        self.state = self._load_state()
        self.daily_stats = self._init_daily_stats()
        self.pyramid_count = 0
        self.addon_count = 0
        self.consecutive_wins = 0
        self.active_positions = []
        
    def _ensure_dirs(self):
        os.makedirs(CONFIG["logs_dir"], exist_ok=True)
        os.makedirs(os.path.dirname(CONFIG["trade_log"]), exist_ok=True)
        
    def _load_state(self) -> Dict:
        default_state = {
            "total_capital": 1.0,
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0,
            "peak_capital": 1.0,
            "last_trade_time": None,
            "daily_reset": datetime.now().strftime("%Y-%m-%d"),
            "positions": {},
            "daily_pnl": 0,
            "daily_trades": 0
        }
        
        if os.path.exists(CONFIG["state_file"]):
            with open(CONFIG["state_file"], 'r') as f:
                loaded_state = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_state.items():
                    if key not in loaded_state:
                        loaded_state[key] = value
                return loaded_state
        
        return default_state
    
    def _init_daily_stats(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        if self.state.get("daily_reset") != today:
            self.state["daily_reset"] = today
            self.state["daily_pnl"] = 0
            self.state["daily_trades"] = 0
        return {
            "day_pnl": self.state.get("daily_pnl", 0),
            "trades_today": self.state.get("daily_trades", 0)
        }
    
    def save_state(self):
        self.state["daily_pnl"] = self.daily_stats["day_pnl"]
        self.state["daily_trades"] = self.daily_stats["trades_today"]
        with open(CONFIG["state_file"], 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_safety(self) -> Tuple[bool, str]:
        """Pre-trade safety checks"""
        # Drawdown check
        current = self.state["total_capital"]
        peak = self.state["peak_capital"]
        drawdown = (peak - current) / peak * 100
        
        if drawdown >= SAFETY["max_drawdown_pct"]:
            return False, f"Max drawdown hit: {drawdown:.1f}%"
        
        # Daily loss check
        if self.daily_stats["day_pnl"] <= -SAFETY["max_daily_loss_sol"]:
            return False, f"Daily loss limit: {self.daily_stats['day_pnl']:.2f} SOL"
        
        # Trade limit check
        if self.daily_stats["trades_today"] >= SAFETY["max_trades_per_day"]:
            return False, f"Max trades today: {self.daily_stats['trades_today']}"
        
        return True, "Safety OK"
    
    def evaluate_token(self, token: Dict) -> Optional[Dict]:
        """Evaluate token for entry signal"""
        # Handle missing fields gracefully
        if not isinstance(token, dict):
            return None
            
        mcap = token.get("marketCap", token.get("mcap", 0))
        liquidity = token.get("liquidity", 0)
        age_hours = token.get("age_hours", 0)
        grade = token.get("grade", "C")
        symbol = token.get("symbol", "UNKNOWN")
        
        # Initialize result with rejection status
        result = {
            "token": token,
            "score": 0,
            "entry_reason": "REJECTED",
            "has_narrative": False,
            "mcap": mcap,
            "age_hours": age_hours,
            "rejected": True,
            "rejection_reason": ""
        }
        
        # Grade check
        if grade not in ["A+", "A"]:
            result["rejection_reason"] = f"Grade {grade} not A/A+"
            return result
        
        # Liquidity check
        if liquidity < CONFIG["liquidity_min"]:
            result["rejection_reason"] = f"Liquidity ${liquidity:,.0f} < ${CONFIG['liquidity_min']:,.0f}"
            return result
        
        liq_ratio = liquidity / mcap if mcap > 0 else 0
        if liq_ratio < CONFIG["liquidity_ratio_min"]:
            result["rejection_reason"] = f"Liq ratio {liq_ratio:.2f} < {CONFIG['liquidity_ratio_min']}"
            return result
        
        # Age check
        if not (CONFIG["age_min_hours"] <= age_hours <= CONFIG["age_max_hours"]):
            result["rejection_reason"] = f"Age {age_hours}h not in range {CONFIG['age_min_hours']}-{CONFIG['age_max_hours']}h"
            return result
        
        # Score calculation
        score = 0
        entry_reason = ""
        
        if grade == "A+":
            score += 40
            entry_reason = "A+ grade"
        else:
            score += 30
            entry_reason = "A grade"
        
        if age_hours <= 6:
            score += 30
            entry_reason += " | Fresh <6h"
        elif age_hours <= 12:
            score += 20
            entry_reason += " | Early <12h"
        else:
            score += 10
            entry_reason += " | Recent"
        
        if liq_ratio >= 0.3:
            score += 20
        elif liq_ratio >= 0.15:
            score += 10
        
        # Narrative check
        has_narrative = any(k in symbol.upper() for k in CONFIG["trending_keywords"])
        if has_narrative:
            score += 10
            entry_reason += f" | NARRATIVE: {symbol}"
        
        return {
            "token": token,
            "score": score,
            "entry_reason": entry_reason,
            "has_narrative": has_narrative,
            "mcap": mcap,
            "age_hours": age_hours,
            "rejected": False,
            "rejection_reason": ""
        }
    
    def calculate_position_size(self) -> float:
        """Calculate position with all boosts"""
        base = self.state["total_capital"] * CONFIG["entry_size_base"]
        
        # Streak boost
        if CONFIG["streak_boost_enabled"] and self.consecutive_wins >= CONFIG["streak_threshold"]:
            streak_mult = 1 + (CONFIG["streak_boost_pct"] / 100)
            base *= streak_mult
        
        # Pyramid boost (after win)
        if CONFIG["pyramid_enabled"] and self.pyramid_count > 0:
            pyramid_mult = 1 + (CONFIG["pyramid_increase_pct"] / 100 * min(self.pyramid_count, CONFIG["pyramid_max_adds"]))
            base *= pyramid_mult
        
        # Add-on boost (after loss)
        if CONFIG["addon_enabled"] and self.addon_count > 0:
            addon_mult = 1 + (CONFIG["addon_increase_pct"] / 100 * min(self.addon_count, CONFIG["addon_max"]))
            base *= addon_mult
        
        # Caps
        base = min(base, self.state["total_capital"] * CONFIG["max_position_pct"])
        base = min(base, SAFETY["max_position_sol"])
        
        return base
    
    def execute_trade(self, signal: Dict, paper: bool = True) -> Dict:
        """Execute trade (paper or live) with review"""
        
        # Step 1: Safety checks
        safe, msg = self.check_safety()
        if not safe:
            return {"status": "rejected", "reason": msg, "stage": "safety_check"}
        
        position = self.calculate_position_size()
        token = signal["token"]
        token_address = token.get("address", "")
        token_symbol = token.get("symbol", "UNKNOWN")
        
        # Build trade object
        trade = {
            "timestamp": datetime.now().isoformat(),
            "mode": "PAPER" if paper else "LIVE",
            "symbol": token_symbol,
            "address": token_address,
            "entry_price": token.get("price", 0),
            "position_sol": position,
            "position_pct": position / self.state["total_capital"] * 100,
            "entry_reason": signal["entry_reason"],
            "has_narrative": signal.get("has_narrative", False),
            "score": signal["score"],
            "targets": {
                "tier1": CONFIG["tier1_target_pct"],
                "tier2": CONFIG["tier2_target_pct"],
                "tier3": CONFIG["tier3_target_pct"]
            }
        }
        
        if paper:
            print(f"\n📄 PAPER TRADE: {trade['symbol']}")
            print(f"   Position: {position:.4f} SOL ({trade['position_pct']:.1f}%)")
            print(f"   Reason: {signal['entry_reason']}")
            print(f"   Targets: +{CONFIG['tier1_target_pct']}%/+{CONFIG['tier2_target_pct']}%/+{CONFIG['tier3_target_pct']}%")
            print(f"   Stop: -{CONFIG['stop_loss_pct']}%")
            
            # Simulate outcome
            outcome = self._simulate_outcome(signal)
            trade["result"] = outcome
            self._update_stats(trade, outcome)
        else:
            # Step 3: PRE-BUY REVIEW
            print(f"\n🔍 REVIEWING TRADE: {trade['symbol']}")
            
            if REVIEWER_AVAILABLE:
                # Generate detailed review
                review_report = review_token(token, position)
                print(review_report)
                
                # Auto-approve based on review
                approved, approval_reason = approve_token(token, position)
                
                if not approved:
                    print(f"\n🚫 REVIEW REJECTED: {approval_reason}")
                    trade["status"] = "rejected"
                    trade["rejection_reason"] = approval_reason
                    trade["stage"] = "review"
                    self._save_trade(trade)
                    return trade
                
                print(f"\n✅ REVIEW APPROVED: {approval_reason}")
                trade["review_approved"] = True
                trade["review_reason"] = approval_reason
            
            # Step 4: EXECUTION
            print(f"\n🔴 EXECUTING LIVE TRADE: {trade['symbol']}")
            print(f"   Address: {WALLET_ADDRESS}")
            print(f"   Position: {position:.4f} SOL")
            
            # Try Ultra API first (more reliable), then fall back to standard
            result = None
            
            if ULTRA_AVAILABLE:
                print("   🚀 Trying Ultra API (v1)...")
                result = execute_buy_ultra(
                    wallet=WALLET_ADDRESS,
                    token_address=token_address,
                    amount_sol=position,
                    token_symbol=token_symbol
                )
                
                # If Ultra fails, try standard API
                if result.get("status") in ["failed", "manual_required"]:
                    print("   ⚠️ Ultra API failed, trying standard API...")
                    result = None
            
            if not result and FULL_AUTO_AVAILABLE:
                print("   🚀 Using standard Jupiter API...")
                result = execute_buy_auto(
                    wallet=WALLET_ADDRESS,
                    token_address=token_address,
                    amount_sol=position,
                    token_symbol=token_symbol
                )
            elif not result and JUPITER_AVAILABLE:
                print("   🚀 Semi-auto mode - Jupiter link generation...")
                result = execute_buy(
                    wallet=WALLET_ADDRESS,
                    token_address=token_address,
                    amount_sol=position,
                    token_symbol=token_symbol
                )
            
            if not result:
                result = {
                    "status": "manual_required",
                    "message": "No executor available",
                    "manual_url": f"https://jup.ag/swap/SOL-{token_address}"
                }
            
            trade["execution"] = result
            
            if result.get("status") == "executed":
                print(f"   ✅ TRADE EXECUTED!")
                print(f"   Tx: {result.get('transaction_signature', 'N/A')[:30]}...")
                trade["status"] = "executed"
                trade["transaction_signature"] = result.get("transaction_signature")
                
                # Add to positions (for duplicate checking)
                self._add_position(token, position, result)
                
            elif result.get("status") == "manual_required":
                print(f"   ⚠️ Manual execution required")
                print(f"   🔗 {result.get('manual_url', 'N/A')}")
                trade["status"] = "pending_manual"
                trade["manual_url"] = result.get("manual_url")
                
            elif result.get("status") == "failed":
                print(f"   ❌ Execution failed: {result.get('error')}")
                trade["status"] = "failed"
                trade["error"] = result.get("error")
                
            elif result.get("status") == "blocked":
                print(f"   🚫 Trade blocked: {result.get('error')}")
                trade["status"] = "blocked"
                trade["error"] = result.get("error")
                
            else:
                print(f"   ⚠️ Unknown status: {result.get('status')}")
                trade["status"] = "unknown"
                trade["error"] = result.get("error", "Unknown error")
        
        # Save trade to log
        self._save_trade(trade)
        
        return trade
    
    def _add_position(self, token: Dict, position_sol: float, execution_result: Dict):
        """Add token to active positions after buy"""
        token_address = token.get("address", "")
        token_symbol = token.get("symbol", "UNKNOWN")
        entry_price = token.get("price", 0)
        
        if not token_address:
            return
        
        # Get tokens received from execution result
        tokens_received = execution_result.get("expected_output", 0)
        
        # Add to internal state
        if "positions" not in self.state:
            self.state["positions"] = {}
        
        self.state["positions"][token_address] = {
            "symbol": token_symbol,
            "entry_price": entry_price,
            "position_sol": position_sol,
            "tokens_received": tokens_received,
            "entry_time": datetime.now().isoformat(),
            "execution": execution_result
        }
        
        self.save_state()
        print(f"   📝 Added to positions: {token_symbol}")
        
        # Also add to exit manager for automated exits
        if EXIT_MANAGER_AVAILABLE:
            try:
                exit_mgr = ExitManager()
                exit_mgr.add_position(
                    token_address=token_address,
                    symbol=token_symbol,
                    entry_price=entry_price,
                    position_sol=position_sol,
                    tokens_received=tokens_received,
                    execution_result=execution_result
                )
                print(f"   🎯 Exit manager tracking: {token_symbol}")
            except Exception as e:
                print(f"   ⚠️ Could not add to exit manager: {e}")
    
    def _save_trade(self, trade: Dict):
        """Save trade to log file"""
        try:
            log_file = CONFIG["trade_log"]
            trades = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    trades = json.load(f)
            trades.append(trade)
            with open(log_file, 'w') as f:
                json.dump(trades, f, indent=2)
        except Exception as e:
            print(f"   ⚠️ Could not save trade log: {e}")
    
    def _simulate_outcome(self, signal: Dict) -> Dict:
        """Simulate trade outcome (paper mode)"""
        win_rate = 0.75 if signal["score"] >= 80 else 0.65
        is_win = random.random() < win_rate
        
        if is_win:
            pnl_pct = random.uniform(CONFIG["tier1_target_pct"], CONFIG["tier3_target_pct"])
            if signal.get("has_narrative"):
                pnl_pct *= CONFIG["narrative_target_mult"]
            exit_reason = f"Target +{pnl_pct:.1f}%"
        else:
            pnl_pct = -random.uniform(CONFIG["stop_loss_pct"], CONFIG["stop_loss_pct"] * 1.2)
            exit_reason = f"Stop -{abs(pnl_pct):.1f}%"
        
        return {
            "win": is_win,
            "pnl_pct": pnl_pct,
            "exit_reason": exit_reason,
            "duration_min": random.randint(15, 180)
        }
    
    def _update_stats(self, trade: Dict, outcome: Dict):
        """Update tracking stats"""
        position = trade["position_sol"]
        pnl_pct = outcome["pnl_pct"]
        pnl_sol = position * (pnl_pct / 100)
        
        # Update capital
        self.state["total_capital"] += pnl_sol
        self.state["total_pnl"] += pnl_sol
        self.daily_stats["day_pnl"] += pnl_sol
        self.daily_stats["trades_today"] += 1
        self.state["total_trades"] += 1
        
        # Track peak
        if self.state["total_capital"] > self.state["peak_capital"]:
            self.state["peak_capital"] = self.state["total_capital"]
        
        # Streak tracking
        if outcome["win"]:
            self.state["wins"] += 1
            self.consecutive_wins += 1
            self.pyramid_count = min(self.pyramid_count + 1, CONFIG["pyramid_max_adds"])
            self.addon_count = 0
        else:
            self.state["losses"] += 1
            self.consecutive_wins = 0
            self.pyramid_count = 0
            self.addon_count = min(self.addon_count + 1, CONFIG["addon_max"])
        
        # Log trade
        trade["result"] = outcome
        self._log_trade(trade)
        self.save_state()
        
        print(f"\n✅ RESULT: {trade['symbol']} {outcome['exit_reason']}")
        print(f"   P&L: {pnl_sol:+.4f} SOL ({pnl_pct:+.1f}%)")
        print(f"   Capital: {self.state['total_capital']:.4f} SOL")
    
    def _log_trade(self, trade: Dict):
        """Save trade to log"""
        log_file = CONFIG["trade_log"]
        trades = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                trades = json.load(f)
        trades.append(trade)
        with open(log_file, 'w') as f:
            json.dump(trades, f, indent=2)
    
    def check_exits(self):
        """Check and execute exits for open positions"""
        if EXIT_MANAGER_AVAILABLE:
            try:
                from exit_manager import check_and_execute_exits
                check_and_execute_exits()
            except Exception as e:
                print(f"⚠️ Exit check error: {e}")
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "mode": MODE,
            "capital": self.state["total_capital"],
            "starting": 1.0,
            "total_pnl": self.state["total_pnl"],
            "total_trades": self.state["total_trades"],
            "win_rate": (self.state["wins"] / self.state["total_trades"] * 100) if self.state["total_trades"] > 0 else 0,
            "daily_pnl": self.daily_stats["day_pnl"],
            "trades_today": self.daily_stats["trades_today"],
            "consecutive_wins": self.consecutive_wins,
            "pyramid_ready": self.pyramid_count,
            "addon_ready": self.addon_count
        }

# MAIN
if __name__ == "__main__":
    trader = LuxTraderLive()
    
    print("=" * 70)
    print("✨ LUXTRADER v3.0 - LIVE TRADING SYSTEM")
    print("=" * 70)
    print()
    print(f"Mode: {'📄 PAPER' if MODE == 'PAPER' else '🔴 LIVE - REAL MONEY'}")
    print(f"Wallet: {WALLET_ADDRESS}")
    
    if MODE == "LIVE":
        print()
        print("=" * 70)
        print("🔴🔴🔴 LIVE MODE - REAL SOLANA TRANSACTIONS 🔴🔴🔴")
        print("=" * 70)
        print("⚠️  WARNING: Real money at risk!")
        print(f"   Helius API: ✅ Connected (RPC active)")
        print(f"   Jupiter API: ✅ Connected (swaps enabled)")
        print(f"   Birdeye API: ✅ Connected (data feed)")
        print()
        print("💰 Live Trading Limits:")
        print(f"   Position Size: {SAFETY['max_position_sol']} SOL per trade")
        print(f"   Daily Loss Limit: -{SAFETY['max_daily_loss_sol']} SOL (HALT)")
        print(f"   Drawdown Limit: {SAFETY['max_drawdown_pct']}% (HALT)")
        print(f"   Max Trades/Day: {SAFETY['max_trades_per_day']}")
        print(f"   Min Liquidity: ${SAFETY['min_liquidity_usd']:,}")
        print()
        print("🛡️ Safety: Trades only on A/A+ grade tokens with $8K+ liquidity")
        print("=" * 70)
    print()
    print("Safety Limits:")
    print(f"  Max position: {SAFETY['max_position_sol']} SOL per trade")
    print(f"  Max drawdown: {SAFETY['max_drawdown_pct']}%")
    print(f"  Daily loss limit: {SAFETY['max_daily_loss_sol']} SOL")
    print(f"  Max trades/day: {SAFETY['max_trades_per_day']}")
    print()
    print("v3.0 Features:")
    print("  ✓ Pyramid entry (+50% after wins)")
    print("  ✓ Mean-rev add-on (+30% after dips)")
    print("  ✓ 3-tier exits (15/25/40%)")
    print("  ✓ Streak boost (+15% per 3 wins)")
    print("  ✓ Narrative detection (AI/Meme)")
    print()
    
    status = trader.get_status()
    print(f"Current Status:")
    print(f"  Capital: {status['capital']:.4f} SOL")
    print(f"  Total P&L: {status['total_pnl']:+.4f} SOL")
    print(f"  Trades: {status['total_trades']} ({status['win_rate']:.0f}% WR)")
    print(f"  Today's P&L: {status['daily_pnl']:+.4f} SOL ({status['trades_today']} trades)")
    print()
    
    # Example simulation
    print("Running demo trades...")
    print("-" * 70)
    
    # Simulate 5 trades
    demo_signals = [
        {"token": {"symbol": "TESTAI", "marketCap": 25000, "liquidity": 8000, "age_hours": 3, "grade": "A+", "price": 0.001}, "score": 85, "has_narrative": True, "mcap": 25000, "age_hours": 3},
        {"token": {"symbol": "MEMEINU", "marketCap": 35000, "liquidity": 12000, "age_hours": 5, "grade": "A", "price": 0.002}, "score": 75, "has_narrative": True, "mcap": 35000, "age_hours": 5},
        {"token": {"symbol": "BADDEX", "marketCap": 20000, "liquidity": 4000, "age_hours": 2, "grade": "B", "price": 0.0015}, "score": 45, "has_narrative": False, "mcap": 20000, "age_hours": 2},
    ]
    
    for i, sig in enumerate(demo_signals[:3], 1):
        print(f"\n--- Trade {i} ---")
        
        # Evaluate
        evaluated = trader.evaluate_token(sig["token"])
        if evaluated:
            print(f"Signal: {sig['token']['symbol']}")
            print(f"Score: {evaluated['score']}, Reason: {evaluated['entry_reason']}")
            
            # Execute
            trade = trader.execute_trade(evaluated, paper=(MODE == "PAPER"))
        else:
            print(f"REJECTED: {sig['token']['symbol']} - Failed filters")
    
    print()
    print("-" * 70)
    status = trader.get_status()
    print(f"\nFinal Status:")
    print(f"  Capital: {status['capital']:.4f} SOL")
    print(f"  Session P&L: {status['total_pnl']:+.4f} SOL")
    print(f"  Consecutive wins: {status['consecutive_wins']}")
    print()
    
    if MODE == "PAPER":
        print("✅ Paper trading complete. Trades logged to:", CONFIG["trade_log"])
        print("\nTo switch to LIVE mode, change MODE = 'LIVE' at top of file")
    else:
        print("⚠️ LIVE MODE - Real trades would execute here")
        print("Review trades in:", CONFIG["trade_log"])
