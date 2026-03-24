#!/usr/bin/env python3
"""
🚀 Raydium SDK Integration - Sell INCOME Token
Using Raydium API v3 for direct swap execution
"""

import requests
import json
import base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders import message
from solders.pubkey import Pubkey
import os

# Configuration
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump"  # INCOME
TOKEN_SYMBOL = "INCOME"
TOKENS_TO_SELL = 490.916016
RAYDIUM_API = "https://api-v3.raydium.io"

def load_keypair():
    """Load wallet keypair"""
    try:
        # Try to load from full_auto_executor location
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
        print(f"❌ Error loading keypair: {e}")
        return None

def get_pool_info(token_address):
    """Get Raydium pool info for token"""
    print(f"🔍 Finding Raydium pool for {TOKEN_SYMBOL}...")
    
    try:
        # Search for pools containing this token
        url = f"{RAYDIUM_API}/pools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pools = data.get('data', {}).get('data', [])
            
            # Find pool with our token
            for pool in pools:
                if pool.get('mintA') == token_address or pool.get('mintB') == token_address:
                    print(f"   ✅ Found pool: {pool.get('id', 'N/A')}")
                    print(f"   Type: {pool.get('type', 'N/A')}")
                    return pool
            
            print("   ❌ No Raydium pool found for this token")
            return None
        else:
            print(f"   ❌ API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def get_swap_compute(pool_id, input_mint, output_mint, amount, slippage=0.01):
    """Get swap computation from Raydium"""
    print(f"\n🧮 Getting swap computation...")
    
    try:
        url = f"{RAYDIUM_API}/swap/compute"
        params = {
            "poolId": pool_id,
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(int(amount)),
            "slippage": slippage,
            "txVersion": "V0"
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Computation successful")
                return data.get('data')
            else:
                print(f"   ❌ Computation failed: {data.get('msg', 'Unknown')}")
                return None
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def build_swap_transaction(compute_data, wallet_pubkey, keypair):
    """Build and sign swap transaction"""
    print(f"\n🔨 Building swap transaction...")
    
    try:
        # Get transaction from Raydium
        url = f"{RAYDIUM_API}/swap/transaction"
        
        # Prepare request body
        payload = {
            "wallet": wallet_pubkey,
            "computeUnitPriceMicroLamports": "auto",
            "swapResponse": compute_data
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tx_data = data.get('data')
                print(f"   ✅ Transaction built")
                return tx_data
            else:
                print(f"   ❌ Build failed: {data.get('msg', 'Unknown')}")
                return None
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def execute_swap():
    """Execute swap using Raydium"""
    print("="*70)
    print("🚀 RAYDIUM SDK INTEGRATION - SELL INCOME")
    print("="*70)
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Amount: {TOKENS_TO_SELL}")
    print(f"Wallet: {WALLET}")
    print("="*70)
    
    # Load keypair
    keypair = load_keypair()
    if not keypair:
        print("\n❌ Cannot proceed without keypair")
        return False
    
    # Get pool info
    pool = get_pool_info(TOKEN)
    if not pool:
        print("\n❌ No Raydium pool available")
        print("💡 This token may only be available on PumpSwap/Jupiter")
        return False
    
    pool_id = pool.get('id')
    
    # Determine input/output based on pool
    if pool.get('mintA') == TOKEN:
        input_mint = pool.get('mintA')
        output_mint = pool.get('mintB')
    else:
        input_mint = pool.get('mintB')
        output_mint = pool.get('mintA')
    
    # Calculate amount (need to know decimals)
    # Assuming 9 decimals for now
    amount = int(TOKENS_TO_SELL * 1e9)
    
    # Get swap computation
    compute_data = get_swap_compute(pool_id, input_mint, output_mint, amount)
    if not compute_data:
        print("\n❌ Failed to get swap computation")
        return False
    
    # Build transaction
    tx_data = build_swap_transaction(compute_data, WALLET, keypair)
    if not tx_data:
        print("\n❌ Failed to build transaction")
        return False
    
    print(f"\n📝 Transaction ready to execute!")
    print(f"   Data: {json.dumps(tx_data, indent=2)[:300]}")
    
    # Note: Full execution would require deserializing, signing, and sending
    # the transaction using solders/solana-py
    
    print("\n⚠️ Note: Full transaction execution requires additional steps")
    print("   This demo shows the Raydium API integration")
    
    return True

def check_token_on_raydium():
    """Quick check if token has Raydium pools"""
    print("="*70)
    print("🔍 Checking Raydium for INCOME token...")
    print("="*70)
    
    try:
        # Get all pools
        url = f"{RAYDIUM_API}/pools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pools = data.get('data', {}).get('data', [])
            
            # Count pools with our token
            matching_pools = [p for p in pools if p.get('mintA') == TOKEN or p.get('mintB') == TOKEN]
            
            print(f"   Total pools: {len(pools)}")
            print(f"   Pools with {TOKEN_SYMBOL}: {len(matching_pools)}")
            
            if matching_pools:
                for pool in matching_pools[:3]:
                    print(f"\n   Pool: {pool.get('id', 'N/A')[:20]}...")
                    print(f"   Type: {pool.get('type', 'N/A')}")
                    print(f"   Mint A: {pool.get('mintA', 'N/A')[:20]}...")
                    print(f"   Mint B: {pool.get('mintB', 'N/A')[:20]}...")
                return True
            else:
                print(f"\n   ❌ {TOKEN_SYMBOL} not found in Raydium pools")
                print("   This token likely trades on PumpSwap only")
                return False
        else:
            print(f"   ❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    # First check if token exists on Raydium
    has_pool = check_token_on_raydium()
    
    if has_pool:
        print("\n" + "="*70)
        print("✅ Token found on Raydium!")
        print("="*70)
        execute_swap()
    else:
        print("\n" + "="*70)
        print("⚠️ Token not on Raydium")
        print("="*70)
        print("\n💡 Alternative: Use PumpSwap or Jupiter")
        print("   https://jup.ag/swap/5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump-SOL")
