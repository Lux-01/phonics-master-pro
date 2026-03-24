#!/usr/bin/env python3
"""
🚀 PumpSwap Direct Integration
For tokens that trade on PumpSwap (pump.fun's DEX)
"""

import requests
import json
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
import base64

# Configuration
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump"  # INCOME
TOKEN_SYMBOL = "INCOME"
TOKENS_TO_SELL = 490.916016

def load_keypair():
    """Load wallet keypair"""
    try:
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')
        from full_auto_executor import FullAutoExecutor
        
        executor = FullAutoExecutor(WALLET)
        if executor.keypair:
            return executor.keypair
        else:
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_pumpswap_quote():
    """Get quote from PumpSwap"""
    print("="*70)
    print("🔍 Getting PumpSwap Quote...")
    print("="*70)
    
    # PumpSwap uses a bonding curve mechanism
    # The API endpoint might be different
    
    try:
        # Try Jupiter with specific dexes
        url = "https://quote-api.jup.ag/v6/quote"
        params = {
            "inputMint": TOKEN,
            "outputMint": "So11111111111111111111111111111111111111112",  # SOL
            "amount": str(int(TOKENS_TO_SELL * 1e9)),  # Assuming 9 decimals
            "slippageBps": "1000",  # 10% slippage for PumpSwap
            "dexes": "PumpSwap"  # Only use PumpSwap
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quote received!")
            print(f"   Out: {data.get('outAmount', 'N/A')}")
            print(f"   Price impact: {data.get('priceImpactPct', 'N/A')}%")
            return data
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def build_pumpswap_swap(quote_data):
    """Build swap transaction for PumpSwap"""
    print("\n" + "="*70)
    print("🔨 Building PumpSwap Transaction...")
    print("="*70)
    
    try:
        url = "https://quote-api.jup.ag/v6/swap"
        
        payload = {
            "userPublicKey": WALLET,
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": False,  # Important for PumpSwap
            "quoteResponse": quote_data
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transaction built!")
            return data.get('swapTransaction')
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def execute_swap():
    """Execute the full swap"""
    print("\n" + "="*70)
    print("🚀 PUMPSWAP SELL EXECUTION")
    print("="*70)
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Amount: {TOKENS_TO_SELL}")
    print(f"Wallet: {WALLET}")
    print("="*70)
    
    # Load keypair
    keypair = load_keypair()
    if not keypair:
        print("❌ No keypair loaded")
        return False
    
    # Get quote
    quote = get_pumpswap_quote()
    if not quote:
        print("\n❌ Failed to get quote")
        return False
    
    # Build swap
    swap_tx = build_pumpswap_swap(quote)
    if not swap_tx:
        print("\n❌ Failed to build swap")
        return False
    
    # Sign and send
    print("\n" + "="*70)
    print("✍️ Signing Transaction...")
    print("="*70)
    
    try:
        # Deserialize transaction
        tx_bytes = base64.b64decode(swap_tx)
        tx = VersionedTransaction.from_bytes(tx_bytes)
        
        # Sign
        signed_tx = VersionedTransaction(tx.message, [keypair])
        
        print("✅ Transaction signed!")
        
        # Send
        print("\n📤 Sending Transaction...")
        
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')
        from full_auto_executor import FullAutoExecutor
        
        executor = FullAutoExecutor(WALLET)
        
        # Use the RPC to send
        from solders.rpc.requests import SendVersionedTransaction
        from solders.rpc.config import RpcSendTransactionConfig
        
        result = executor.client.send_transaction(
            signed_tx,
            opts=RpcSendTransactionConfig(
                skip_preflight=False,
                preflight_commitment="confirmed"
            )
        )
        
        if result:
            tx_sig = result.value
            print(f"✅ SUCCESS!")
            print(f"   TX: {tx_sig}")
            print(f"   Explorer: https://solscan.io/tx/{tx_sig}")
            return True
        else:
            print("❌ Failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def manual_sell_options():
    """Show manual sell options"""
    print("\n" + "="*70)
    print("🔗 QUICK SELL LINKS")
    print("="*70)
    
    print("\n1. **Jupiter (Recommended)**")
    print(f"   https://jup.ag/swap/{TOKEN}-SOL")
    print("   - Set slippage to 10-20%")
    
    print("\n2. **PumpSwap Direct**")
    print("   https://pump.fun/swap")
    print("   - Connect wallet")
    print(f"   - Select {TOKEN_SYMBOL}")
    print("   - Swap to SOL")
    
    print("\n3. **Phantom Wallet**")
    print("   - Open Phantom")
    print("   - Go to Swap")
    print(f"   - Select {TOKEN_SYMBOL} → SOL")
    print("   - Set high slippage (10%)")

def main():
    print("\n" + "="*70)
    print("🚀 PUMPSWAP SELL ATTEMPT")
    print("="*70)
    
    # Try automated sell
    success = execute_swap()
    
    if not success:
        print("\n⚠️ Automated sell failed")
        manual_sell_options()
    
    return success

if __name__ == "__main__":
    main()
