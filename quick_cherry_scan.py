#!/usr/bin/env python3
"""
Quick Cherry wallet scan - check for recent token buys
"""

import requests
import json
from collections import defaultdict

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_ENHANCED = f"https://api.helius.xyz/v0/addresses/?api-key={HELIUS_API_KEY}"

WALLETS = [
    "AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51",
    "8vUyFMnDfDrsz6c9UupPBVp6A5DLCg45Nuh1Zj39b8ft",
    "6ktp1QRtEbh788vcUi9mV3A4yPDabtS8h7hhjbZVwbeL",
    "5K6ZMakz47twGFJSzS1DP2S2RhGy39CHpFfbTUSzRKnR",
]

def get_token_accounts(wallet):
    """Get token accounts for wallet using RPC"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            accounts = data.get("result", {}).get("value", [])
            print(f"  Found {len(accounts)} token accounts")
            for acc in accounts:
                mint = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("mint")
                amt = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("tokenAmount", {}).get("uiAmount")
                if mint and amt and amt > 0:
                    print(f"    - {mint[:20]}...: {amt}")
            return accounts
    except Exception as e:
        print(f"  Error: {e}")
    return []

print("🔍 Quick scan of Cherry wallets (current holdings)")
print("=" * 60)

token_holders = defaultdict(list)

for i, wallet in enumerate(WALLETS, 1):
    print(f"\n[{i}] {wallet[:25]}...")
    accounts = get_token_accounts(wallet)
    
    for acc in accounts:
        mint = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("mint")
        if mint and mint != "So11111111111111111111111111111111111111112":  # Skip SOL
            token_holders[mint].append(wallet)

print("\n" + "=" * 60)
print("📊 TOKENS HELD BY MULTIPLE WALLETS:")
print("=" * 60)

found = False
for token, wallets in sorted(token_holders.items(), key=lambda x: len(x[1]), reverse=True):
    if len(wallets) >= 2:
        found = True
        print(f"\n🎯 {token}")
        print(f"   Held by {len(wallets)} wallets:")
        for w in wallets:
            print(f"     • {w[:30]}...")

if not found:
    print("\n❌ No tokens held by 2+ wallets in current snapshot")
    print("\nNote: This shows CURRENT holdings, not recent purchases.")
    print("To see historical buys, we'd need to scan transactions.")
