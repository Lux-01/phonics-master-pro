#!/usr/bin/env python3
"""
Full Cherry wallet scan - all 14 wallets
"""

import requests
from collections import defaultdict

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"

WALLETS = [
    "AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51",
    "8vUyFMnDfDrsz6c9UupPBVp6A5DLCg45Nuh1Zj39b8ft",
    "6ktp1QRtEbh788vcUi9mV3A4yPDabtS8h7hhjbZVwbeL",
    "5K6ZMakz47twGFJSzS1DP2S2RhGy39CHpFfbTUSzRKnR",
    "2NuAgVk3hcb7s4YvP4GjV5fD8eDvZQv5wuN6ZC8igRfV",
    "4o8b8jgJNDEQPgEuZeq4j2ohopW4GdvDHySTidooWCRg",
    "2JmEcVhRv6e63ucRngTGUNNsWTPb8hXMsQJyM1wwDies",
    "2tgUbS9UMoQD6GkDZBiqKYCURnGrSb6ocYwRABrSJUvY",
    "HJHpNNXksc49uX7oJu8LgjJPa4RViuraN5LP6hsXuGjm",
    "5aLY85pyxiuX3fd4RgM3Yc1e3MAL6b7UgaZz6MS3JUfG",
    "5QG4pUeX47BX1RvhJCwjHaLrfW2iE45PAeFALcJenATW",
    "3wjyaSegfV7SZzjv9Ut1p6AcY5ZdoZjmu6i6QPCVvnmz",
    "2PYURJrSX1GBFrcHiUnkxaCxqCHcen7DeKm6prD392ZD",
    "HzGCMK4tioGPYJAwNsPSYJ3CTMXiaBXQyNhdmfsVsmVe"
]

# Common tokens to filter out
COMMON_TOKENS = {
    "So11111111111111111111111111111111111111112",  # Wrapped SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", # USDC
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", # Jupiter
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", # Bonk
    "BTCKrB2BHXUs3uQPJWSVjeHoxAfmq8G4jzZXo9XaGzT7", # BTC
    "DezXAZ8z7PnrnRJjz3wXBoRGixWy6W7B7vtHJ4oFpnj3", # BONK
}

def get_token_accounts(wallet):
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
            return data.get("result", {}).get("value", [])
    except Exception as e:
        print(f"  Error: {e}")
    return []

print("🔍 Full scan of 14 Cherry wallets")
print("=" * 70)

token_holders = defaultdict(list)

for i, wallet in enumerate(WALLETS, 1):
    print(f"[{i:2d}/14] {wallet[:25]}...", end=" ")
    accounts = get_token_accounts(wallet)
    print(f"({len(accounts)} tokens)")
    
    for acc in accounts:
        parsed = acc.get("account", {}).get("data", {}).get("parsed", {})
        info = parsed.get("info", {})
        mint = info.get("mint")
        amt = info.get("tokenAmount", {}).get("uiAmount") or 0
        
        if mint and mint not in COMMON_TOKENS and amt > 0:
            token_holders[mint].append({
                "wallet": wallet,
                "amount": amt
            })

print("\n" + "=" * 70)
print("📊 TOKENS HELD BY 3+ WALLETS:")
print("=" * 70)

found_multis = []
for token, holders in sorted(token_holders.items(), key=lambda x: len(x[1]), reverse=True):
    if len(holders) >= 3:
        found_multis.append((token, holders))
        
if not found_multis:
    print("❌ No tokens held by 3+ wallets")

print("\n" + "=" * 70)
print("📊 TOKENS HELD BY 2 WALLETS:")
print("=" * 70)

found_pairs = []
for token, holders in sorted(token_holders.items(), key=lambda x: len(x[1]), reverse=True):
    if len(holders) == 2:
        found_pairs.append((token, holders))
        
if not found_pairs:
    print("❌ No tokens held by exactly 2 wallets")

print(f"\n✅ Scan complete. Analyzed {len(WALLETS)} wallets.")
