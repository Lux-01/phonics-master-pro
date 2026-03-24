#!/usr/bin/env python3
"""
Find Profitable Whale Wallets using Helius API
Searches for wallets with successful trading patterns
"""

import requests
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce")
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Known profitable wallet patterns (these are examples - replace with real ones)
KNOWN_WHALE_PATTERNS = [
    # Format: (name, description, typical_behavior)
    ("Early Adopter", "Buys within first hour of launch", "high_risk_high_reward"),
    ("Swing Trader", "Holds 1-7 days, takes 20-50% profits", "consistent_gains"),
    ("Diamond Hands", "Holds through dips, sells at 2x+", "high_conviction"),
    ("Snipe Bot", "Multiple small buys in seconds", "automated"),
]

def get_recent_token_launches(hours: int = 24) -> List[Dict]:
    """Get recently launched tokens with significant volume"""
    try:
        # Use Helius to get recent token activity
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": "helius-test",
            "method": "getSignaturesForAddress",
            "params": [
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
                {"limit": 100}
            ]
        }
        
        resp = requests.post(HELIUS_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            signatures = data.get("result", [])
            
            # Parse for new token creations
            tokens = []
            for sig in signatures[:20]:
                tx_info = get_transaction_details(sig.get("signature", ""))
                if tx_info:
                    tokens.append(tx_info)
            
            return tokens
    except Exception as e:
        print(f"Error fetching launches: {e}")
    
    return []

def get_transaction_details(signature: str) -> Optional[Dict]:
    """Get detailed transaction info"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": "helius-test",
            "method": "getTransaction",
            "params": [
                signature,
                {"encoding": "json", "maxSupportedTransactionVersion": 0}
            ]
        }
        
        resp = requests.post(HELIUS_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("result", {})
    except Exception as e:
        print(f"Error fetching tx: {e}")
    return None

def analyze_wallet_trades(wallet: str, days: int = 7) -> Optional[Dict]:
    """Analyze a wallet's recent trading activity"""
    try:
        url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions"
        params = {"api-key": HELIUS_API_KEY, "limit": 100}
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code != 200:
            return None
        
        txs = resp.json()
        
        # Analyze patterns
        token_buys = {}
        token_sells = {}
        total_volume = 0
        
        for tx in txs:
            # Parse token transfers
            transfers = tx.get("tokenTransfers", [])
            for transfer in transfers:
                mint = transfer.get("mint", "")
                to = transfer.get("toUserAccount", "")
                from_addr = transfer.get("fromUserAccount", "")
                amount = float(transfer.get("tokenAmount", 0))
                
                if not mint or mint == "So11111111111111111111111111111111111111112":
                    continue
                
                if to == wallet:
                    # Buy
                    if mint not in token_buys:
                        token_buys[mint] = []
                    token_buys[mint].append({
                        "amount": amount,
                        "time": tx.get("timestamp", 0)
                    })
                elif from_addr == wallet:
                    # Sell
                    if mint not in token_sells:
                        token_sells[mint] = []
                    token_sells[mint].append({
                        "amount": amount,
                        "time": tx.get("timestamp", 0)
                    })
        
        # Calculate metrics
        unique_tokens = set(list(token_buys.keys()) + list(token_sells.keys()))
        total_buys = sum(len(v) for v in token_buys.values())
        total_sells = sum(len(v) for v in token_sells.values())
        
        # Find tokens with both buy and sell (completed trades)
        completed_trades = []
        for token in unique_tokens:
            if token in token_buys and token in token_sells:
                buy_count = len(token_buys[token])
                sell_count = len(token_sells[token])
                if buy_count > 0 and sell_count > 0:
                    completed_trades.append({
                        "token": token,
                        "buys": buy_count,
                        "sells": sell_count
                    })
        
        return {
            "wallet": wallet,
            "total_buys": total_buys,
            "total_sells": total_sells,
            "unique_tokens": len(unique_tokens),
            "completed_trades": len(completed_trades),
            "buy_sell_ratio": total_buys / max(total_sells, 1),
            "activity_score": (total_buys + total_sells) * len(unique_tokens)
        }
        
    except Exception as e:
        print(f"Error analyzing wallet {wallet}: {e}")
        return None

def find_whales_from_transactions():
    """Find whales by analyzing recent profitable transactions"""
    print("🔍 Searching for profitable whale wallets...\n")
    
    # Sample high-activity wallets to analyze (these would be discovered dynamically)
    # In production, you'd scan recent successful token launches and find early buyers
    test_wallets = [
        # These are example addresses - in real usage, scan recent token launches
        "JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv",  # Your current target
    ]
    
    print("Analyzing wallet activity...\n")
    
    results = []
    for wallet in test_wallets:
        print(f"Checking {wallet[:20]}...")
        analysis = analyze_wallet_trades(wallet)
        if analysis:
            results.append(analysis)
    
    if not results:
        print("\n⚠️ Could not analyze wallets via API")
        print("\n💡 Alternative: Use DeBank to find whales manually")
        print("   1. Go to https://debank.com/ranking")
        print("   2. Filter by Solana")
        print("   3. Look for wallets with:")
        print("      - High ROI")
        print("      - Consistent profits")
        print("      - Early entry patterns")
        return
    
    # Sort by activity score
    results.sort(key=lambda x: x["activity_score"], reverse=True)
    
    print("\n" + "="*70)
    print("🐳 WHALE ANALYSIS RESULTS")
    print("="*70)
    
    for i, whale in enumerate(results[:5], 1):
        print(f"\n{i}. Wallet: {whale['wallet']}")
        print(f"   Activity Score: {whale['activity_score']:.0f}")
        print(f"   Buys: {whale['total_buys']} | Sells: {whale['total_sells']}")
        print(f"   Buy/Sell Ratio: {whale['buy_sell_ratio']:.2f}")
        print(f"   Unique Tokens: {whale['unique_tokens']}")
        print(f"   Completed Trades: {whale['completed_trades']}")
        print(f"\n   ➜ Add: python3 run_tracker_v2.py add-wallet {whale['wallet']} \"Whale_{i}\" 1.0")

def generate_whale_recommendations():
    """Generate wallet recommendations based on patterns"""
    print("\n" + "="*70)
    print("📋 WHALE WALLET RECOMMENDATIONS")
    print("="*70)
    
    print("""
Based on successful meme coin trading patterns, here are wallet types to track:

1️⃣ EARLY ADOPTERS (Best for 10x+ gains)
   - Buy within first 30 minutes of launch
   - Small position sizes (0.1-0.5 SOL)
   - High volume of trades (20+ per day)
   - How to find: Check token launch block explorers

2️⃣ SWING TRADERS (Consistent 20-50% gains)
   - Hold 2-48 hours
   - Take profits at +25%, +50%, +100%
   - Cut losses at -10%
   - How to find: DeBank ROI leaderboard

3️⃣ SMART MONEY (Insider signals)
   - Buy before major announcements
   - Often dev wallets or connected wallets
   - Large positions (1-5 SOL)
   - How to find: Token holder analysis

4️⃣ SNIPERS (Automated bots)
   - Multiple buys in <5 seconds
   - Always first 10 buyers
   - Sell within 1 hour
   - How to find: Transaction pattern analysis

""")
    
    print("="*70)
    print("🔧 TOOLS TO FIND WHALES")
    print("="*70)
    print("""
1. DeBank (https://debank.com)
   - Go to Ranking → Solana
   - Filter by ROI, time period
   - Click wallets to see trade history

2. Solscan (https://solscan.io)
   - Find trending tokens
   - Check 'Holders' tab
   - Look for early buyers

3. Birdeye (https://birdeye.so)
   - Wallet analyzer tool
   - Shows P&L for any wallet

4. AlphaVybe (https://alphavybe.com)
   - Smart money tracking
   - Whale alerts

5. Step Finance (https://step.finance)
   - Portfolio tracking
   - Whale watching
""")

def create_sample_wallets():
    """Create a list of sample whale wallets to track"""
    # These are placeholder - user should replace with real profitable wallets
    sample_wallets = [
        {
            "name": "Smart Money A",
            "description": "Consistent 30%+ gains on meme coins",
            "strategy": "Early entry, quick exits",
            "risk_level": "medium"
        },
        {
            "name": "Diamond Hands",
            "description": "Holds for 2x-5x gains",
            "strategy": "High conviction, longer holds",
            "risk_level": "medium"
        },
        {
            "name": "Snipe King",
            "description": "Always in first 50 buyers",
            "strategy": "Ultra-early entry",
            "risk_level": "high"
        }
    ]
    
    print("\n" + "="*70)
    print("📝 SAMPLE WHALE PROFILES")
    print("="*70)
    
    for wallet in sample_wallets:
        print(f"\n🐋 {wallet['name']}")
        print(f"   Description: {wallet['description']}")
        print(f"   Strategy: {wallet['strategy']}")
        print(f"   Risk: {wallet['risk_level']}")

if __name__ == "__main__":
    print("🔍 Whale Wallet Finder")
    print("="*70)
    
    # Try to find whales from transactions
    find_whales_from_transactions()
    
    # Generate recommendations
    generate_whale_recommendations()
    
    # Show sample profiles
    create_sample_wallets()
    
    print("\n" + "="*70)
    print("✅ NEXT STEPS")
    print("="*70)
    print("""
1. Visit DeBank and find 2-3 profitable wallets
2. Copy their addresses
3. Add them: python3 run_tracker_v2.py add-wallet <address> <name>
4. Start tracking: python3 run_tracker_v2.py start

Your current wallet (JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv)
is already configured and ready to monitor.
""")
