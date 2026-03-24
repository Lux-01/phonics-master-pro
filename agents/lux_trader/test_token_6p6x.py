#!/usr/bin/env python3
"""
🧪 TEST BUY AND SELL - Token: 6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN
Buy 0.001 SOL, then immediately sell
"""

import sys
import time
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from ultra_executor import execute_buy_ultra, execute_sell_ultra
from full_auto_executor import execute_sell_auto

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"
TOKEN_SYMBOL = "TEST"

def test_buy():
    """Buy 0.001 SOL worth"""
    print("\n" + "="*60)
    print("🛒 TEST BUY (Ultra API)")
    print("="*60)
    print(f"Token: {TOKEN}")
    print(f"Amount: 0.001 SOL")
    
    result = execute_buy_ultra(WALLET, TOKEN, 0.001, TOKEN_SYMBOL)
    
    print(f"\n📊 Buy Result: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"✅ SUCCESS!")
        print(f"Tx: {result.get('transaction_signature', 'N/A')}")
        print(f"Received: {result.get('expected_output', 'N/A')} tokens")
        return True, result
    else:
        print(f"❌ Failed: {result.get('error', result.get('message', 'Unknown'))}")
        return False, result

def test_sell(tokens_received: float):
    """Sell tokens back"""
    print("\n" + "="*60)
    print("💰 TEST SELL")
    print("="*60)
    print(f"Token: {TOKEN}")
    print(f"Amount: {tokens_received:.6f} tokens")
    
    # Try Ultra API first
    print("\n📍 Trying Ultra API...")
    result = execute_sell_ultra(WALLET, TOKEN, tokens_received, TOKEN_SYMBOL)
    
    if result.get('status') == 'executed':
        print(f"✅ ULTRA SELL SUCCESS!")
        print(f"Tx: {result.get('transaction_signature', 'N/A')}")
        return True, "ultra"
    
    print(f"⚠️ Ultra failed: {result.get('error', result.get('message', 'Unknown'))}")
    
    # Try Standard API
    print("\n📍 Trying Standard API...")
    result = execute_sell_auto(WALLET, TOKEN, tokens_received, TOKEN_SYMBOL)
    
    if result.get('status') == 'executed':
        print(f"✅ STANDARD SELL SUCCESS!")
        print(f"Tx: {result.get('transaction_signature', 'N/A')}")
        return True, "standard"
    
    print(f"❌ Standard also failed: {result.get('error', result.get('message', 'Unknown'))}")
    return False, None

def main():
    print("\n" + "="*60)
    print("🚀 BUY AND SELL TEST")
    print("="*60)
    print(f"Token: 6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN")
    print(f"Wallet: {WALLET}")
    print(f"Testing: Buy 0.001 SOL → Sell immediately")
    
    # Step 1: Buy
    buy_success, buy_result = test_buy()
    
    if not buy_success:
        print("\n❌ Buy failed - stopping")
        return False
    
    tokens_received = buy_result.get('expected_output', 0)
    
    # Step 2: Sell immediately
    print(f"\n⏳ Selling immediately...")
    sell_success, method = test_sell(tokens_received)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Buy: {'✅ SUCCESS' if buy_success else '❌ FAILED'}")
    print(f"Sell: {'✅ SUCCESS (' + method + ')' if sell_success else '❌ FAILED'}")
    
    if buy_success and sell_success:
        print("\n🎉 FULL CYCLE COMPLETE!")
        print("✅ Buy and sell automation working!")
        return True
    elif buy_success and not sell_success:
        print("\n⚠️ Buy worked, sell failed")
        print(f"Manual sell: https://jup.ag/swap/{TOKEN}-SOL")
        return False
    else:
        print("\n❌ Both failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
