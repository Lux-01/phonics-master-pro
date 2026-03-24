#!/usr/bin/env python3
"""
🧪 TEST USDC BUY AND SELL (Enhanced Version)
Buy 0.001 SOL of USDC, then sell using enhanced seller with retry logic
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

import asyncio
from full_auto_executor import execute_buy_auto
from lux_enhanced_seller import LuxEnhancedSeller

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_SYMBOL = "USDC"

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
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True, result
    else:
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        return False, result

async def test_sell_enhanced(usdc_amount: float):
    """Test selling USDC using enhanced seller with retry logic"""
    print("\n" + "="*60)
    print("💰 TEST SELL: USDC → SOL (Enhanced)")
    print("="*60)
    print(f"Input: {usdc_amount} USDC")
    print(f"Output: SOL")
    print(f"Wallet: {WALLET}")
    print(f"Using: Dynamic slippage + retry logic")
    
    # Create enhanced seller
    seller = LuxEnhancedSeller(WALLET)
    
    # Build position data
    position = {
        'price_change_24h': 0,
        'age_hours': 0.1,  # Just bought
    }
    
    # Execute smart sell
    result = await seller.execute_smart_sell(
        token_address=USDC_MINT,
        token_symbol=USDC_SYMBOL,
        position=position,
        exit_reason="test_sell"
    )
    
    print(f"\n📊 Sell Result:")
    print(f"   Success: {result.success}")
    print(f"   Attempts: {result.total_attempts}")
    print(f"   Time: {result.execution_time_ms}ms")
    
    if result.success:
        print(f"   ✅ SUCCESS!")
        print(f"   Sold: {result.amount_sold:.6f} USDC")
        print(f"   Received: {result.amount_received:.6f} SOL")
        return True
    else:
        print(f"   ❌ Failed: {result.error_message}")
        if result.sell_attempts:
            print(f"\n   Attempt History:")
            for attempt in result.sell_attempts:
                print(f"      #{attempt.attempt_number}: {attempt.status} (slippage: {attempt.slippage_bps/100:.1f}%)")
        return False

def main():
    """Run buy and sell test"""
    print("\n" + "="*60)
    print("🚀 USDC BUY AND SELL TEST (Enhanced)")
    print("="*60)
    print(f"Testing with 0.001 SOL ↔ USDC")
    print(f"Buy: Standard executor")
    print(f"Sell: Enhanced seller with retry logic")
    
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
        
        # Step 2: Sell using enhanced seller
        sell_success = asyncio.run(test_sell_enhanced(usdc_received))
        
        if sell_success:
            print("\n" + "="*60)
            print("🎉 BUY AND SELL TEST COMPLETE!")
            print("="*60)
            print("✅ Buy executed: SOL → USDC")
            print("✅ Sell executed: USDC → SOL (Enhanced)")
            print("\nLuxTrader enhanced seller is working!")
            return True
        else:
            print("\n⚠️ Buy succeeded but sell failed")
            print("   Enhanced seller attempted multiple strategies")
            return False
    else:
        print("\n⚠️ Buy succeeded but no USDC amount returned")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
