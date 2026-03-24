#!/usr/bin/env python3
"""
Find Profitable Whale Wallets to Track
Analyzes recent successful trades to find wallets worth copying
"""

import json
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "6335463fca7340f9a2c73eacd5a37f64")

def get_trending_tokens() -> List[Dict]:
    """Get currently trending tokens on Solana"""
    try:
        url = "https://public-api.birdeye.so/v1/trending"
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("tokens", [])
    except Exception as e:
        print(f"Error fetching trending: {e}")
    return []

def get_token_holders(token_address: str) -> List[Dict]:
    """Get top holders of a token"""
    try:
        url = f"https://public-api.birdeye.so/v1/token/holders"
        params = {"address": token_address, "limit": 20}
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("items", [])
    except Exception as e:
        print(f"Error fetching holders: {e}")
    return []

def get_wallet_transactions(wallet: str, days: int = 7) -> List[Dict]:
    """Get recent transactions for a wallet"""
    try:
        url = "https://public-api.birdeye.so/v1/wallet/tx_list"
        params = {
            "wallet": wallet,
            "limit": 50,
            "sort_by": "blockTime",
            "sort_order": "desc"
        }
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("txs", [])
    except Exception as e:
        print(f"Error fetching transactions: {e}")
    return []

def analyze_wallet_performance(wallet: str) -> Dict:
    """Analyze wallet's recent trading performance"""
    txs = get_wallet_transactions(wallet, days=7)
    
    if not txs:
        return None
    
    buys = 0
    sells = 0
    total_volume = 0
    tokens_traded = set()
    
    for tx in txs:
        token = tx.get("tokenAddress", "")
        if not token:
            continue
        
        tokens_traded.add(token)
        
        # Determine if buy or sell
        if tx.get("to") == wallet:
            buys += 1
        else:
            sells += 1
        
        total_volume += float(tx.get("solAmount", 0))
    
    return {
        "wallet": wallet,
        "buys": buys,
        "sells": sells,
        "total_volume": total_volume,
        "unique_tokens": len(tokens_traded),
        "activity_score": (buys + sells) * total_volume
    }

def find_profitable_wallets():
    """Find wallets that have been trading successfully"""
    print("🔍 Finding profitable whale wallets...\n")
    
    # Get trending tokens
    print("Fetching trending tokens...")
    trending = get_trending_tokens()
    
    if not trending:
        print("❌ Could not fetch trending tokens")
        return
    
    print(f"Found {len(trending)} trending tokens\n")
    
    # Collect unique wallets from top holders
    potential_whales = {}
    
    for token in trending[:5]:  # Check top 5 trending
        symbol = token.get("symbol", "UNKNOWN")
        address = token.get("address", "")
        
        if not address:
            continue
        
        print(f"Analyzing {symbol} holders...")
        holders = get_token_holders(address)
        
        for holder in holders:
            wallet = holder.get("owner", "")
            amount = float(holder.get("amount", 0))
            
            if wallet and amount > 1000000:  # > 1M tokens
                if wallet not in potential_whales:
                    potential_whales[wallet] = {
                        "tokens": [],
                        "total_value": 0
                    }
                potential_whales[wallet]["tokens"].append(symbol)
                potential_whales[wallet]["total_value"] += amount
    
    print(f"\nFound {len(potential_whales)} potential whales\n")
    
    # Analyze each potential whale
    results = []
    for wallet, data in list(potential_whales.items())[:10]:
        print(f"Analyzing {wallet[:20]}...")
        perf = analyze_wallet_performance(wallet)
        if perf:
            perf["tokens_held"] = data["tokens"]
            results.append(perf)
    
    # Sort by activity score
    results.sort(key=lambda x: x["activity_score"], reverse=True)
    
    print("\n" + "="*70)
    print("🐳 TOP WHALE CANDIDATES")
    print("="*70)
    
    for i, whale in enumerate(results[:5], 1):
        print(f"\n{i}. Wallet: {whale['wallet']}")
        print(f"   Buys: {whale['buys']} | Sells: {whale['sells']}")
        print(f"   Volume: {whale['total_volume']:.2f} SOL")
        print(f"   Unique tokens: {whale['unique_tokens']}")
        print(f"   Activity score: {whale['activity_score']:.2f}")
        print(f"   Tokens held: {', '.join(whale['tokens_held'][:3])}")
        print(f"\n   To add: python3 run_tracker_v2.py add-wallet {whale['wallet']} \"Whale_{i}\" 1.0")
    
    print("\n" + "="*70)
    print("\n💡 Tips for selecting whales:")
    print("   • Look for high buy/sell ratio (more buys = accumulation)")
    print("   • Check unique tokens (diversified = experienced)")
    print("   • Verify on DeBank: https://debank.com/profile/<wallet>")
    print("   • Look for early entry patterns (buys before pumps)")

if __name__ == "__main__":
    find_profitable_wallets()
