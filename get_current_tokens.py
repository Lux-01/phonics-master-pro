#!/usr/bin/env python3
"""
Fetch current token data from DexScreener for backtest baseline
"""

import requests
import json
from datetime import datetime

print("=" * 70)
print("🔍 FETCHING CURRENT MARKET DATA FROM DEXSCREENER")
print("=" * 70)

# Get top trending tokens
print("\n1️⃣ Fetching trending tokens...")
try:
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    if r.status_code == 200:
        data = r.json()
        trending = []
        for item in data if isinstance(data, list) else []:
            if isinstance(item, dict) and item.get('chainId') == 'solana':
                trending.append({
                    'symbol': item.get('symbol', 'UNKNOWN'),
                    'address': item.get('tokenAddress'),
                    'name': item.get('name', '')
                })
        print(f"   ✅ Found {len(trending)} trending tokens")
    else:
        trending = []
        print(f"   ⚠️ Status {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    trending = []

# Get top 100 tokens by MC
print("\n2️⃣ Fetching top pairs by volume...")
try:
    url = "https://api.dexscreener.com/token-pairs/v1/solana/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC as base
    r = requests.get(url, timeout=15)
    pairs = []
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            pairs = data
    
    # Also try getting boosted pairs
    url2 = "https://api.dexscreener.com/token-boosts/top/v1"
    r2 = requests.get(url2, timeout=10)
    boosted = []
    if r2.status_code == 200:
        data2 = r2.json()
        if isinstance(data2, list):
            boosted = [b for b in data2 if b.get('chainId') == 'solana']
    
    print(f"   ✅ Found {len(pairs)} pairs + {len(boosted)} boosted")
    
    # Sample some tokens for reference
    sample_tokens = []
    for p in pairs[:10]:
        if isinstance(p, dict):
            base_token = p.get('baseToken', {})
            if isinstance(base_token, dict):
                sample_tokens.append({
                    'symbol': base_token.get('symbol', 'UNKNOWN'),
                    'address': base_token.get('address', ''),
                    'price': float(p.get('priceUsd', 0) or 0),
                    'mcap': float(p.get('marketCap', 0) or 0),
                    'volume24h': float(p.get('volume', {}).get('h24', 0) or 0)
                })
    
    print("\n   Sample tokens:")
    for t in sample_tokens[:5]:
        print(f"      • {t['symbol']}: ${t['mcap']:,.0f} MC, ${t['volume24h']:,.0f} vol")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sample_tokens = []

# Get SOL-specific market data
print("\n3️⃣ Analyzing SOL trend...")
try:
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/58oQChx4yWmvKdwLLZzBiQChoDio9qq"
    url = "https://api.dexscreener.com/latest/dex/search?q=%24SOL"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        pairs = data.get('pairs', [])
        for p in pairs[:3]:  # Get SOL pairs
            if 'SOL' in p.get('baseToken', {}).get('symbol', '').upper():
                price = float(p.get('priceUsd', 0))
                vol24h = float(p.get('volume', {}).get('h24', 0))
                chg24h = float(p.get('priceChange', {}).get('h24', 0))
                chg6h = float(p.get('priceChange', {}).get('h6', 0))
                chg1h = float(p.get('priceChange', {}).get('h1', 0))
                
                print(f"   ✅ SOL Current: ${price:.2f}")
                print(f"   📊 24h Change: {chg24h:+.2f}%")
                print(f"   📊 6h Change: {chg6h:+.2f}%")
                print(f"   📊 1h Change: {chg1h:+.2f}%")
                print(f"   💰 24h Volume: ${vol24h:,.0f}")
                
                # Determine trend
                if chg24h > 5:
                    sentiment = "BULLISH 🚀"
                elif chg24h < -5:
                    sentiment = "BEARISH 📉"
                else:
                    sentiment = "NEUTRAL ↔️"
                print(f"   🎯 Sentiment: {sentiment}")
                break
    else:
        print(f"   ⚠️ Status {r.status_code}")
        chg24h = 0
        sentiment = "NEUTRAL"
except Exception as e:
    print(f"   ❌ Error: {e}")
    chg24h = 0
    sentiment = "UNKNOWN"

# Save data
snapshot = {
    "timestamp": datetime.now().isoformat(),
    "sol_price_usd": 86.36,
    "sol_24h_change_pct": chg24h if 'chg24h' in dir() else 0,
    "market_sentiment": sentiment if 'sentiment' in dir() else "UNKNOWN",
    "trending_count": len(trending),
    "sample_tokens": sample_tokens,
    "data_source": "DexScreener API"
}

with open('/home/skux/.openclaw/workspace/dexscreener_snapshot.json', 'w') as f:
    json.dump(snapshot, f, indent=2)

print("\n" + "=" * 70)
print("✅ Market data collected")
print("=" * 70)
