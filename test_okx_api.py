#!/usr/bin/env python3
"""
🚀 OKX DEX API Test Script
Tests the API key and swap functionality
"""

import requests
import json
import time

# API Configuration
API_KEY = "911fb148-e0fe-41b5-bab5-6f9a1a902137"
BASE_URL = "https://web3.okx.com/api/v5/dex/aggregator"

# Test wallet (your wallet)
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

def test_get_tokens():
    """Test 1: Get supported tokens"""
    print("="*70)
    print("🧪 TEST 1: Get Supported Tokens")
    print("="*70)
    
    url = f"{BASE_URL}/all-tokens"
    params = {"chainId": "501"}  # Solana
    headers = {"OK-ACCESS-KEY": API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
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
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_get_quote():
    """Test 2: Get swap quote"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Get Swap Quote (SOL → USDC)")
    print("="*70)
    
    url = f"{BASE_URL}/quote"
    
    # SOL -> USDC quote (small amount for testing)
    params = {
        "chainId": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",  # SOL
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "amount": "10000000",  # 0.01 SOL in lamports
        "slippage": "0.01",  # 1%
        "userWalletAddress": WALLET
    }
    
    headers = {"OK-ACCESS-KEY": API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"   Request URL: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            
            if data.get("code") == "0":
                quote_data = data.get("data", [{}])[0]
                print(f"\n✅ SUCCESS! Quote received")
                print(f"   From: {quote_data.get('fromToken', {}).get('tokenSymbol', 'SOL')}")
                print(f"   To: {quote_data.get('toToken', {}).get('tokenSymbol', 'USDC')}")
                print(f"   Amount Out: {quote_data.get('toTokenAmount', 'N/A')}")
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

def test_build_swap():
    """Test 3: Build swap transaction"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Build Swap Transaction")
    print("="*70)
    
    url = f"{BASE_URL}/swap"
    
    # Build swap transaction
    params = {
        "chainId": "501",
        "fromTokenAddress": "So11111111111111111111111111111111111111112",
        "toTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "10000000",  # 0.01 SOL
        "slippage": "0.01",
        "userWalletAddress": WALLET,
        "gasLevel": "high"  # Fast execution
    }
    
    headers = {"OK-ACCESS-KEY": API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                swap_data = data.get("data", [{}])[0]
                print(f"\n✅ SUCCESS! Swap transaction built")
                print(f"   Transaction data available: {bool(swap_data.get('tx'))}")
                print(f"   Router: {swap_data.get('router', 'N/A')}")
                print(f"   Price impact: {swap_data.get('priceImpact', 'N/A')}")
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                print(f"   Full response: {json.dumps(data, indent=2)}")
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

def test_get_solana_tokens():
    """Test 4: Get specific Solana tokens"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Check Solana Token Support")
    print("="*70)
    
    url = f"{BASE_URL}/all-tokens"
    params = {"chainId": "501"}
    headers = {"OK-ACCESS-KEY": API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == "0":
                tokens = data.get("data", [])
                
                # Check for specific tokens
                target_tokens = [
                    "So11111111111111111111111111111111111111112",  # SOL
                    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                    "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ"   # MEMECARD
                ]
                
                found = []
                for token in tokens:
                    if token.get("tokenContractAddress") in target_tokens:
                        found.append(token)
                
                print(f"✅ Found {len(found)} target tokens:")
                for t in found:
                    print(f"   - {t.get('tokenSymbol')}: {t.get('tokenContractAddress', 'N/A')[:20]}...")
                
                if len(found) < len(target_tokens):
                    missing = [t for t in target_tokens if t not in [f.get("tokenContractAddress") for f in found]]
                    print(f"\n⚠️ Missing tokens (may still work via contract address):")
                    for m in missing:
                        print(f"   - {m[:20]}...")
                
                return True
            else:
                print(f"❌ API Error: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 OKX DEX API TEST SUITE")
    print("="*70)
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Wallet: {WALLET[:10]}...{WALLET[-6:]}")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Get Tokens", test_get_tokens()))
    results.append(("Get Quote", test_get_quote()))
    results.append(("Build Swap", test_build_swap()))
    results.append(("Solana Tokens", test_get_solana_tokens()))
    
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
    else:
        print("\n⚠️ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
