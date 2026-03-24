#!/usr/bin/env python3
"""
🎯 PUMP GROUP WALLET TRACKER
Monitors 6 wallets that coordinated on Cherry token
Alerts when they buy the same new token (early pump signal)
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

# The 6 wallets from Cherry pump analysis
WATCH_WALLETS = [
    "8L2y55D11k63CAftvW7uMM2mBhtMxLoLnivG9uY2bt8j",  # Highest activity (6 buys)
    "2tgUbS9UMoQD6GkDZBiqKYCURnGrSb6ocYwRABrSJUvY",  # Biggest volume
    "2UGzWzvmdNcawaxTTrhKmHMQutqUguGaszD8QJ1AAYCA",
    "23nGMrCLfyizKFjmwG8c67LFYs8ZpehVs1Swr4srTpYk",  # FOMO buyer
    "7t9kYGrqtrSbGoQ6sfhfUS2UX4wYgekKek1AKPmEnS4p",
    "5eeL1LaKApBv6wJuHkZpsTLiWJAKgGjQadj4qTsfAahC"
]

BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"
HEADERS = {"X-API-KEY": BIRDEYE_KEY, "accept": "application/json"}

# Store recent buys to detect coordination
recent_buys = defaultdict(list)  # token -> [(wallet, timestamp, amount)]
ALERT_THRESHOLD = 2  # Alert when 2+ wallets buy same token within 1 hour
CHECK_INTERVAL = 30  # Minutes between checks

def check_wallet_activity(wallet, since_hours=24):
    """Check a single wallet for recent Solana token purchases"""
    buys = []
    
    try:
        # Birdeye user transactions endpoint
        url = f"https://public-api.birdeye.so/defi/txs/user"
        params = {
            "address": wallet,
            "limit": 20,
            "offset": 0
        }
        
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        
        if r.status_code == 429:
            print(f"⚠️ Rate limited on wallet {wallet[:16]}...")
            return buys
        
        if r.status_code != 200:
            return buys
        
        data = r.json()
        if not isinstance(data, dict):
            return buys
        
        txs = data.get("data", {}).get("items", [])
        since_time = datetime.now() - timedelta(hours=since_hours)
        
        for tx in txs:
            tx_time_str = tx.get("timestamp", "")
            try:
                tx_time = datetime.fromisoformat(tx_time_str.replace("Z", "+00:00"))
                if tx_time < since_time:
                    continue
                    
                # Check if it's a buy (token in, SOL out)
                token_changes = tx.get("tokenChanges", [])
                
                for change in token_changes:
                    if change.get("direction") == "in" and change.get("tokenType") == "token":
                        token_ca = change.get("address", "")
                        amount = float(change.get("value", 0))
                        symbol = change.get("symbol", "Unknown")
                        
                        # Skip common tokens
                        if symbol in ["SOL", "WSOL", "USDC", "USDT"]:
                            continue
                        
                        buys.append({
                            "token_ca": token_ca,
                            "symbol": symbol,
                            "amount": amount,
                            "timestamp": tx_time.isoformat(),
                            "wallet": wallet
                        })
                        
            except:
                continue
                
    except Exception as e:
        print(f"Error checking {wallet[:16]}: {e}")
    
    return buys

def check_coordination():
    """Check for coordination - multiple wallets buying same token"""
    print(f"\n{'='*70}")
    print(f"🎯 PUMP GROUP WALLET TRACKER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")
    print(f"\nMonitoring {len(WATCH_WALLETS)} wallets...")
    print(f"Alert threshold: {ALERT_THRESHOLD}+ wallets buying same token within 1 hour")
    print()
    
    all_buys = []
    
    # Check each wallet
    for i, wallet in enumerate(WATCH_WALLETS, 1):
        print(f"[{i}/{len(WATCH_WALLETS)}] Checking {wallet[:20]}...")
        buys = check_wallet_activity(wallet, since_hours=2)
        all_buys.extend(buys)
        
        if buys:
            print(f"  ✅ Found {len(buys)} recent buys")
            for buy in buys[:3]:  # Show first 3
                print(f"    - {buy['symbol']}: {buy['amount']:,.0f} tokens")
        
        # Rate limiting
        if i < len(WATCH_WALLETS):
            time.sleep(3)
    
    # Check for coordination
    print()
    print("-" * 70)
    print("🔍 ANALYZING COORDINATION PATTERNS...")
    print("-" * 70)
    
    # Group by token
    token_buys = defaultdict(list)
    for buy in all_buys:
        token_buys[buy["token_ca"]].append(buy)
    
    alerts = []
    
    for token_ca, buys in token_buys.items():
        # Check if multiple wallets bought this token
        unique_wallets = set(b["wallet"] for b in buys)
        
        if len(unique_wallets) >= ALERT_THRESHOLD:
            # Check time window (within 1 hour)
            timestamps = sorted([datetime.fromisoformat(b["timestamp"]) for b in buys])
            if timestamps:
                min_time = timestamps[0]
                max_time = timestamps[-1]
                
                if (max_time - min_time) <= timedelta(hours=1):
                    # Coordination detected!
                    symbol = buys[0]["symbol"]
                    total_amount = sum(b["amount"] for b in buys)
                    
                    alert = {
                        "token_ca": token_ca,
                        "symbol": symbol,
                        "wallets": list(unique_wallets),
                        "wallet_count": len(unique_wallets),
                        "buy_count": len(buys),
                        "total_tokens": total_amount,
                        "time_window": f"{min_time.strftime('%H:%M')} - {max_time.strftime('%H:%M')}"
                    }
                    alerts.append(alert)
    
    # Print alerts
    print()
    if alerts:
        print("=" * 70)
        print("🚨🚨🚨 COORDINATED PUMP DETECTED! 🚨🚨🚨")
        print("=" * 70)
        
        for alert in sorted(alerts, key=lambda x: x["wallet_count"], reverse=True):
            print()
            print(f"🔥 TOKEN: {alert['symbol']}")
            print(f"   CA: {alert['token_ca']}")
            print(f"   Wallets: {alert['wallet_count']} (of 6 monitored)")
            print(f"   Total buys: {alert['buy_count']}")
            print(f"   Time window: {alert['time_window']}")
            print(f"   Total tokens: {alert['total_tokens']:,.0f}")
            print()
            print("   Buying wallets:")
            for w in alert['wallets']:
                print(f"   - {w}")
            print()
            print("   ⚡ ACTION: Consider entering position early!")
            print("-" * 70)
    else:
        print("✅ No coordination detected in last 2 hours")
        print("   All wallets appear to be inactive or buying different tokens")
    
    print()
    print(f"Next check in {CHECK_INTERVAL} minutes...")
    print()
    
    return alerts

def get_wallet_summary(wallet):
    """Get wallet age and total transaction count"""
    try:
        url = f"https://public-api.birdeye.so/defi/txs/user"
        params = {"address": wallet, "limit": 1}
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            txs = data.get("data", {}).get("items", [])
            if txs:
                # Get oldest tx
                oldest_str = txs[-1].get("timestamp", "")
                return {"has_activity": True, "oldest_tx": oldest_str}
        
        return {"has_activity": False}
    except:
        return {"has_activity": False}

def check_wallets_are_new():
    """Check if these wallets are new or established"""
    print()
    print("=" * 70)
    print("🔍 WALLET ANALYSIS: Are these new wallets?")
    print("=" * 70)
    print()
    
    for wallet in WATCH_WALLETS:
        summary = get_wallet_summary(wallet)
        status = "Has activity" if summary["has_activity"] else "Unknown"
        print(f"{wallet[:25]}... Status: {status}")
        if summary.get("oldest_tx"):
            print(f"  Oldest tx: {summary['oldest_tx']}")
    
    print()
    print("Note: These wallets show coordinated buying patterns.")
    print("They could be:")
    print("  1. A pump group with multiple members")
    print("  2. One person using multiple wallets")
    print("  3. Discord/telegram group coordinating buys")
    print()

if __name__ == "__main__":
    print("🚀 PUMP GROUP WALLET TRACKER")
    print("=" * 70)
    
    # Check wallet ages first
    check_wallets_are_new()
    
    # Main loop
    while True:
        try:
            check_coordination()
            print(f"\n💤 Sleeping for {CHECK_INTERVAL} minutes...")
            time.sleep(CHECK_INTERVAL * 60)
        except KeyboardInterrupt:
            print("\n\n👋 Tracker stopped by user")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            print(f"Retrying in {CHECK_INTERVAL} minutes...")
            time.sleep(CHECK_INTERVAL * 60)
