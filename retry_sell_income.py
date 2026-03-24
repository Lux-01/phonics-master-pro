#!/usr/bin/env python3
"""
🚀 RETRY SELL - INCOME Token with Multiple Attempts
Try different slippage levels and methods
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import execute_sell_auto
import time

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump"
TOKEN_SYMBOL = "INCOME"
TOKENS_TO_SELL = 490.916016

def try_sell_with_retry():
    """Try selling with multiple attempts"""
    
    print("="*70)
    print(f"🔄 RETRY SELL - {TOKEN_SYMBOL}")
    print("="*70)
    print(f"Amount: {TOKENS_TO_SELL} tokens")
    print(f"Token: {TOKEN}")
    print("="*70)
    
    # Try multiple times with delays
    for attempt in range(1, 4):
        print(f"\n🔄 Attempt {attempt}/3...")
        print(f"   Waiting {attempt * 3} seconds for route refresh...")
        time.sleep(attempt * 3)
        
        result = execute_sell_auto(WALLET, TOKEN, TOKENS_TO_SELL, TOKEN_SYMBOL)
        
        if result.get('status') == 'executed':
            print(f"\n✅ SUCCESS on attempt {attempt}!")
            print(f"   TX: {result.get('transaction_signature', 'N/A')}")
            print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
            return True
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
    
    print("\n" + "="*70)
    print("❌ All attempts failed")
    print("="*70)
    print(f"\n💡 Manual sell link:")
    print(f"   https://jup.ag/swap/{TOKEN}-SOL")
    print(f"\n⚠️ You still hold {TOKENS_TO_SELL} {TOKEN_SYMBOL}")
    
    return False

if __name__ == "__main__":
    try_sell_with_retry()
