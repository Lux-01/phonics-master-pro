#!/usr/bin/env python3
"""
🚀 SELL MEMECARD (Partial sell)
Sell 99% to account for price movement
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import FullAutoExecutor

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"
TOKEN_SYMBOL = "MEMECARD"
AMOUNT_TOKENS = 941.52  # 99% of 951.032241

def sell_memecard():
    """Sell with retry logic"""
    print(f"\n💰 Selling {AMOUNT_TOKENS} {TOKEN_SYMBOL} (99% of balance)")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair")
        return False
    
    # Try with increasing slippage
    slippage_options = [500, 1000, 2000, 5000]  # 5%, 10%, 20%, 50%
    
    for slippage_bps in slippage_options:
        print(f"\n   Trying {slippage_bps/100:.1f}% slippage...")
        
        try:
            # Get quote
            quote = executor.get_quote(
                TOKEN,
                "So11111111111111111111111111111111111111112",
                int(AMOUNT_TOKENS * 1e9),
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
            continue
    
    print(f"\n   ❌ All attempts failed")
    return False

if __name__ == "__main__":
    print("="*70)
    print("🚀 SELL MEMECARD (99% partial)")
    print("="*70)
    
    success = sell_memecard()
    
    if success:
        print("\n✅ Sell successful!")
    else:
        print("\n❌ Sell failed")
        print(f"   Manual sell: https://jup.ag/swap/{TOKEN}-SOL")
