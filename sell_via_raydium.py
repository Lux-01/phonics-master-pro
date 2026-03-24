#!/usr/bin/env python3
"""
🚀 SELL VIA RAYDIUM API
Alternative to Jupiter for selling tokens
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

import requests
import json
import base64
from full_auto_executor import FullAutoExecutor

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TOKEN = "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"
AMOUNT_TOKENS = 941.52

def get_raydium_quote():
    """Get quote from Raydium"""
    print("🔍 Checking Raydium...")
    
    try:
        # Raydium API endpoint
        url = "https://api-v3.raydium.io/pools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pools = data.get('data', {}).get('data', [])
            
            # Find pool for our token
            for pool in pools:
                if pool.get('mintA', '') == TOKEN or pool.get('mintB', '') == TOKEN:
                    print(f"   Found Raydium pool!")
                    print(f"   Pool ID: {pool.get('id', 'N/A')}")
                    return pool
                    
        print("   No Raydium pool found")
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

def try_birdeye_swap():
    """Try Birdeye swap API"""
    print("\n🔍 Trying Birdeye Swap API...")
    
    BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"
    
    try:
        # Birdeye swap API
        url = "https://public-api.birdeye.so/defi/swap"
        headers = {"X-API-KEY": BIRDEYE_KEY}
        
        payload = {
            "fromAddress": TOKEN,
            "toAddress": "So11111111111111111111111111111111111111112",
            "amount": int(AMOUNT_TOKENS * 1e9),
            "slippage": 10,  # 10%
            "fromWallet": WALLET
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Birdeye swap data received")
            return data
        else:
            print(f"   Birdeye swap failed: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   Error: {e}")
        return None

def try_meteora():
    """Try Meteora pools"""
    print("\n🔍 Checking Meteora...")
    
    try:
        # Meteora API
        url = "https://app.meteora.ag/api/pools"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            pools = response.json()
            
            for pool in pools:
                if TOKEN in str(pool):
                    print(f"   Found Meteora pool!")
                    return pool
                    
        print("   No Meteora pool found")
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

def try_dexscreener_swap():
    """Get swap URL from DexScreener"""
    print("\n🔍 Getting DexScreener swap URL...")
    
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{TOKEN}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                pair = data[0]
                
                # Get dexId
                dex_id = pair.get('dexId', '')
                
                print(f"   Token traded on: {dex_id}")
                
                # Return swap URLs
                urls = {
                    'jupiter': f"https://jup.ag/swap/{TOKEN}-SOL",
                    'raydium': f"https://raydium.io/swap/?inputMint={TOKEN}&outputMint=So11111111111111111111111111111111111111112",
                    'orca': f"https://orca.so/?tokenIn={TOKEN}&tokenOut=So11111111111111111111111111111111111111112",
                    'meteora': f"https://app.meteora.ag/pools?address={TOKEN}"
                }
                
                return urls
    except Exception as e:
        print(f"   Error: {e}")
    
    return None

def main():
    print("="*70)
    print("🚀 ALTERNATIVE SELL METHODS")
    print("="*70)
    print(f"Token: MEMECARD")
    print(f"Amount: {AMOUNT_TOKENS} tokens")
    print(f"Wallet: {WALLET}")
    print("="*70)
    
    # Try Raydium
    raydium_pool = get_raydium_quote()
    
    # Try Birdeye
    birdeye_result = try_birdeye_swap()
    
    # Try Meteora
    meteora_pool = try_meteora()
    
    # Get swap URLs
    print("\n" + "="*70)
    print("🔗 DIRECT SWAP LINKS:")
    print("="*70)
    
    urls = try_dexscreener_swap()
    if urls:
        print(f"\n1. Jupiter (tried):")
        print(f"   {urls['jupiter']}")
        
        print(f"\n2. Raydium:")
        print(f"   {urls['raydium']}")
        
        print(f"\n3. Orca:")
        print(f"   {urls['orca']}")
        
        print(f"\n4. Meteora:")
        print(f"   {urls['meteora']}")
    
    print("\n" + "="*70)
    print("💡 RECOMMENDATION:")
    print("="*70)
    print("Try these in order:")
    print("1. Raydium - Often has better routes for newer tokens")
    print("2. Orca - Good for established tokens")
    print("3. Jupiter (retry) - Routes refresh every few minutes")
    print("\nOr use Phantom wallet's built-in swap:")
    print("   Open Phantom → Swap → Select MEMECARD → Swap to SOL")

if __name__ == "__main__":
    main()
