#!/usr/bin/env python3
"""
🚀 SELL MEMECARD (via USDC)
Sell MEMECARD → USDC → SOL
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import FullAutoExecutor

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
AMOUNT_TOKENS = 941.52

def sell_via_usdc():
    """Two-step sell: MEMECARD → USDC → SOL"""
    print(f"\n💰 Step 1: Selling {AMOUNT_TOKENS} MEMECARD → USDC")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair")
        return False
    
    # Step 1: MEMECARD → USDC
    for slippage_bps in [1000, 2000, 5000]:
        print(f"\n   Trying {slippage_bps/100:.1f}% slippage...")
        
        try:
            quote = executor.get_quote(TOKEN, USDC, int(AMOUNT_TOKENS * 1e9), slippage_bps)
            if not quote:
                continue
            
            expected_usdc = int(quote.get('outAmount', 0)) / 1e6
            print(f"      Quote: ~{expected_usdc:.6f} USDC")
            
            swap_tx = executor.get_swap_transaction(quote, str(executor.keypair.pubkey()))
            if not swap_tx:
                continue
            
            signature = executor.sign_and_send_transaction(swap_tx)
            
            if signature:
                print(f"   ✅ Step 1 SUCCESS!")
                print(f"      TX: {signature}")
                print(f"      Got: ~{expected_usdc:.6f} USDC")
                
                # Step 2: USDC → SOL
                print(f"\n💰 Step 2: Selling {expected_usdc:.6f} USDC → SOL")
                
                import time
                time.sleep(2)
                
                quote2 = executor.get_quote(USDC, "So11111111111111111111111111111111111111112", 
                                           int(expected_usdc * 1e6), 100)
                if quote2:
                    expected_sol = int(quote2.get('outAmount', 0)) / 1e9
                    print(f"      Quote: ~{expected_sol:.6f} SOL")
                    
                    swap_tx2 = executor.get_swap_transaction(quote2, str(executor.keypair.pubkey()))
                    if swap_tx2:
                        signature2 = executor.sign_and_send_transaction(swap_tx2)
                        if signature2:
                            print(f"   ✅ Step 2 SUCCESS!")
                            print(f"      TX: {signature2}")
                            print(f"      Total received: ~{expected_sol:.6f} SOL")
                            return True
                
                print(f"   ⚠️ Step 2 failed, but you have {expected_usdc:.6f} USDC")
                return True  # Partial success
            
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    return False

if __name__ == "__main__":
    print("="*70)
    print("🚀 SELL MEMECARD (via USDC)")
    print("="*70)
    
    success = sell_via_usdc()
    
    if success:
        print("\n✅ Sell successful!")
    else:
        print("\n❌ Sell failed")
        print(f"   Manual: https://jup.ag/swap/{TOKEN}-SOL")
