#!/usr/bin/env python3
"""
🚀 OKX DEX API V6 - Full Working Test
Test selling MEMECARD using OKX DEX API
"""

import requests
import json
import hmac
import hashlib
import base64
from datetime import datetime, timezone

API_KEY = "911fb148-e0fe-41b5-bab5-6f9a1a902137"
SECRET_KEY = "4290D41E30734568BC09F683FFB01C96"
PASSPHRASE = "Fellmongery11!"
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# Token addresses
SOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
MEMECARD = "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"

def get_timestamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def sign_message(message, secret):
    mac = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')

def get_headers(method, request_path, body=''):
    timestamp = get_timestamp()
    if body:
        message = timestamp + method.upper() + request_path + body
    else:
        message = timestamp + method.upper() + request_path
    
    signature = sign_message(message, SECRET_KEY)
    
    return {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

def get_swap_quote(from_token, to_token, amount):
    """Get swap quote from OKX DEX"""
    url = "https://web3.okx.com/api/v6/dex/aggregator/quote"
    params = {
        "chainIndex": "501",
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": str(amount),
        "slippage": "0.01"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/quote" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                return data.get("data", [])
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

def build_swap_transaction(from_token, to_token, amount, wallet):
    """Build swap transaction"""
    url = "https://web3.okx.com/api/v6/dex/aggregator/swap"
    
    # V6 uses slippagePercent (as integer percentage)
    params = {
        "chainIndex": "501",
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": str(amount),
        "slippagePercent": "1",  # 1% slippage (integer)
        "userWalletAddress": wallet,
        "gasLevel": "high"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/swap" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                return data.get("data", [])
            else:
                print(f"   API Error: {data.get('msg')}")
        else:
            print(f"   HTTP Error: {response.status_code}")
            print(f"   {response.text[:300]}")
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_sol_to_usdc():
    """Test SOL → USDC swap"""
    print("="*70)
    print("🧪 TEST: SOL → USDC Swap")
    print("="*70)
    
    amount = 10000000  # 0.01 SOL in lamports
    
    # Get quote
    print("   Getting quote...")
    quote = get_swap_quote(SOL, USDC, amount)
    
    if quote:
        print(f"   ✅ Quote received")
        print(f"   Amount Out: {quote[0].get('toTokenAmount', 'N/A')} USDC units")
    else:
        print("   ❌ Failed to get quote")
        return False
    
    # Build swap
    print("\n   Building swap transaction...")
    swap = build_swap_transaction(SOL, USDC, amount, WALLET)
    
    if swap:
        print(f"   ✅ Swap transaction built!")
        tx_data = swap[0].get('tx', {})
        if tx_data:
            print(f"   Transaction ready to sign and send")
            print(f"   Router: {swap[0].get('router', 'N/A')}")
            return True
    else:
        print("   ❌ Failed to build swap")
    
    return False

def test_memecard_to_sol():
    """Test MEMECARD → SOL swap (the real test!)"""
    print("\n" + "="*70)
    print("🧪 TEST: MEMECARD → SOL Swap")
    print("="*70)
    
    # Amount of MEMECARD to sell (941.52 tokens)
    # Need to know decimals - assuming 9 like most Solana tokens
    amount = int(941.52 * 1e9)  # 941520000000
    
    print(f"   Selling: 941.52 MEMECARD")
    print(f"   Amount in base units: {amount}")
    
    # Get quote
    print("\n   Getting quote...")
    quote = get_swap_quote(MEMECARD, SOL, amount)
    
    if quote:
        print(f"   ✅ Quote received!")
        print(f"   Expected SOL out: {quote[0].get('toTokenAmount', 'N/A')}")
        print(f"   Price impact: {quote[0].get('priceImpact', 'N/A')}")
        
        # Build swap
        print("\n   Building swap transaction...")
        swap = build_swap_transaction(MEMECARD, SOL, amount, WALLET)
        
        if swap:
            print(f"   ✅ SUCCESS! Swap transaction built")
            tx_data = swap[0].get('tx', {})
            if tx_data:
                print(f"\n   📝 Transaction ready!")
                print(f"   Data: {json.dumps(tx_data, indent=2)[:400]}")
                return True
        else:
            print("   ❌ Failed to build swap")
    else:
        print("   ❌ Failed to get quote")
        print("   This might mean OKX doesn't have a route for this token")
    
    return False

def main():
    print("\n" + "="*70)
    print("🚀 OKX DEX API V6 - MEMECARD SELL TEST")
    print("="*70)
    print(f"Wallet: {WALLET}")
    print(f"Token: MEMECARD (2X4NET...FeJJ)")
    print(f"Amount: 941.52 tokens")
    print("="*70)
    
    # First test with SOL → USDC to make sure API works
    test_sol_to_usdc()
    
    # Then test MEMECARD → SOL
    print("\n")
    success = test_memecard_to_sol()
    
    if success:
        print("\n" + "="*70)
        print("🎉 SUCCESS! OKX DEX can sell MEMECARD!")
        print("="*70)
        print("\nNext: Sign and send the transaction to complete the sell")
    else:
        print("\n" + "="*70)
        print("⚠️ MEMECARD sell failed")
        print("="*70)
        print("\nPossible reasons:")
        print("- Token not supported by OKX DEX")
        print("- Insufficient liquidity")
        print("- Wrong token decimals")
        print("\nTry: Check token decimals or use a different DEX")

if __name__ == "__main__":
    main()
