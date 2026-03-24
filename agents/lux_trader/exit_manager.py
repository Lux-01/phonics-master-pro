#!/usr/bin/env python3
"""
🎯 LUXTRADER EXIT MANAGER
Handles 3-tier exit strategy for open positions

Exit Rules:
- Tier 1: Close 40% at +15%
- Tier 2: Close 30% at +25%
- Tier 3: Trail remaining 30% to +40%
- Hard stop: -7%
- Time stop: 4 hours
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests

# Import executors
try:
    from full_auto_executor import execute_sell_auto
    from ultra_executor import execute_sell_ultra
    from manual_sell_assistant import try_sell_or_manual
    from browser_automation_seller import execute_browser_sell_sync
    FULL_AUTO_AVAILABLE = True
    ULTRA_AVAILABLE = True
    MANUAL_ASSISTANT_AVAILABLE = True
    BROWSER_AUTO_AVAILABLE = True
except ImportError as e:
    FULL_AUTO_AVAILABLE = False
    ULTRA_AVAILABLE = False
    MANUAL_ASSISTANT_AVAILABLE = False
    BROWSER_AUTO_AVAILABLE = False
    print(f"⚠️ Some executors not available: {e}")

# Config
CONFIG = {
    "tier1_target_pct": 15,
    "tier2_target_pct": 25,
    "tier3_target_pct": 40,
    "trailing_stop_pct": 25,
    "stop_loss_pct": 7,
    "time_stop_minutes": 240,
    "position_file": "/home/skux/.openclaw/workspace/agents/lux_trader/live_positions.json",
    "trade_log": "/home/skux/.openclaw/workspace/agents/lux_trader/live_trades.json",
}

# Helius API for price checking
HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"


class ExitManager:
    """Manage exits for open positions"""
    
    def __init__(self):
        self.positions = self._load_positions()
        self.wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    
    def _load_positions(self) -> Dict:
        """Load open positions from file"""
        if os.path.exists(CONFIG["position_file"]):
            try:
                with open(CONFIG["position_file"], 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load positions: {e}")
        return {}
    
    def _save_positions(self):
        """Save positions to file"""
        try:
            os.makedirs(os.path.dirname(CONFIG["position_file"]), exist_ok=True)
            with open(CONFIG["position_file"], 'w') as f:
                json.dump(self.positions, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save positions: {e}")
    
    def get_token_price(self, token_address: str) -> Optional[float]:
        """Get current token price from Jupiter/Helius"""
        try:
            # Try Jupiter price API
            url = f"https://lite-api.jup.ag/price/v1?ids={token_address}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if token_address in data and data[token_address]:
                    return float(data[token_address])
        except Exception as e:
            print(f"⚠️ Price fetch error: {e}")
        return None
    
    def calculate_pnl_pct(self, position: Dict, current_price: float) -> float:
        """Calculate P&L percentage"""
        entry_price = position.get("entry_price", 0)
        if entry_price <= 0:
            return 0
        return ((current_price - entry_price) / entry_price) * 100
    
    def check_exit_conditions(self, token_address: str, position: Dict) -> Tuple[bool, str, float]:
        """
        Check if position should be exited
        
        Returns:
            (should_exit, reason, sell_pct)
        """
        current_price = self.get_token_price(token_address)
        if not current_price:
            return False, "no_price", 0
        
        pnl_pct = self.calculate_pnl_pct(position, current_price)
        entry_time = datetime.fromisoformat(position.get("entry_time", datetime.now().isoformat()))
        elapsed_minutes = (datetime.now() - entry_time).total_seconds() / 60
        
        # Get current tier status
        tier1_done = position.get("tier1_exited", False)
        tier2_done = position.get("tier2_exited", False)
        tier3_active = position.get("tier3_active", False)
        
        # Check hard stop loss
        if pnl_pct <= -CONFIG["stop_loss_pct"]:
            return True, f"stop_loss_{pnl_pct:.1f}pct", 100  # Sell all
        
        # Check time stop
        if elapsed_minutes >= CONFIG["time_stop_minutes"]:
            return True, f"time_stop_{elapsed_minutes:.0f}min", 100  # Sell all
        
        # Tier 1: Close 40% at +15%
        if not tier1_done and pnl_pct >= CONFIG["tier1_target_pct"]:
            return True, f"tier1_target_{pnl_pct:.1f}pct", 40
        
        # Tier 2: Close 30% at +25%
        if tier1_done and not tier2_done and pnl_pct >= CONFIG["tier2_target_pct"]:
            return True, f"tier2_target_{pnl_pct:.1f}pct", 30
        
        # Tier 3: Trail remaining 30% to +40%
        if tier2_done and not tier3_active and pnl_pct >= CONFIG["trailing_stop_pct"]:
            # Activate trailing stop
            position["tier3_active"] = True
            position["trailing_high"] = pnl_pct
            self._save_positions()
            print(f"   🎯 Tier 3 trailing activated at +{pnl_pct:.1f}%")
        
        if tier3_active:
            # Update trailing high
            if pnl_pct > position.get("trailing_high", pnl_pct):
                position["trailing_high"] = pnl_pct
                self._save_positions()
            
            # Check if hit trailing stop (10% pullback from high)
            trailing_high = position.get("trailing_high", pnl_pct)
            if pnl_pct <= trailing_high - 10:  # 10% pullback
                return True, f"tier3_trailing_{pnl_pct:.1f}pct", 100  # Sell remaining
            
            # Check if hit final target
            if pnl_pct >= CONFIG["tier3_target_pct"]:
                return True, f"tier3_target_{pnl_pct:.1f}pct", 100  # Sell remaining
        
        return False, "hold", 0
    
    def execute_partial_sell(self, token_address: str, position: Dict, sell_pct: float, reason: str) -> Dict:
        """Execute partial sell with multiple fallbacks: API -> Browser -> Manual"""
        symbol = position.get("symbol", "UNKNOWN")
        total_tokens = position.get("tokens_received", 0)
        
        if total_tokens <= 0:
            return {"status": "error", "error": "No tokens to sell"}
        
        # Calculate amount to sell
        sell_amount = total_tokens * (sell_pct / 100)
        
        print(f"\n🔴 EXECUTING SELL: {symbol}")
        print(f"   Reason: {reason}")
        print(f"   Sell %: {sell_pct}%")
        print(f"   Tokens: {sell_amount:.6f}")
        
        result = None
        
        # Method 1: Try API methods (Ultra -> Standard -> v2)
        if MANUAL_ASSISTANT_AVAILABLE:
            print(f"\n📍 Trying API methods...")
            result = try_sell_or_manual(
                self.wallet, 
                token_address, 
                sell_amount, 
                symbol,
                reason=reason
            )
        
        # Method 2: If API failed, try browser automation
        if (not result or result.get("status") != "executed") and BROWSER_AUTO_AVAILABLE:
            print(f"\n📍 API methods failed, trying browser automation...")
            print(f"   ⚠️ Browser will open - please ensure wallet is connected")
            try:
                browser_result = execute_browser_sell_sync(
                    self.wallet,
                    token_address,
                    sell_amount,
                    symbol
                )
                if browser_result.get("status") == "executed":
                    result = browser_result
                    print(f"   ✅ Browser automation succeeded!")
                else:
                    print(f"   ⚠️ Browser automation failed: {browser_result.get('error', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ Browser automation error: {e}")
        
        # Method 3: If all automated methods failed, provide manual link
        if not result or result.get("status") not in ["executed", "manual_required"]:
            print(f"\n📍 All automated methods failed, providing manual link...")
            result = {
                "status": "manual_required",
                "message": "All automated methods failed - manual sell required",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL",
                "raydium_url": f"https://raydium.io/swap/?inputCurrency={token_address}&outputCurrency=SOL",
                "token_symbol": symbol,
                "amount_tokens": sell_amount,
                "reason": reason,
                "urgency": "high" if reason in ["stop_loss", "time_stop"] else "normal"
            }
        
        # Update position if executed
        if result.get("status") == "executed":
            print(f"   ✅ SELL EXECUTED!")
            print(f"   Method: {result.get('method', 'API')}")
            if result.get('transaction_signature'):
                print(f"   Tx: {result.get('transaction_signature', 'N/A')[:30]}...")
            
            # Update position
            position["tokens_remaining"] = total_tokens - sell_amount
            position["last_exit"] = reason
            position["last_exit_time"] = datetime.now().isoformat()
            
            # Track which tiers are done
            if sell_pct == 40:
                position["tier1_exited"] = True
            elif sell_pct == 30:
                position["tier2_exited"] = True
            elif sell_pct == 100:
                # Complete exit
                position["fully_exited"] = True
                position["exit_time"] = datetime.now().isoformat()
            
            self._save_positions()
            
        elif result.get("status") == "manual_required":
            print(f"\n   ⚠️ MANUAL SELL REQUIRED")
            print(f"   Token: {symbol}")
            print(f"   Amount: {sell_amount:.6f} tokens")
            print(f"   Reason: {reason}")
            print(f"   Urgency: {result.get('urgency', 'normal').upper()}")
            print(f"\n   🌐 Quick Links:")
            print(f"      Jupiter: {result.get('manual_url', 'N/A')}")
            print(f"      Raydium: {result.get('raydium_url', 'N/A')}")
            print(f"\n   ⏰ Please sell as soon as possible!")
            # Position NOT updated - will retry on next check
        
        return result
    
    def monitor_positions(self):
        """Monitor all positions and execute exits"""
        print("\n" + "="*60)
        print("🎯 EXIT MANAGER - Checking Positions")
        print("="*60)
        
        if not self.positions:
            print("No open positions to monitor")
            return
        
        print(f"Monitoring {len(self.positions)} position(s)...")
        
        for token_address, position in list(self.positions.items()):
            symbol = position.get("symbol", "UNKNOWN")
            
            # Skip fully exited positions
            if position.get("fully_exited", False):
                continue
            
            print(f"\n📊 {symbol}:")
            
            # Check exit conditions
            should_exit, reason, sell_pct = self.check_exit_conditions(token_address, position)
            
            if should_exit:
                result = self.execute_partial_sell(token_address, position, sell_pct, reason)
                
                if result.get("status") == "executed":
                    print(f"   ✅ Exit executed: {reason}")
                elif result.get("status") == "manual_required":
                    print(f"   ⚠️ Manual sell required")
                    print(f"   URL: {result.get('manual_url', 'N/A')}")
                else:
                    print(f"   ❌ Sell failed: {result.get('error', 'Unknown')}")
            else:
                current_price = self.get_token_price(token_address)
                if current_price:
                    pnl_pct = self.calculate_pnl_pct(position, current_price)
                    print(f"   Holding... P&L: {pnl_pct:+.1f}%")
    
    def add_position(self, token_address: str, symbol: str, entry_price: float, 
                     position_sol: float, tokens_received: float, execution_result: Dict):
        """Add new position after buy"""
        self.positions[token_address] = {
            "symbol": symbol,
            "entry_price": entry_price,
            "position_sol": position_sol,
            "tokens_received": tokens_received,
            "tokens_remaining": tokens_received,
            "entry_time": datetime.now().isoformat(),
            "execution": execution_result,
            "tier1_exited": False,
            "tier2_exited": False,
            "tier3_active": False,
            "trailing_high": 0,
            "fully_exited": False
        }
        self._save_positions()
        print(f"   📝 Position added: {symbol} ({tokens_received:.2f} tokens)")


# Convenience function
def check_and_execute_exits():
    """Check all positions and execute exits"""
    manager = ExitManager()
    manager.monitor_positions()


if __name__ == "__main__":
    print("LuxTrader Exit Manager")
    print("="*60)
    check_and_execute_exits()
