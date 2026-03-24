#!/usr/bin/env python3
"""
🧪 LUXTRADER TEST - 0.01 SOL Buy/Sell
Token: Barrel Index (BBX) - GB2K9Ft9GuCAh4qn4da67oLYiWKmnCRtYdgzKQARpump
Grade A | Score: 14.5 | Liquidity: $21,389
"""

import sys
import time
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import execute_buy_auto, execute_sell_auto

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "GB2K9Ft9GuCAh4qn4da67oLYiWKmnCRtYdgzKQARpump"
TOKEN_SYMBOL = "BBX"
BUY_AMOUNT_SOL = 0.01

def test_buy():
    """Test buying 0.01 SOL worth of BBX"""
    print("\n" + "="*60)
    print("🛒 LUXTRADER TEST BUY")
    print("="*60)
    print(f"Token: {TOKEN_SYMBOL} ({TOKEN})")
    print(f"Amount: {BUY_AMOUNT_SOL} SOL")
    print(f"Wallet: {WALLET}")
    print(f"Grade: A | Score: 14.5 | Liq: $21,389")
    
    result = execute_buy_auto(WALLET, TOKEN, BUY_AMOUNT_SOL, TOKEN_SYMBOL)
    
    print(f"\n📊 Buy Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
        print(f"   Expected Output: {result.get('expected_output', 'N/A')} {TOKEN_SYMBOL}")
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
    print("💰 LUXTRADER TEST SELL")
    print("="*60)
    print(f"Token: {TOKEN_SYMBOL}")
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
    """Run LuxTrader buy and sell test"""
    print("\n" + "="*60)
    print("🚀 LUXTRADER LIVE TEST - 0.01 SOL")
    print("="*60)
    print(f"Token: Barrel Index (BBX)")
    print(f"CA: {TOKEN}")
    print(f"Buy Amount: {BUY_AMOUNT_SOL} SOL")
    print(f"Strategy: LuxTrader v3.1 LIVE")
    print("="*60)
    
    # Step 1: Buy
    buy_success, buy_result = test_buy()
    
    if not buy_success:
        print("\n❌ Buy failed - cannot proceed to sell")
        print("\nTest Result: FAILED")
        return False
    
    # Get tokens received
    tokens_received = buy_result.get('expected_output', 0)
    
    if tokens_received:
        print(f"\n⏳ Waiting 10 seconds before selling...")
        time.sleep(10)
        
        # Step 2: Sell
        sell_success = test_sell(tokens_received)
        
        print("\n" + "="*60)
        print("🎯 LUXTRADER TEST RESULTS")
        print("="*60)
        
        if sell_success:
            print("✅ BUY: Executed successfully")
            print("✅ SELL: Executed successfully")
            print("\n🎉 FULL AUTO TRADING WORKS!")
            print("LuxTrader can successfully buy and sell tokens.")
            return True
        else:
            print("✅ BUY: Executed successfully")
            print("❌ SELL: Failed")
            print("\n⚠️ Partial success - buy works, sell needs attention")
            return False
    else:
        print("\n⚠️ Buy succeeded but no token amount returned")
        print("   Cannot proceed with sell test")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
