#!/usr/bin/env python3
"""Test rug check using DexScreener + Helius mix"""

import requests
import json
import time

# Try DexScreener first
token_ca = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

print(f"Testing Rug Check via DexScreener on BONK")
print("-" * 60)

# DexScreener API
url = f"https://api.dexscreener.com/latest/dex/tokens/{token_ca}"
print(f"Fetching from DexScreener...")
resp = requests.get(url, timeout=30)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    pairs = data.get("pairs", [])
    print(f"Found {len(pairs)} pairs")
    
    if pairs:
        pair = pairs[0]
        print(f"\n📊 Token Info:")
        print(f"   Name: {pair.get('baseToken', {}).get('name', 'N/A')}")
        print(f"   Symbol: {pair.get('baseToken', {}).get('symbol', 'N/A')}")
        print(f"   Price: ${pair.get('priceUsd', 'N/A')}")
        print(f"   Market Cap: ${pair.get('marketCap', 'N/A')}")
        print(f"   Holders: {pair.get('holders', 'N/A')}")
        print(f"   Liquidity: ${pair.get('liquidity', {}).get('usd', 'N/A')}")
        print(f"   Liquidity Locked: {pair.get('liquidity', {}).get('quote', 0) > 0}")
        
        # Get first few txns from Helius to check wallets
        HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
        HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
        
        print(f"\n🔍 Checking recent transactions...")
        tx_resp = requests.post(
            HELIUS_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [token_ca, {"limit": 20}]
            },
            timeout=30
        )
        
        if tx_resp.status_code == 200:
            tx_data = tx_resp.json()
            signatures = tx_data.get("result", [])
            print(f"Found {len(signatures)} recent transactions")
            
            if signatures:
                print(f"\nRecent transactions (first 5):")
                for i, sig in enumerate(signatures[:5]):
                    print(f"   {i+1}. {sig.get('signature', 'N/A')[:30]}...")
                    print(f"      Time: {sig.get('blockTime', 'N/A')}")
        else:
            print(f"Error: {tx_resp.status_code}")

print("\n" + "=" * 60)
print("Rug Check Logic:")
print("1. Get top holders via getTokenLargestAccounts")
print("2. Check each wallet's SOL balance")
print("3. Count 'dust wallets' (<0.01 SOL)")
print("4. If 4+/5 are dust → RUG (-10 pts)")
print("5. If 3/5 are dust → WARNING (-5 pts)")
print("=" * 60)
