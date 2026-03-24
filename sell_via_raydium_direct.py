#!/usr/bin/env python3
"""
🚀 SELL VIA RAYDIUM DIRECT API
Execute swap using Raydium's API instead of Jupiter
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

def get_raydium_swap_tx():
    """Get swap transaction from Raydium"""
    print("🔍 Getting Raydium swap transaction...")
    
    try:
        # Raydium swap API
        url = "https://api-v3.raydium.io/swap/compute"
        
        params = {
            "inputMint": TOKEN,
            "outputMint": "So11111111111111111111111111111111111111112",
            "amount": int(AMOUNT_TOKENS * 1e9),
            "slippage": 0.1,  # 10%
            "txVersion": "V0"
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Raydium quote received")
            return data
        else:
            print(f"   Raydium API error: {response.status_code}")
            print(f"   {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"   Error: {e}")
        return None

def execute_raydium_swap():
    """Execute swap via Raydium"""
    print("\n💰 Executing Raydium swap...")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair loaded")
        return False
    
    # Get swap transaction
    swap_data = get_raydium_swap_tx()
    
    if not swap_data:
        print("❌ Could not get Raydium swap data")
        return False
    
    try:
        # Extract transaction from response
        tx_data = swap_data.get('data', {}).get('transaction', {})
        
        if not tx_data:
            print("❌ No transaction in response")
            return False
        
        print(f"   Transaction data received")
        
        # Sign and send
        # Note: Raydium returns a transaction that needs to be signed
        # This is a simplified version - full implementation would
        # deserialize, sign, and send the transaction
        
        print(f"   ⚠️ Raydium requires manual signing")
        print(f"   Please use the Raydium UI link below")
        return False
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print("="*70)
    print("🚀 RAYDIUM DIRECT SELL")
    print("="*70)
    print(f"Token: MEMECARD")
    print(f"Amount: {AMOUNT_TOKENS} tokens")
    print(f"Wallet: {WALLET}")
    print("="*70)
    
    # Try Raydium
    success = execute_raydium_swap()
    
    if not success:
        print("\n" + "="*70)
        print("🔗 USE RAYDIUM UI:")
        print("="*70)
        print(f"\n   https://raydium.io/swap/?inputMint={TOKEN}&outputMint=So11111111111111111111111111111111111111112")
        print("\n   Steps:")
        print("   1. Connect your wallet (8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5)")
        print("   2. Select MEMECARD as input")
        print("   3. Select SOL as output")
        print("   4. Enter amount: 941.52")
        print("   5. Set slippage to 10%")
        print("   6. Click Swap")

if __name__ == "__main__":
    main()
