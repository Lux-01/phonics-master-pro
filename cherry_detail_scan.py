#!/usr/bin/env python3
"""
Full Cherry wallet scan - show all overlaps
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

KNOWN_TOKENS = {
    "So11111111111111111111111111111111111111112": "SOL (Wrapped)",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "Jupiter (JUP)",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "BONK (Old)",
    "DezXAZ8z7PnrnRJjz3wXBoRGixWy6W7B7vtHJ4oFpnj3": "BONK",
    "BTCKrB2BHXUs3uQPJWSVjeHoxAfmq8G4jzZXo9XaGzT7": "Bitcoin (Solana)",
    "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB": "USD Coin",
    "7vfCXTUXx5WJV5JADk17sUMHrKx8uVb4gFH2j2tB3p7": "$WIF",
    "5oVNBeEEQvY1e1ErTqV3rpjP8Wj1vHYPJ1g9Dq7N6M": "BOME",
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

def get_token_info(mint):
    """Get token metadata from Helius"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAsset",
        "params": [mint]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", {})
            return {
                "name": result.get("content", {}).get("metadata", {}).get("name", "Unknown"),
                "symbol": result.get("content", {}).get("metadata", {}).get("symbol", "???"),
                "image": result.get("content", {}).get("files", [{}])[0].get("uri", "")
            }
    except:
        pass
    return None

print("🔍 Analyzing token overlaps across 14 Cherry wallets")
print("=" * 70)

token_holders = defaultdict(list)

for i, wallet in enumerate(WALLETS, 1):
    print(f"[{i:2d}/14] Checking {wallet[:30]}...")
    accounts = get_token_accounts(wallet)
    
    for acc in accounts:
        parsed = acc.get("account", {}).get("data", {}).get("parsed", {})
        info = parsed.get("info", {})
        mint = info.get("mint")
        amt = info.get("tokenAmount", {}).get("uiAmount") or 0
        
        if mint and amt > 0.001:  # Ignore dust
            token_holders[mint].append({
                "wallet_index": i,
                "wallet": wallet,
                "amount": amt
            })

print("\n" + "=" * 70)
print("📊 COORDINATED TOKEN HOLDINGS (2+ wallets)")
print("=" * 70)

coordinated = [(t, h) for t, h in token_holders.items() if len(h) >= 2]
coordinated.sort(key=lambda x: len(x[1]), reverse=True)

if not coordinated:
    print("❌ No overlapping token holdings found")
else:
    for mint, holders in coordinated:
        count = len(holders)
        name = KNOWN_TOKENS.get(mint, "Unknown Token")
        total_amt = sum(h["amount"] for h in holders)
        
        print(f"\n🎯 {name}")
        print(f"   Mint: {mint}")
        print(f"   Held by {count} wallets | Total: {total_amt:,.4f}")
        print("   Wallets:")
        for h in holders[:5]:
            print(f"     • Wallet #{h['wallet_index']}: {h['amount']:,.4f}")
        if len(holders) > 5:
            print(f"     ... and {len(holders)-5} more")

print(f"\n✅ Found {len(coordinated)} tokens with coordinated holdings")
