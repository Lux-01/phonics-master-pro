#!/usr/bin/env python3
"""
🧪 SIMPLE USDC SELL TEST
Direct sell execution using FullAutoExecutor methods
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

import base64
from full_auto_executor import FullAutoExecutor

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def simple_sell_usdc(amount_usdc: float):
    """Simple direct sell with higher slippage tolerance"""
    print(f"\n💰 Selling {amount_usdc} USDC → SOL")
    print(f"Wallet: {WALLET}")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair loaded")
        return False
    
    # Convert USDC amount (6 decimals)
    amount_raw = int(amount_usdc * 1_000_000)
    
    # Try with increasing slippage
    slippage_options = [100, 250, 500, 1000]  # 1%, 2.5%, 5%, 10%
    
    for slippage_bps in slippage_options:
        print(f"\n   Trying with {slippage_bps/100:.1f}% slippage...")
        
        try:
            # Get quote
            quote = executor.get_quote(
                USDC_MINT,
                "So11111111111111111111111111111111111111112",
                amount_raw,
                slippage_bps
            )
            
            if not quote:
                print(f"      Quote failed")
                continue
            
            expected_sol = int(quote.get('outAmount', 0)) / 1e9
            print(f"      Quote: ~{expected_sol:.6f} SOL")
            
            # Build swap
            swap_tx = executor.get_swap_transaction(quote, str(executor.keypair.pubkey()))
            
            if not swap_tx:
                print(f"      Swap build failed")
                continue
            
            # Sign and send
            signature = executor.sign_and_send_transaction(swap_tx)
            
            if signature:
                print(f"   ✅ SUCCESS!")
                print(f"      TX: {signature}")
                print(f"      Explorer: https://solscan.io/tx/{signature}")
                return True
            else:
                print(f"      ❌ Send failed")
                
        except Exception as e:
            print(f"      Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n   ❌ All attempts failed")
    return False

if __name__ == "__main__":
    # Sell the USDC we bought
    usdc_amount = 0.088497  # From previous buy
    
    print("="*60)
    print("🚀 SIMPLE USDC SELL TEST")
    print("="*60)
    
    success = simple_sell_usdc(usdc_amount)
    
    if success:
        print("\n✅ Sell successful!")
    else:
        print("\n❌ Sell failed - may need manual execution")
        print(f"   Sell manually at: https://jup.ag/swap/USDC-SOL")
