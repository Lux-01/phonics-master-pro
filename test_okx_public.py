#!/usr/bin/env python3
"""
🚀 OKX DEX API Test - Public Endpoints
Some endpoints don't require authentication
"""

import requests
import json

BASE_URL = "https://web3.okx.com/api/v5/dex/aggregator"

def test_public_endpoints():
    """Test endpoints that might be public"""
    
    endpoints = [
        ("All Tokens", "/all-tokens", {"chainId": "501"}),
        ("Quote", "/quote", {
            "chainId": "501",
            "fromTokenAddress": "So11111111111111111111111111111111111111112",
            "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "amount": "10000000",
            "slippage": "0.01"
        }),
    ]
    
    for name, path, params in endpoints:
        print(f"\n🧪 Testing {name} (no auth)...")
        url = f"{BASE_URL}{path}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0":
                    print(f"   ✅ SUCCESS! {name} works without auth")
                else:
                    print(f"   ⚠️ API Error: {data.get('msg')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("="*70)
    print("🚀 Testing OKX DEX Public Endpoints")
    print("="*70)
    test_public_endpoints()
