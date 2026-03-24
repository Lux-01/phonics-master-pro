#!/usr/bin/env python3
"""
🚀 OKX DEX API V6 Test - With chainIndex
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

def test_v6_with_chainindex():
    """Test V6 with chainIndex parameter"""
    
    # Solana chainIndex is likely 501 or 1399811149
    chain_indices = ["501", "1399811149", "solana", "SOL"]
    
    for chain_idx in chain_indices:
        print(f"\n🧪 Testing chainIndex={chain_idx}")
        
        url = "https://web3.okx.com/api/v6/dex/aggregator/all-tokens"
        params = {"chainIndex": chain_idx}
        
        query_string = f"?chainIndex={chain_idx}"
        headers = get_headers('GET', "/api/v6/dex/aggregator/all-tokens" + query_string)
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    print(f"   ✅ SUCCESS with chainIndex={chain_idx}!")
                    tokens = data.get("data", {}).get("tokens", [])
                    print(f"   Found {len(tokens)} tokens")
                    return chain_idx
                else:
                    print(f"   Error: {data.get('msg')}")
            else:
                print(f"   HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"   Error: {e}")
    
    return None

def test_quote_v6(chain_idx):
    """Test quote with working chainIndex"""
    print(f"\n🧪 Testing V6 Quote with chainIndex={chain_idx}")
    
    url = "https://web3.okx.com/api/v6/dex/aggregator/quote"
    params = {
        "chainIndex": chain_idx,
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/quote" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                print(f"   ✅ Quote SUCCESS!")
                print(f"   Data: {json.dumps(data, indent=2)[:400]}")
                return True
            else:
                print(f"   Error: {data.get('msg')}")
        else:
            print(f"   HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return False

def test_swap_v6(chain_idx):
    """Test swap with working chainIndex"""
    print(f"\n🧪 Testing V6 Swap with chainIndex={chain_idx}")
    
    url = "https://web3.okx.com/api/v6/dex/aggregator/swap"
    params = {
        "chainIndex": chain_idx,
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01",
        "userWalletAddress": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/swap" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                print(f"   ✅ Swap SUCCESS!")
                print(f"   Data: {json.dumps(data, indent=2)[:400]}")
                return True
            else:
                print(f"   Error: {data.get('msg')}")
        else:
            print(f"   HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return False

if __name__ == "__main__":
    print("="*70)
    print("🚀 OKX DEX API V6 - Finding chainIndex")
    print("="*70)
    
    # Find working chainIndex
    working_chain = test_v6_with_chainindex()
    
    if working_chain:
        print(f"\n✅ Found working chainIndex: {working_chain}")
        test_quote_v6(working_chain)
        test_swap_v6(working_chain)
    else:
        print("\n❌ No working chainIndex found")
