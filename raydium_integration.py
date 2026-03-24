#!/usr/bin/env python3
"""
🚀 Raydium Direct Contract Integration
Using solana-py to interact with Raydium pools directly
"""

import requests
import json
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from solders.message import Message
import base64

# Raydium Program IDs
RAYDIUM_AMM_V4 = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
RAYDIUM_CLMM = Pubkey.from_string("CAMMCzo5YL8w4VzuUVhkKpA6FccXgV9eZxMhXjE1f7J")  # Concentrated Liquidity
TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

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
            print(f"✅ Keypair loaded: {executor.keypair.pubkey()}")
            return executor.keypair
        else:
            print("❌ No keypair found")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def find_raydium_pools():
    """Find Raydium pools for token"""
    print("="*70)
    print("🔍 Searching for Raydium pools...")
    print("="*70)
    
    # Try different Raydium API endpoints
    endpoints = [
        "https://api.raydium.io/v2/main/pools",
        "https://api.raydium.io/v2/ammPools",
        "https://api-v3.raydium.io/pools/info/ids",
    ]
    
    for endpoint in endpoints:
        print(f"\n   Trying: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())[:5]}")
                
                # Check for our token
                pools = data.get('data', data.get('pools', []))
                if isinstance(pools, list):
                    for pool in pools:
                        if isinstance(pool, dict):
                            mint_a = pool.get('mintA', pool.get('baseMint', ''))
                            mint_b = pool.get('mintB', pool.get('quoteMint', ''))
                            
                            if TOKEN in [mint_a, mint_b]:
                                print(f"\n   ✅ Found pool!")
                                print(f"   ID: {pool.get('id', pool.get('poolId', 'N/A'))}")
                                return pool
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n   ❌ No pools found via API")
    return None

def check_dexscreener():
    """Check DEX info for token"""
    print("\n" + "="*70)
    print("🔍 Checking DEX Screener for pool info...")
    print("="*70)
    
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{TOKEN}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                pair = data[0]
                dex_id = pair.get('dexId', 'Unknown')
                pool_id = pair.get('pairAddress', 'Unknown')
                
                print(f"   DEX: {dex_id}")
                print(f"   Pool: {pool_id}")
                print(f"   Liquidity: ${pair.get('liquidity', {}).get('usd', 0):,.0f}")
                
                if dex_id.lower() in ['raydium', 'raydium v4', 'raydium cpmm']:
                    print(f"\n   ✅ Token trades on Raydium!")
                    return True, pool_id
                else:
                    print(f"\n   ⚠️ Token trades on {dex_id}, not Raydium")
                    return False, dex_id
                    
    except Exception as e:
        print(f"   Error: {e}")
    
    return False, None

def create_raydium_swap_instruction():
    """Create Raydium swap instruction"""
    print("\n" + "="*70)
    print("🔨 Creating Raydium swap instruction...")
    print("="*70)
    
    # This requires:
    # 1. Pool account
    # 2. Token accounts
    # 3. Proper instruction data
    
    # Raydium swap instruction layout is complex
    # Requires specific account ordering and instruction data
    
    print("   ⚠️ Raydium contract integration requires:")
    print("   - Pool account address")
    print("   - Token account addresses")
    print("   - Proper instruction encoding")
    print("   - Account metas in correct order")
    
    print("\n   💡 Recommendation: Use Raydium SDK (TypeScript)")
    print("   Or use Jupiter which aggregates Raydium")
    
    return None

def alternative_solutions():
    """Show alternative solutions"""
    print("\n" + "="*70)
    print("💡 ALTERNATIVE SOLUTIONS")
    print("="*70)
    
    print("\n1. **Jupiter (Retry with higher slippage)**")
    print(f"   https://jup.ag/swap/{TOKEN}-SOL")
    print("   - Try 5%, 10%, or 20% slippage")
    print("   - Wait 2-3 minutes between attempts")
    
    print("\n2. **PumpSwap Direct**")
    print("   https://pump.fun/swap")
    print("   - Native DEX for this token")
    print("   - May have better liquidity")
    
    print("\n3. **Phantom Wallet**")
    print("   - Built-in swap aggregator")
    print("   - Often finds routes when APIs fail")
    
    print("\n4. **Raydium UI (if pool exists)**")
    print(f"   https://raydium.io/swap/?inputMint={TOKEN}")
    
    print("\n5. **TypeScript SDK** (For future automation)")
    print("   npm install @raydium-io/raydium-sdk-v2")
    print("   - Full swap functionality")
    print("   - Better maintained than Python")

def main():
    print("\n" + "="*70)
    print("🚀 RAYDIUM SDK INTEGRATION")
    print("="*70)
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Address: {TOKEN}")
    print(f"Amount: {TOKENS_TO_SELL}")
    print("="*70)
    
    # Check where token trades
    is_raydium, pool_info = check_dexscreener()
    
    if is_raydium:
        print("\n✅ Token found on Raydium!")
        print(f"   Pool: {pool_info}")
        
        # Try to find via API
        pool = find_raydium_pools()
        
        if pool:
            print("\n🔄 Would proceed with swap...")
            print("   (Full implementation requires TypeScript SDK)")
        else:
            print("\n⚠️ Pool found on DEXScreener but not in Raydium API")
            print("   May be a new pool not yet indexed")
    
    # Show alternatives
    alternative_solutions()

if __name__ == "__main__":
    main()
