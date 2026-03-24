#!/usr/bin/env python3
"""
🔍 WALLET COORDINATION TRACKER
Tracks if the 14 Cherry pump wallets bought other tokens together
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
from time import sleep

# The 14 wallets from Cherry analysis
CHERRY_WALLETS = [
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

# Plus the original 6 Cherry pump wallets
ORIGINAL_CHERRY_WALLETS = [
    "8L2y55D11k63CAftvW7uMM2mBhtMxLoLnivG9uY2bt8j",
    "2tgUbS9UMoQD6GkDZBiqKYCURnGrSb6ocYwRABrSJUvY",
    "2UGzWzvmdNcawaxTTrhKmHMQutqUguGaszD8QJ1AAYCA",
    "23nGMrCLfyizKFjmwG8c67LFYs8ZpehVs1Swr4srTpYk",
    "7t9kYGrqtrSbGoQ6sfhfUS2UX4wYgekKek1AKPmEnS4p",
    "5eeL1LaKApBv6wJuHkKpsTLiWJAKgGjQadj4qTsfAahC"
]

ALL_WALLETS = list(set(CHERRY_WALLETS + ORIGINAL_CHERRY_WALLETS))  # Remove duplicates

HEADERS = {
    'X-API-KEY': '6335463fca7340f9a2c73eacd5a37f64',
    'accept': 'application/json'
}

def main():
    print("=" * 80)
    print("🦞 CHERRY PUMP GROUP - COORDINATION AUDIT")
    print("=" * 80)
    print()
    print(f"Tracking {len(ALL_WALLETS)} total wallets:")
    print(f"  • 14 wallets from March 2 analysis")
    print(f"  • 6 original Cherry pump wallets")
    print(f"  • Total unique: {len(ALL_WALLETS)} (2 overlap)")
    print()
    
    # Check first wallet to see format
    url = f'https://public-api.birdeye.so/defi/txs/token?address={ALL_WALLETS[0]}&limit=10'
    print(f"Testing with wallet: {ALL_WALLETS[0][:35]}...")
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            items = data.get('data', {}).get('items', [])
            print(f"Recent transactions: {len(items)}")
            
            if items:
                print("\nRecent buys:")
                for tx in items[:5]:
                    if tx.get('side') == 'buy':
                        symbol = tx.get('base', {}).get('symbol', 'UNKNOWN')
                        ca = tx.get('base', {}).get('address', '')
                        sol = tx.get('quote', {}).get('uiAmount', 0)
                        print(f"  {symbol} ({ca[:20]}...): {sol:.4f} SOL")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
