#!/usr/bin/env python3
"""
Cherry Wallet Coordinated Buy Tracker
Scans 14 wallets for tokens bought together in last 96 hours
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Helius API
HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_BASE = "https://mainnet.helius-rpc.com/"

# 14 Cherry wallets
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

def get_wallet_transactions(wallet, hours_back=96):
    """Get transactions for a wallet in last N hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    cutoff_signature = None  # Helius handles pagination
    
    transactions = []
    
    try:
        # Get signatures first
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet, {"limit": 100}]
        }
        
        response = requests.post(
            f"{HELIUS_BASE}?api-key={HELIUS_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            signatures = data.get("result", [])
            
            # Get transaction details for each signature
            for sig_info in signatures[:50]:  # Limit to 50 recent
                sig = sig_info.get("signature")
                block_time = sig_info.get("blockTime")
                
                # Check if within time window
                if block_time:
                    tx_time = datetime.fromtimestamp(block_time)
                    if tx_time < cutoff_time:
                        continue
                
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                }
                
                tx_response = requests.post(
                    f"{HELIUS_BASE}?api-key={HELIUS_API_KEY}",
                    headers=headers,
                    json=tx_payload,
                    timeout=30
                )
                
                if tx_response.status_code == 200:
                    tx_data = tx_response.json()
                    tx_result = tx_data.get("result")
                    if tx_result:
                        transactions.append({
                            "signature": sig,
                            "timestamp": tx_time if block_time else None,
                            "data": tx_result
                        })
                
                time.sleep(0.1)  # Rate limit
                
    except Exception as e:
        print(f"Error fetching transactions for {wallet[:8]}...: {e}")
    
    return transactions

def extract_token_buys(transactions):
    """Extract token purchases from transactions"""
    buys = []
    
    for tx in transactions:
        meta = tx["data"].get("meta", {})
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])
        
        # Look for token balance increases (buys)
        pre_map = {b["accountIndex"]: b for b in pre_balances}
        post_map = {b["accountIndex"]: b for b in post_balances}
        
        for idx, post in post_map.items():
            pre = pre_map.get(idx, {"uiTokenAmount": {"uiAmount": 0}})
            pre_amount = pre.get("uiTokenAmount", {}).get("uiAmount") or 0
            post_amount = post.get("uiTokenAmount", {}).get("uiAmount") or 0
            
            if post_amount > pre_amount:
                mint = post.get("mint")
                amount_bought = post_amount - pre_amount
                
                buys.append({
                    "token": mint,
                    "amount": amount_bought,
                    "timestamp": tx["timestamp"],
                    "signature": tx["signature"]
                })
    
    return buys

def scan_all_wallets():
    """Scan all wallets and find coordinated buys"""
    print("🔍 Scanning 14 Cherry wallets for coordinated buys...")
    print(f"⏰ Checking last 96 hours")
    print("=" * 60)
    
    all_buys = defaultdict(list)  # token -> list of {wallet, amount, timestamp, sig}
    
    for i, wallet in enumerate(WALLETS, 1):
        print(f"\n[{i}/14] Scanning {wallet[:20]}...")
        transactions = get_wallet_transactions(wallet)
        buys = extract_token_buys(transactions)
        
        for buy in buys:
            all_buys[buy["token"]].append({
                "wallet": wallet,
                "amount": buy["amount"],
                "timestamp": buy["timestamp"],
                "signature": buy["signature"]
            })
        
        print(f"   Found {len(buys)} token purchases")
        time.sleep(0.5)  # Rate limit between wallets
    
    # Find coordinated buys (2+ wallets buying same token)
    print("\n" + "=" * 60)
    print("📊 COORDINATED BUY ANALYSIS")
    print("=" * 60)
    
    coordinated = {}
    for token, buys in all_buys.items():
        unique_wallets = set(b["wallet"] for b in buys)
        if len(unique_wallets) >= 2:
            # Sort by timestamp
            buys.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min)
            coordinated[token] = buys
    
    if not coordinated:
        print("\n❌ No coordinated buys found in the last 96 hours")
        return
    
    # Sort by number of wallets coordinated
    sorted_tokens = sorted(coordinated.items(), 
                          key=lambda x: len(set(b["wallet"] for b in x[1])), 
                          reverse=True)
    
    print(f"\n✅ Found {len(sorted_tokens)} tokens with coordinated buys\n")
    
    for token, buys in sorted_tokens:
        unique_wallets = list(set(b["wallet"] for b in buys))
        wallet_count = len(unique_wallets)
        
        # Get time window
        timestamps = [b["timestamp"] for b in buys if b["timestamp"]]
        if timestamps:
            first_buy = min(timestamps)
            last_buy = max(timestamps)
            time_window = (last_buy - first_buy).total_seconds() / 3600  # hours
        else:
            time_window = "Unknown"
        
        print(f"\n🎯 TOKEN: {token}")
        print(f"   📈 Wallets coordinated: {wallet_count}")
        print(f"   ⏱️  Time window: {time_window:.1f} hours" if isinstance(time_window, float) else f"   ⏱️  Time window: {time_window}")
        print(f"   🛒 Total purchases: {len(buys)}")
        print("   👥 Wallets:")
        
        for wallet in unique_wallets[:5]:
            wallet_buys = [b for b in buys if b["wallet"] == wallet]
            total_amount = sum(b["amount"] for b in wallet_buys)
            print(f"      • {wallet[:20]}... ({len(wallet_buys)} buys, {total_amount:.4f} tokens)")
        
        if len(unique_wallets) > 5:
            print(f"      ... and {len(unique_wallets) - 5} more")
        
        # Show buy timeline
        print("   📅 Timeline:")
        for buy in buys[:5]:
            if buy["timestamp"]:
                time_str = buy["timestamp"].strftime("%m-%d %H:%M")
                print(f"      [{time_str}] {buy['wallet'][:15]}... +{buy['amount']:.4f}")
        
        print("-" * 60)
    
    # Summary
    print(f"\n📈 SUMMARY:")
    print(f"   • Total tokens with coordination: {len(sorted_tokens)}")
    print(f"   • Max wallets coordinated on single token: {max(len(set(b['wallet'] for b in buys)) for _, buys in sorted_tokens)}")
    
    return sorted_tokens

if __name__ == "__main__":
    results = scan_all_wallets()
    
    # Save results
    output = {
        "scan_time": datetime.now().isoformat(),
        "wallets_scanned": len(WALLETS),
        "hours_back": 96,
        "coordinated_buys": []
    }
    
    if results:
        for token, buys in results:
            output["coordinated_buys"].append({
                "token": token,
                "wallet_count": len(set(b["wallet"] for b in buys)),
                "total_buys": len(buys),
                "wallets": list(set(b["wallet"] for b in buys)),
                "buys": [{"wallet": b["wallet"], "amount": b["amount"], 
                         "timestamp": b["timestamp"].isoformat() if b["timestamp"] else None,
                         "signature": b["signature"]} for b in buys]
            })
    
    with open("cherry_coordination_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to cherry_coordination_results.json")
