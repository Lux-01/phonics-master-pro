#!/usr/bin/env python3
"""
Quick Whale Finder - Find profitable wallets from recent token data
Uses DexScreener API to find tokens with good performance
"""

import requests
import json
from datetime import datetime, timedelta

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search"

def find_recent_gainers():
    """Find tokens that have pumped recently"""
    print("🔍 Searching for recent high-performers...\n")
    
    # Search for trending tokens
    searches = ["solana", "meme", "pump", "trending"]
    all_tokens = []
    
    for query in searches:
        try:
            resp = requests.get(f"{DEXSCREENER_API}?q={query}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                for pair in pairs[:10]:
                    if pair.get("chainId") == "solana":
                        all_tokens.append(pair)
        except Exception as e:
            print(f"Error searching {query}: {e}")
    
    # Filter for recent pumps
    gainers = []
    for token in all_tokens:
        try:
            price_change = token.get("priceChange", {})
            h24 = price_change.get("h24", 0)
            
            # Look for tokens with 50%+ gains
            if h24 and float(h24) > 50:
                gainers.append({
                    "symbol": token.get("baseToken", {}).get("symbol", "?"),
                    "address": token.get("baseToken", {}).get("address", ""),
                    "priceChange24h": h24,
                    "volume24h": token.get("volume", {}).get("h24", 0),
                    "liquidity": token.get("liquidity", {}).get("usd", 0),
                    "pairAddress": token.get("pairAddress", "")
                })
        except:
            pass
    
    # Sort by price change
    gainers.sort(key=lambda x: float(x.get("priceChange24h", 0)), reverse=True)
    
    return gainers[:5]  # Top 5

def analyze_token_holders(token_address):
    """Get early buyers of a token"""
    # This would require Helius API or Birdeye
    # For now, return placeholder
    return []

def main():
    print("="*70)
    print("🐳 QUICK WHALE FINDER")
    print("="*70)
    print("\nFinding recent high-performers to analyze...\n")
    
    gainers = find_recent_gainers()
    
    if not gainers:
        print("❌ Could not fetch token data from DexScreener")
        print("\n💡 Manual method:")
        print("   1. Go to https://dexscreener.com/solana")
        print("   2. Sort by 24h gainers")
        print("   3. Click a token that pumped 5x+")
        print("   4. Check 'Holders' tab")
        print("   5. Look for wallets in first 100 buyers")
        return
    
    print(f"Found {len(gainers)} recent gainers:\n")
    
    for i, token in enumerate(gainers, 1):
        print(f"{i}. {token['symbol']}")
        print(f"   24h Change: +{token['priceChange24h']}%")
        print(f"   Volume: ${token['volume24h']:,.0f}")
        print(f"   Liquidity: ${token['liquidity']:,.0f}")
        print(f"   Address: {token['address']}")
        print()
    
    print("="*70)
    print("📋 NEXT STEPS")
    print("="*70)
    print("""
To find the whales who bought these early:

1. Visit Solscan for each token:
   https://solscan.io/token/<ADDRESS>

2. Click "Holders" tab

3. Look for wallets that:
   - Are in first 100 holders
   - Still hold significant amount
   - Have multiple successful tokens

4. Copy wallet addresses and add:
   python3 run_tracker_v2.py add-wallet <ADDRESS> "Whale_Name" 1.0

5. Verify on DeBank:
   https://debank.com/profile/<WALLET_ADDRESS>
""")

if __name__ == "__main__":
    main()
