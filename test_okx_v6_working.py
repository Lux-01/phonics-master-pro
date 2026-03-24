#!/usr/bin/env python3
"""
🚀 OKX DEX API V6 - Working Test
chainIndex=501 works!
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

def test_get_tokens():
    """Test 1: Get supported tokens"""
    print("="*70)
    print("🧪 TEST 1: Get Supported Tokens (V6)")
    print("="*70)
    
    url = "https://web3.okx.com/api/v6/dex/aggregator/all-tokens"
    params = {"chainIndex": "501"}
    
    query_string = "?chainIndex=501"
    headers = get_headers('GET', "/api/v6/dex/aggregator/all-tokens" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response structure: {list(data.keys())}")
            
            if data.get("code") == "0":
                # V6 returns data as a list
                tokens = data.get("data", [])
                if isinstance(tokens, list):
                    print(f"✅ SUCCESS! Found {len(tokens)} tokens")
                    print(f"   Sample:")
                    for token in tokens[:3]:
                        print(f"   - {token.get('tokenSymbol')}: {token.get('tokenContractAddress', 'N/A')[:20]}...")
                    return True
                else:
                    print(f"   Data type: {type(tokens)}")
                    print(f"   Data: {tokens}")
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
    
    url = "https://web3.okx.com/api/v6/dex/aggregator/quote"
    params = {
        "chainIndex": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/quote" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                quote_data = data.get("data", [])
                if isinstance(quote_data, list) and len(quote_data) > 0:
                    quote = quote_data[0]
                    print(f"✅ SUCCESS! Quote received")
                    print(f"   From: SOL")
                    print(f"   To: USDC")
                    print(f"   Amount In: 0.01 SOL")
                    print(f"   Amount Out: {quote.get('toTokenAmount', 'N/A')}")
                    print(f"   Price Impact: {quote.get('priceImpact', 'N/A')}")
                    return True
                else:
                    print(f"   Data: {quote_data}")
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

def test_build_swap():
    """Test 3: Build swap transaction"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Build Swap Transaction")
    print("="*70)
    
    url = "https://web3.okx.com/api/v6/dex/aggregator/swap"
    params = {
        "chainIndex": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",
        "slippage": "0.01",
        "userWalletAddress": WALLET,
        "gasLevel": "high"
    }
    
    query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    headers = get_headers('GET', "/api/v6/dex/aggregator/swap" + query_string)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                swap_data = data.get("data", [])
                if isinstance(swap_data, list) and len(swap_data) > 0:
                    swap = swap_data[0]
                    print(f"✅ SUCCESS! Swap transaction built")
                    print(f"   Transaction data: {bool(swap.get('tx'))}")
                    print(f"   Router: {swap.get('router', 'N/A')}")
                    print(f"   Price impact: {swap.get('priceImpact', 'N/A')}")
                    
                    # Show transaction data
                    tx_data = swap.get('tx', {})
                    if tx_data:
                        print(f"\n   📝 Transaction ready to sign!")
                        print(f"   Data: {json.dumps(tx_data, indent=2)[:300]}")
                    return True
                else:
                    print(f"   Data: {swap_data}")
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

def main():
    print("\n" + "="*70)
    print("🚀 OKX DEX API V6 TEST SUITE")
    print("="*70)
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Wallet: {WALLET[:10]}...{WALLET[-6:]}")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Get Tokens", test_get_tokens()))
    results.append(("Get Quote", test_get_quote()))
    results.append(("Build Swap", test_build_swap()))
    
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
        print("\n🎉 All tests passed! OKX DEX API V6 is ready to use.")
        print("\n💡 Next step: Try selling MEMECARD using OKX DEX API")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
