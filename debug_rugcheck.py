#!/usr/bin/env python3
"""Debug the quick_rug_check function"""

import requests
import json
import time
import random

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def quick_rug_check_debug(token_ca: str, token_name: str = "Unknown", token_decimals: int = 5) -> tuple:
    """
    Debug version with full tracing
    """
    print(f"\n{'='*60}")
    print(f"🔍 RUG CHECK: {token_name}")
    print(f"   CA: {token_ca}")
    print(f"   Decimals: {token_decimals}")
    print('='*60)
    
    try:
        print(f"\n1. Calling getTokenLargestAccounts...")
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
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ API_ERROR: status {response.status_code}")
            return "API_ERROR", 0
        
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
        
        if "error" in data:
            print(f"   ❌ RPC_ERROR: {data['error']}")
            return "RPC_ERROR", 0
        
        result = data.get("result", {})
        print(f"   Result keys: {list(result.keys())}")
        
        holders = result.get("value", [])
        print(f"   Holders found: {len(holders)}")
        
        if len(holders) == 0:
            print(f"   ❌ Found 0 holders - checking full response:")
            print(f"   {json.dumps(data, indent=2)[:500]}")
            return "NO_HOLDERS", 0
        
        if len(holders) < 10:
            print(f"   ❌ TOO_FEW_HOLDERS: {len(holders)} < 10")
            return "TOO_FEW_HOLDERS", 0
        
        print(f"\n2. Getting token supply...")
        supply_resp = requests.post(
            HELIUS_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenSupply",
                "params": [token_ca]
            },
            timeout=5
        )
        
        total_supply = 1e9  # Default fallback
        if supply_resp.status_code == 200:
            supply_data = supply_resp.json()
            print(f"   Supply response received")
            if "result" in supply_data and "value" in supply_data["result"]:
                supply_info = supply_data["result"]["value"]
                total_supply_raw = supply_info.get("amount", 1e9)
                decimals = supply_info.get("decimals", token_decimals)
                total_supply = int(total_supply_raw) / (10 ** decimals)
                print(f"   Total supply: {total_supply:,.0f} tokens (decimals: {decimals})")
        else:
            print(f"   ⚠️ Supply fetch failed: {supply_resp.status_code}")
        
        # Select 5 wallets
        check_indices = [0, 1, 2, 3]  # First 4
        if len(holders) > 5:
            random_idx = random.randint(4, min(14, len(holders)-1))
            check_indices.append(random_idx)
        
        print(f"\n3. Checking {len(check_indices)} wallets at indices: {check_indices}")
        dust_count = 0
        
        for i, idx in enumerate(check_indices):
            if idx >= len(holders):
                print(f"   Skipping index {idx} (out of range)")
                continue
            
            holder = holders[idx]
            address = holder.get("address", "N/A")
            amount_raw = int(holder.get("amount", 0))
            
            print(f"\n   Wallet {idx}:")
            print(f"      Address: {address}")
            print(f"      Raw amount: {amount_raw}")
            
            # Convert to actual token amount
            amount = amount_raw / (10 ** token_decimals)
            print(f"      Actual amount: {amount:,.0f} tokens")
            
            # Calculate percentage
            pct_supply = (amount_raw / int(supply_data.get("result", {}).get("value", {}).get("amount", amount_raw))) * 100
            print(f"      % of supply: {pct_supply:.4f}%")
            
            is_dust = pct_supply < 0.1
            status = "⚠️ DUST" if is_dust else "✅ OK"
            print(f"      {status}")
            
            if is_dust:
                dust_count += 1
        
        print(f"\n4. FINAL SCORING:")
        print(f"   Dust wallets: {dust_count}/{len(check_indices)}")
        
        if dust_count >= 4:
            print(f"   🚫 RUG (-10 pts)")
            return "RUG", -10
        elif dust_count == 3:
            print(f"   ⚠️ WARNING (-5 pts)")
            return "WARNING", -5
        else:
            print(f"   ✅ PASS (0 pts)")
            return "PASS", 0
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR", 0


# Test on BONK
BONK_CA = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
result = quick_rug_check_debug(BONK_CA, "BONK", token_decimals=5)
print(f"\n{'='*60}")
print(f"FINAL RESULT: {result}")
print('='*60)
