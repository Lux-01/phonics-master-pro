#!/usr/bin/env python3
"""
🚀 OKX DEX API Test Script with Full Authentication
Tests the API key with proper HMAC SHA256 signature
"""

import requests
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone

# API Configuration
API_KEY = "911fb148-e0fe-41b5-bab5-6f9a1a902137"
SECRET_KEY = "4290D41E30734568BC09F683FFB01C96"
PASSPHRASE = "Fellmongery11!"
BASE_URL = "https://web3.okx.com/api/v5/dex/aggregator"

# Test wallet
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

def get_timestamp():
    """Get ISO format timestamp"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def sign_message(message, secret):
    """Create HMAC SHA256 signature"""
    mac = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')

def get_headers(method, request_path, body=''):
    """Generate OKX API headers with signature"""
    timestamp = get_timestamp()
    
    # Create signature string: timestamp + method + request_path + body
    if body:
        message = timestamp + method.upper() + request_path + body
    else:
        message = timestamp + method.upper() + request_path
    
    signature = sign_message(message, SECRET_KEY)
    passphrase_sig = sign_message(PASSPHRASE, SECRET_KEY)
    
    return {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': PASSPHRASE,
        'Content-Type': 'application/json'
    }

def test_get_tokens():
    """Test 1: Get supported tokens"""
    print("="*70)
    print("🧪 TEST 1: Get Supported Tokens")
    print("="*70)
    
    request_path = "/api/v5/dex/aggregator/all-tokens"
    url = f"https://web3.okx.com{request_path}"
    params = {"chainId": "501"}  # Solana
    
    # Add query string to request path for signature
    query_string = f"?chainId=501"
    headers = get_headers('GET', request_path + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "0":
                tokens = data.get("data", [])
                print(f"✅ SUCCESS! Found {len(tokens)} tokens")
                print(f"   Sample tokens:")
                for token in tokens[:3]:
                    print(f"   - {token.get('tokenSymbol')}: {token.get('tokenContractAddress', 'N/A')[:20]}...")
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_quote():
    """Test 2: Get swap quote"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Get Swap Quote (SOL → USDC)")
    print("="*70)
    
    request_path = "/api/v5/dex/aggregator/quote"
    url = f"https://web3.okx.com{request_path}"
    
    params = {
        "chainId": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01"
    }
    
    # Build query string for signature
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', request_path + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                quote_data = data.get("data", [{}])[0]
                print(f"✅ SUCCESS! Quote received")
                print(f"   From: SOL")
                print(f"   To: USDC")
                print(f"   Amount In: 0.01 SOL")
                print(f"   Amount Out: {quote_data.get('toTokenAmount', 'N/A')}")
                print(f"   Price Impact: {quote_data.get('priceImpact', 'N/A')}")
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                print(f"   Response: {json.dumps(data, indent=2)[:300]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_build_swap():
    """Test 3: Build swap transaction"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Build Swap Transaction")
    print("="*70)
    
    request_path = "/api/v5/dex/aggregator/swap"
    url = f"https://web3.okx.com{request_path}"
    
    params = {
        "chainId": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01",
        "userWalletAddress": WALLET,
        "gasLevel": "high"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', request_path + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                swap_data = data.get("data", [{}])[0]
                print(f"✅ SUCCESS! Swap transaction built")
                print(f"   Transaction data: {bool(swap_data.get('tx'))}")
                print(f"   Router: {swap_data.get('router', 'N/A')}")
                print(f"   Price impact: {swap_data.get('priceImpact', 'N/A')}")
                
                # Show transaction data structure
                tx_data = swap_data.get('tx', {})
                if tx_data:
                    print(f"   Transaction ready to sign!")
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_chains():
    """Test 4: Get supported chains"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Get Supported Chains")
    print("="*70)
    
    request_path = "/api/v5/dex/aggregator/supported-chains"
    url = f"https://web3.okx.com{request_path}"
    
    headers = get_headers('GET', request_path)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                chains = data.get("data", [])
                print(f"✅ SUCCESS! Found {len(chains)} supported chains")
                for chain in chains[:5]:
                    print(f"   - {chain.get('chainName')} (ID: {chain.get('chainId')})")
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 OKX DEX API TEST SUITE (With Full Auth)")
    print("="*70)
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Wallet: {WALLET[:10]}...{WALLET[-6:]}")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Get Tokens", test_get_tokens()))
    results.append(("Get Quote", test_get_quote()))
    results.append(("Build Swap", test_build_swap()))
    results.append(("Get Chains", test_get_chains()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! OKX DEX API is ready to use.")
        print("\n💡 Next step: Try selling MEMECARD using OKX DEX API")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
