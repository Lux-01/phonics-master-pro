#!/usr/bin/env python3
"""
🎯 100K POTENTIAL SCANNER
Find tokens in the 20k-80k MC range that could pump to 100k+
Looks for: Early tokens, volume spikes, positive momentum
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
TARGET_MC = 100000

print("="*70)
print("🎯 SCANNING FOR TOKENS WITH 100K POTENTIAL")
print(f"Target: Reaching ${TARGET_MC:,} MC")
print(f"Current Time (Sydney): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

headers = {"x-api-key": BIRDEYE_API_KEY}
params = {
    "sort_by": "mc",
    "sort_type": "desc",
    "min_marketcap": 0,
    "max_marketcap": 150000,
    "offset": 0,
    "limit": 50
}

print("\n📊 Fetching tokens from Birdeye...")

# Get trending tokens
tokens = []
try:
    url = "https://public-api.birdeye.so/defi/v2/tokens"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        tokens = data.get('data', [])
except Exception as e:
    print(f"Error: {e}")

print(f"✅ Found {len(tokens)} tokens")

# Score and filter tokens
candidates = []
print("\n" + "="*70)
print("🔍 ANALYZING TOKENS...")
print("="*70)

for token in tokens:
    mc = token.get('marketCap', 0) or token.get('mc', 0) or 0
    v24h = token.get('v24hUSD', 0) or token.get('volume24hUSD', 0) or 0
    price = token.get('price', 0) or 0
    
    # Focus on 5k-80k range (room to grow to 100k)
    if 5000 < mc < 80000:
        symbol = token.get('symbol', '???')[:10]
        address = token.get('address', '')
        name = token.get('name', 'Unknown')[:20]
        
        # Calculate scores
        mc_score = min((mc / TARGET_MC) * 100, 100)  # Closer to target = better
        vol_ratio = (v24h / mc) if mc > 0 else 0
        vol_score = min(vol_ratio * 10, 100)  # High volume relative to MC
        
        # Calculate potential score (how likely to hit 100k)
        potential = (mc_score * 0.3) + (vol_score * 0.7)  # Volume matters more
        
        if potential > 30:  # Lower threshold for more results
            candidates.append({
                'symbol': symbol,
                'name': name,
                'address': address,
                'mc': mc,
                'mc_score': int(mc_score),
                'v24h': v24h,
                'vol_score': int(vol_score),
                'potential': int(potential),
                'distance_to_100k': TARGET_MC - mc,
                'multiplier_needed': TARGET_MC / mc if mc > 0 else 0
            })

# Sort by potential
if candidates:
    candidates.sort(key=lambda x: x['potential'], reverse=True)
    
    print(f"\n🎯 TOP {len(candidates)} CANDIDATES (5k-80k MC with growth potential):")
    print("-"*70)
    
    for i, c in enumerate(candidates[:15], 1):
        status = "🔥 HIGH" if c['potential'] > 80 else "⭐ GOOD" if c['potential'] > 60 else "📈 WATCH"
        print(f"\n{i}. {c['symbol']} ({c['name']})")
        print(f"   MC: ${c['mc']:,.0f} | Needs {c['multiplier_needed']:.1f}x to hit 100k")
        print(f"   Volume 24h: ${c['v24h']:,.0f}")
        print(f"   Potential Score: {c['potential']}/100 {status}")
        print(f"   CA: {c['address']}")
    
    # Summary stats
    print("\n" + "="*70)
    print("📊 SUMMARY:")
    print("="*70)
    high_potential = len([c for c in candidates if c['potential'] > 80])
    good_potential = len([c for c in candidates if 60 < c['potential'] <= 80])
    print(f"  🔥 High Potential (>80): {high_potential} tokens")
    print(f"  ⭐ Good Potential (60-80): {good_potential} tokens")
    print(f"  📈 Total Watchable: {len(candidates)} tokens")
    
else:
    print("\n❌ No tokens found in the 5k-80k MC range")

# Also show tokens close to 100k (80k-150k)
print("\n" + "="*70)
print("🚀 TOKENS CLOSE TO 100K (80k-150k MC):")
print("="*70)

close_tokens = []
for token in tokens:
    mc = token.get('marketCap', 0) or token.get('mc', 0) or 0
    if 80000 <= mc <= 150000:
        symbol = token.get('symbol', '???')[:10]
        address = token.get('address', '')
        v24h = token.get('v24hUSD', 0) or 0
        progress = (mc / TARGET_MC) * 100
        close_tokens.append({
            'symbol': symbol,
            'mc': mc,
            'v24h': v24h,
            'address': address,
            'progress': progress
        })

if close_tokens:
    close_tokens.sort(key=lambda x: x['mc'], reverse=True)
    for c in close_tokens[:10]:
        print(f"  • {c['symbol']}: ${c['mc']:,.0f} MC ({c['progress']:.0f}% of 100k)")
else:
    print("  No tokens in the 80k-150k range")

print("\n" + "="*70)
print("✅ SCAN COMPLETE")
print("="*70)
