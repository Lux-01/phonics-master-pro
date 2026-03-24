#!/usr/bin/env python3
"""
🧪 TEST BUY AND SELL - EpCeDYpPRzwa8tSitgyNLjExh88n2M9nRuJQHuCiFgJV
Buy 0.001 SOL, then sell the tokens received
"""

import sys
import time
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import execute_buy_auto, execute_sell_auto

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "EpCeDYpPRzwa8tSitgyNLjExh88n2M9nRuJQHuCiFgJV"
TOKEN_SYMBOL = "TEST"

def test_buy():
    """Test buying 0.001 SOL worth of token"""
    print("\n" + "="*60)
    print("🛒 TEST BUY")
    print("="*60)
    print(f"Token: {TOKEN}")
    print(f"Amount: 0.001 SOL")
    print(f"Wallet: {WALLET}")
    
    result = execute_buy_auto(WALLET, TOKEN, 0.001, TOKEN_SYMBOL)
    
    print(f"\n📊 Buy Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
        print(f"   Expected Output: {result.get('expected_output', 'N/A')}")
        print(f"   Price Impact: {result.get('price_impact', 'N/A')}")
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True, result
    elif result.get('status') == 'manual_required':
        print(f"   ⚠️ Manual execution required")
        print(f"   Reason: {result.get('message', 'Unknown')}")
        print(f"   URL: {result.get('manual_url', 'N/A')}")
        return False, result
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        return False, result

def test_sell(tokens_received: float):
    """Test selling tokens back"""
    print("\n" + "="*60)
    print("💰 TEST SELL")
    print("="*60)
    print(f"Token: {TOKEN}")
    print(f"Amount: {tokens_received} tokens")
    print(f"Wallet: {WALLET}")
    
    result = execute_sell_auto(WALLET, TOKEN, tokens_received, TOKEN_SYMBOL)
    
    print(f"\n📊 Sell Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
        print(f"   Expected SOL: {result.get('expected_output_sol', 'N/A')}")
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True
    elif result.get('status') == 'manual_required':
        print(f"   ⚠️ Manual execution required")
        print(f"   Reason: {result.get('message', 'Unknown')}")
        print(f"   URL: {result.get('manual_url', 'N/A')}")
        return False
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        return False

def main():
    """Run buy and sell test"""
    print("\n" + "="*60)
    print("🚀 BUY AND SELL TEST")
    print("="*60)
    print(f"Token: EpCeDYpPRzwa8tSitgyNLjExh88n2M9nRuJQHuCiFgJV")
    print(f"Testing with new Jupiter API endpoint")
    print(f"API: https://lite-api.jup.ag/swap/v1")
    
    # Step 1: Buy
    buy_success, buy_result = test_buy()
    
    if not buy_success:
        print("\n❌ Buy failed - cannot proceed to sell")
        return False
    
    # Get tokens received
    tokens_received = buy_result.get('expected_output', 0)
    
    if tokens_received:
        print(f"\n⏳ Waiting 5 seconds before selling...")
        time.sleep(5)
        
        # Step 2: Sell
        sell_success = test_sell(tokens_received)
        
        if sell_success:
            print("\n" + "="*60)
            print("🎉 BUY AND SELL TEST COMPLETE!")
            print("="*60)
            print("✅ Buy executed successfully")
            print("✅ Sell executed successfully")
            print("\nFull auto trading is working!")
            return True
        else:
            print("\n⚠️ Buy succeeded but sell failed")
            print("   You may need to sell manually")
            return False
    else:
        print("\n⚠️ Buy succeeded but no token amount returned")
        print("   Cannot proceed with sell test")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
