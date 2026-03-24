#!/usr/bin/env python3
"""
🧪 TEST USDC BUY AND SELL
Buy 0.001 SOL of USDC, then sell it back to SOL
Safe test with stablecoin
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import execute_buy_auto, execute_sell_auto

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_SYMBOL = "USDC"
SOL_MINT = "So11111111111111111111111111111111111111112"

def test_buy():
    """Test buying 0.001 SOL worth of USDC"""
    print("\n" + "="*60)
    print("🛒 TEST BUY: SOL → USDC")
    print("="*60)
    print(f"Input: 0.001 SOL")
    print(f"Output: USDC")
    print(f"Wallet: {WALLET}")
    
    result = execute_buy_auto(WALLET, USDC_MINT, 0.001, USDC_SYMBOL)
    
    print(f"\n📊 Buy Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
        print(f"   Expected USDC: {result.get('expected_output', 'N/A')}")
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

def test_sell(usdc_amount: float):
    """Test selling USDC back to SOL"""
    print("\n" + "="*60)
    print("💰 TEST SELL: USDC → SOL")
    print("="*60)
    print(f"Input: {usdc_amount} USDC")
    print(f"Output: SOL")
    print(f"Wallet: {WALLET}")
    
    result = execute_sell_auto(WALLET, USDC_MINT, usdc_amount, USDC_SYMBOL)
    
    print(f"\n📊 Sell Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
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
    print("🚀 USDC BUY AND SELL TEST")
    print("="*60)
    print(f"Testing with 0.001 SOL ↔ USDC")
    print(f"This is a safe test with stablecoin")
    print(f"API: https://lite-api.jup.ag/swap/v1")
    
    # Step 1: Buy
    buy_success, buy_result = test_buy()
    
    if not buy_success:
        print("\n❌ Buy failed - cannot proceed to sell")
        return False
    
    # Get USDC received
    usdc_received = buy_result.get('expected_output', 0)
    
    if usdc_received:
        print(f"\n⏳ Waiting 3 seconds before selling...")
        import time
        time.sleep(3)
        
        # Step 2: Sell
        sell_success = test_sell(usdc_received)
        
        if sell_success:
            print("\n" + "="*60)
            print("🎉 BUY AND SELL TEST COMPLETE!")
            print("="*60)
            print("✅ Buy executed: SOL → USDC")
            print("✅ Sell executed: USDC → SOL")
            print("\nLuxTrader is working correctly!")
            return True
        else:
            print("\n⚠️ Buy succeeded but sell failed")
            print("   You may need to sell manually")
            return False
    else:
        print("\n⚠️ Buy succeeded but no USDC amount returned")
        print("   Cannot proceed with sell test")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
