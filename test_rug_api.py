#!/usr/bin/env python3
"""Standalone test for rug check API"""

import requests
import json
import time
import random

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Test with BONK
token_ca = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

print(f"Testing Rug Check on BONK ({token_ca[:20]}...)")
print(f"HELIUS_URL: {HELIUS_URL}")
print("-" * 60)

# Get holders list
print("\n1. Getting token largest accounts...")
response = requests.post(
    HELIUS_URL,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenLargestAccounts",
        "params": [token_ca]
    },
    timeout=30
)

print(f"Response status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print(f"\nParsed data: {json.dumps(data, indent=2)[:1000]}")
    
    if "result" in data and "value" in data["result"]:
        holders = data["result"]["value"]
        print(f"\nFound {len(holders)} holders")
        
        if len(holders) >= 10:
            # Check 5 wallets
            check_indices = [0, 1, 2, 3]
            if len(holders) > 5:
                random_idx = random.randint(4, min(14, len(holders)-1))
                check_indices.append(random_idx)
            
            print(f"\nChecking {len(check_indices)} wallets at indices: {check_indices}")
            dust_count = 0
            
            for idx in check_indices:
                if idx >= len(holders):
                    continue
                
                wallet = holders[idx]["address"]
                amount = holders[idx].get("amount", "0")
                ui_amount = holders[idx].get("uiAmountString", "0")
                
                print(f"\n  Wallet {idx}: {wallet}")
                print(f"    Token amount: {ui_amount}")
                
                # Get SOL balance
                time.sleep(0.5)  # Rate limit protection
                balance_resp = requests.post(
                    HELIUS_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [wallet]
                    },
                    timeout=15
                )
                
                if balance_resp.status_code == 200:
                    balance_data = balance_resp.json()
                    sol_balance = balance_data.get("result", {}).get("value", 0) / 1e9
                    is_dust = sol_balance < 0.01
                    
                    status = "⚠️ DUST" if is_dust else "✅ OK"
                    print(f"    SOL balance: {sol_balance:.4f} {status}")
                    
                    if is_dust:
                        dust_count += 1
                else:
                    print(f"    Balance check failed: {balance_resp.status_code}")
            
            print(f"\n" + "-" * 60)
            print(f"FINAL RESULT: {dust_count}/5 wallets are dust")
            
            if dust_count >= 4:
                print("Status: 🚫 RUG DETECTED!")
            elif dust_count == 3:
                print("Status: ⚠️ WARNING")
            else:
                print("Status: ✅ PASS")
        else:
            print(f"Too few holders: {len(holders)} < 10")
    else:
        print(f"No 'result' in response: {data.keys()}")
else:
    print(f"API Error: {response.status_code}")
