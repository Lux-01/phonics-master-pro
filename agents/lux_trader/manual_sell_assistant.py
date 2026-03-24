#!/usr/bin/env python3
"""
🤖 MANUAL SELL ASSISTANT
When auto-sell fails, provides manual sell link for user

Flow:
1. Try auto-sell (Ultra → Standard → v2)
2. If all fail → Generate manual sell link
3. Send notification with link
4. Log for tracking
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from typing import Dict, Optional
from datetime import datetime
import json
import os

from ultra_executor import execute_sell_ultra
from full_auto_executor import execute_sell_auto
from full_auto_executor_v2 import execute_sell_v2

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
NOTIFICATIONS_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/manual_sell_queue.json"


class ManualSellAssistant:
    """Assistant that tries auto-sell then falls back to manual"""
    
    def __init__(self):
        self.wallet = WALLET
        self.pending_sells = self._load_pending()
    
    def _load_pending(self) -> list:
        """Load pending manual sells"""
        if os.path.exists(NOTIFICATIONS_FILE):
            try:
                with open(NOTIFICATIONS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_pending(self):
        """Save pending manual sells"""
        with open(NOTIFICATIONS_FILE, 'w') as f:
            json.dump(self.pending_sells, f, indent=2)
    
    def try_sell_with_fallback(self, token_address: str, amount_tokens: float,
                                  token_symbol: str = "UNKNOWN", token_decimals: int = 9,
                                  reason: str = "exit") -> Dict:
        """
        Try to sell automatically, fallback to manual if needed
        """
        print(f"\n{'='*60}")
        print("🤖 MANUAL SELL ASSISTANT")
        print(f"{'='*60}")
        print(f"Token: {token_symbol}")
        print(f"Amount: {amount_tokens:.6f} tokens")
        print(f"Reason: {reason}")
        
        # Try all auto methods
        auto_result = self._try_auto_sell(token_address, amount_tokens, token_symbol, token_decimals)
        
        if auto_result.get('status') == 'executed':
            print(f"\n✅ AUTO-SELL SUCCESS!")
            return auto_result
        
        # Auto failed - generate manual sell info
        print(f"\n⚠️ Auto-sell failed - generating manual sell link...")
        
        manual_info = self._generate_manual_sell(token_address, amount_tokens, token_symbol, reason)
        
        # Save to queue
        self._queue_manual_sell(manual_info)
        
        # Display for user
        self._display_manual_sell(manual_info)
        
        return {
            "status": "manual_required",
            "auto_attempted": True,
            "auto_failed_reason": auto_result.get('error', 'Unknown'),
            "manual_info": manual_info
        }
    
    def _try_auto_sell(self, token_address: str, amount_tokens: float,
                       token_symbol: str, token_decimals: int) -> Dict:
        """Try all auto-sell methods"""
        
        # Method 1: Ultra API
        print(f"\n📍 Trying Ultra API...")
        try:
            result = execute_sell_ultra(self.wallet, token_address, amount_tokens, token_symbol, token_decimals)
            if result.get('status') == 'executed':
                return result
            print(f"   ⚠️ Ultra failed: {result.get('error', result.get('message', 'Unknown'))}")
        except Exception as e:
            print(f"   ❌ Ultra exception: {e}")
        
        # Method 2: Standard API
        print(f"\n📍 Trying Standard API...")
        try:
            result = execute_sell_auto(self.wallet, token_address, amount_tokens, token_symbol)
            if result.get('status') == 'executed':
                return result
            print(f"   ⚠️ Standard failed: {result.get('error', result.get('message', 'Unknown'))}")
        except Exception as e:
            print(f"   ❌ Standard exception: {e}")
        
        # Method 3: v2 with retries
        print(f"\n📍 Trying v2 with retries...")
        try:
            result = execute_sell_v2(self.wallet, token_address, amount_tokens, token_symbol, token_decimals)
            if result.get('status') == 'executed':
                return result
            print(f"   ⚠️ v2 failed: {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ v2 exception: {e}")
        
        return {"status": "failed", "error": "All auto methods failed"}
    
    def _generate_manual_sell(self, token_address: str, amount_tokens: float,
                              token_symbol: str, reason: str) -> Dict:
        """Generate manual sell information"""
        
        # Calculate approximate SOL value (rough estimate)
        # In real implementation, would get actual price
        estimated_sol = amount_tokens * 0.0001  # Placeholder
        
        manual_info = {
            "token_address": token_address,
            "token_symbol": token_symbol,
            "amount_tokens": amount_tokens,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "jupiter_url": f"https://jup.ag/swap/{token_address}-SOL",
            "raydium_url": f"https://raydium.io/swap/?inputCurrency={token_address}&outputCurrency=SOL",
            "estimated_sol": estimated_sol,
            "wallet": self.wallet,
            "status": "pending_manual",
            "urgency": "high" if reason in ["stop_loss", "time_stop"] else "normal"
        }
        
        return manual_info
    
    def _queue_manual_sell(self, manual_info: Dict):
        """Add to manual sell queue"""
        self.pending_sells.append(manual_info)
        self._save_pending()
        print(f"   ✅ Added to manual sell queue")
    
    def _display_manual_sell(self, manual_info: Dict):
        """Display manual sell information to user"""
        print(f"\n{'='*60}")
        print("🔗 MANUAL SELL REQUIRED")
        print(f"{'='*60}")
        print(f"Token: {manual_info['token_symbol']}")
        print(f"Amount: {manual_info['amount_tokens']:.6f} tokens")
        print(f"Reason: {manual_info['reason']}")
        print(f"Urgency: {manual_info['urgency'].upper()}")
        print(f"\n🌐 QUICK SELL LINK:")
        print(f"   {manual_info['jupiter_url']}")
        print(f"\n📋 INSTRUCTIONS:")
        print(f"   1. Click the link above")
        print(f"   2. Connect your wallet: {self.wallet[:20]}...")
        print(f"   3. Review the swap details")
        print(f"   4. Confirm the transaction")
        print(f"\n⏰ Please sell as soon as possible!")
        print(f"{'='*60}")
    
    def get_pending_sells(self) -> list:
        """Get list of pending manual sells"""
        return self.pending_sells
    
    def mark_sold(self, token_address: str):
        """Mark a token as manually sold"""
        for sell in self.pending_sells:
            if sell['token_address'] == token_address:
                sell['status'] = 'completed'
                sell['completed_at'] = datetime.now().isoformat()
        self._save_pending()
        print(f"✅ Marked {token_address[:20]}... as sold")


# Convenience function
def try_sell_or_manual(token_address: str, amount_tokens: float,
                       token_symbol: str = "UNKNOWN", token_decimals: int = 9,
                       reason: str = "exit") -> Dict:
    """Try to sell, fallback to manual if needed"""
    assistant = ManualSellAssistant()
    return assistant.try_sell_with_fallback(token_address, amount_tokens, token_symbol, token_decimals, reason)


def show_pending_sells():
    """Show all pending manual sells"""
    assistant = ManualSellAssistant()
    pending = assistant.get_pending_sells()
    
    print(f"\n{'='*60}")
    print("📋 PENDING MANUAL SELLS")
    print(f"{'='*60}")
    
    if not pending:
        print("No pending sells!")
        return
    
    for i, sell in enumerate(pending, 1):
        if sell.get('status') == 'pending_manual':
            print(f"\n{i}. {sell['token_symbol']}")
            print(f"   Amount: {sell['amount_tokens']:.6f} tokens")
            print(f"   Reason: {sell['reason']}")
            print(f"   Urgency: {sell['urgency']}")
            print(f"   Link: {sell['jupiter_url']}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "pending":
        show_pending_sells()
    else:
        # Test with a token
        print("Manual Sell Assistant Test")
        print("="*60)
        
        # This would be called from exit_manager when auto-sell fails
        result = try_sell_or_manual(
            "32CdQdBUxbCsLy5AUHWmyidfwhgGUr9N573NBUrDpump",
            35.29,
            "TEST",
            reason="stop_loss"
        )
        
        print(f"\nResult: {json.dumps(result, indent=2)}")
