#!/usr/bin/env python3
"""
🚀 MEME COIN TRADE TEST
Buy and sell MEMECARD token
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import execute_buy_auto, execute_sell_auto
import time

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"
TOKEN_SYMBOL = "MEMECARD"
BUY_AMOUNT_SOL = 0.001  # Small test amount

def test_buy():
    """Buy the meme coin"""
    print("\n" + "="*70)
    print("🛒 BUYING MEMECARD")
    print("="*70)
    print(f"Amount: {BUY_AMOUNT_SOL} SOL")
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Address: {TOKEN}")
    
    result = execute_buy_auto(WALLET, TOKEN, BUY_AMOUNT_SOL, TOKEN_SYMBOL)
    
    print(f"\n📊 Buy Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   TX: {result.get('transaction_signature', 'N/A')}")
        print(f"   Tokens Received: {result.get('expected_output', 'N/A')}")
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True, result
    elif result.get('status') == 'manual_required':
        print(f"   ⚠️ Manual execution required")
        print(f"   URL: {result.get('manual_url', 'N/A')}")
        return False, result
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
        return False, result

def test_sell(tokens_received: float):
    """Sell the meme coin back"""
    print("\n" + "="*70)
    print("💰 SELLING MEMECARD")
    print("="*70)
    print(f"Amount: {tokens_received} {TOKEN_SYMBOL}")
    
    result = execute_sell_auto(WALLET, TOKEN, tokens_received, TOKEN_SYMBOL)
    
    print(f"\n📊 Sell Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   TX: {result.get('transaction_signature', 'N/A')}")
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True
    elif result.get('status') == 'manual_required':
        print(f"   ⚠️ Manual execution required")
        print(f"   URL: {result.get('manual_url', 'N/A')}")
        return False
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
        return False

def main():
    print("="*70)
    print("🚀 MEME COIN TRADE TEST")
    print("="*70)
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Address: {TOKEN}")
    print(f"Buy Amount: {BUY_AMOUNT_SOL} SOL")
    print("="*70)
    
    # Step 1: Buy
    buy_success, buy_result = test_buy()
    
    if not buy_success:
        print("\n❌ Buy failed - cannot proceed")
        return False
    
    tokens_received = buy_result.get('expected_output', 0)
    
    if not tokens_received:
        print("\n❌ No tokens received")
        return False
    
    print(f"\n⏳ Waiting 5 seconds before selling...")
    time.sleep(5)
    
    # Step 2: Sell
    sell_success = test_sell(tokens_received)
    
    if sell_success:
        print("\n" + "="*70)
        print("🎉 MEME COIN TRADE COMPLETE!")
        print("="*70)
        print("✅ Buy executed successfully")
        print("✅ Sell executed successfully")
        print(f"\nToken: {TOKEN_SYMBOL}")
        print(f"Amount: {BUY_AMOUNT_SOL} SOL")
        return True
    else:
        print("\n⚠️ Buy succeeded but sell failed")
        print(f"   You have {tokens_received} {TOKEN_SYMBOL} tokens")
        print(f"   Sell manually at: https://jup.ag/swap/{TOKEN}-SOL")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
