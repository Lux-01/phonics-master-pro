#!/usr/bin/env python3
"""
🚀 OKX DEX API V6 Test
Trying V6 endpoints
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

def test_v6_endpoints():
    """Try V6 API endpoints"""
    
    # Possible V6 endpoints
    endpoints = [
        ("V6 Tokens", "/api/v6/dex/aggregator/all-tokens", {"chainId": "501"}),
        ("V6 Quote", "/api/v6/dex/aggregator/quote", {
            "chainId": "501",
            "fromTokenAddress": "So11111111111111111111111111111111111111112",
            "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "amount": "10000000",
            "slippage": "0.01"
        }),
        ("V6 Swap", "/api/v6/dex/aggregator/swap", {
            "chainId": "501",
            "fromTokenAddress": "So11111111111111111111111111111111111111112",
            "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "amount": "10000000",
            "slippage": "0.01",
            "userWalletAddress": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
        }),
    ]
    
    for name, path, params in endpoints:
        print(f"\n🧪 Testing {name}...")
        url = f"https://web3.okx.com{path}"
        
        query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        headers = get_headers('GET', path + query_string)
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    print(f"   ✅ SUCCESS!")
                    print(f"   Data: {json.dumps(data, indent=2)[:300]}")
                else:
                    print(f"   ⚠️ API Error: {data.get('msg')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                print(f"   {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_dex_api_path():
    """Try different base paths"""
    
    bases = [
        "https://www.okx.com/api/v5/dex",
        "https://www.okx.com/api/v6/dex",
        "https://web3.okx.com/api/v5/dex",
        "https://web3.okx.com/api/v6/dex",
    ]
    
    for base in bases:
        print(f"\n🧪 Testing base: {base}")
        url = f"{base}/aggregator/all-tokens"
        params = {"chainId": "501"}
        
        query_string = "?chainId=501"
        headers = get_headers('GET', f"/api/v5/dex/aggregator/all-tokens" if "v5" in base else "/api/v6/dex/aggregator/all-tokens")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}")
            else:
                print(f"   Error: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("="*70)
    print("🚀 Testing OKX DEX API V6")
    print("="*70)
    
    test_v6_endpoints()
    test_dex_api_path()
