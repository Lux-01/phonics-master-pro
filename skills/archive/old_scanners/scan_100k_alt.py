#!/usr/bin/env python3
"""
🎯 100K POTENTIAL SCANNER V2
Alternative approach using DexScreener + manual filtering
"""

import requests
import json
from datetime import datetime

TARGET_MC = 100000

print("="*75)
print("🎯 SCANNING FOR TOKENS WITH 100K POTENTIAL (Birdeye + DexScreener)")
print(f"Target: Reaching ${TARGET_MC:,} MC")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*75)

# Get trending from Birdeye
tokens = []
try:
    print("\n📊 Fetching trending tokens from Birdeye...")
    url = "https://public-api.birdeye.so/defi/tokenlist"
    headers = {"x-api-key": "6335463fca7340f9a2c73eacd5a37f64"}
    params = {"sort_by": "v24hUSD", "sort_type": "desc", "offset": 0, "limit": 200}
    
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        tokens = data.get('data', {}).get('tokens', [])
        print(f"✅ Got {len(tokens)} tokens from Birdeye tokenlist")
except Exception as e:
    print(f"⚠️ Birdeye error: {e}")

# Filter for 100k potential
candidates = []
print("\n" + "="*75)
print("🔍 FILTERING FOR 100K POTENTIAL CANDIDATES...")
print("="*75)

for token in tokens:
    try:
        mc = float(token.get('mc', 0) or token.get('marketCap', 0) or 0)
        v24h = float(token.get('v24hUSD', 0) or token.get('volume24hUSD', 0) or 0)
        
        # FOCUS: 10k to 90k MC (room to grow to 100k)
        if 10000 <= mc < 90000:
            symbol = token.get('symbol', '???')[:12]
            name = token.get('name', 'Unknown')[:25]
            address = token.get('address', '')
            
            # Volume-to-MC ratio (momentum indicator)
            vol_ratio = v24h / mc if mc > 0 else 0
            
            # Calculate how many multiples to reach 100k
            multiplier = TARGET_MC / mc if mc > 0 else 0
            
            # Score: lower multiplier = easier to reach target
            # Plus volume ratio for momentum
            potential_score = ((2 - min(multiplier/5, 1.5)) * 50) + (vol_ratio * 30)
            potential_score = min(max(potential_score, 0), 100)
            
            candidates.append({
                'symbol': symbol,
                'name': name,
                'address': address,
                'mc': mc,
                'v24h': v24h,
                'multiplier': multiplier,
                'vol_ratio': vol_ratio,
                'score': potential_score
            })
    except:
        continue

# Sort by score
if candidates:
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🎯 FOUND {len(candidates)} TOKENS WITH 100K POTENTIAL:")
    print("-"*75)
    
    for i, c in enumerate(candidates[:20], 1):
        # Status badge
        if c['mc'] >= 70000:
            badge = "🚀 CLOSE"
        elif c['mc'] >= 50000:
            badge = "⭐ GOOD"
        elif c['mc'] >= 30000:
            badge = "📈 WATCH"
        else:
            badge = "👀 EARLY"
        
        print(f"\n{i}. {c['symbol']} ({c['name']})")
        print(f"   Current MC: ${c['mc']:,.0f}")
        print(f"   Needs: {c['multiplier']:.1f}x to reach 100k")
        print(f"   Volume 24h: ${c['v24h']:,.0f} (Ratio: {c['vol_ratio']:.2f})")
        print(f"   Potential Score: {c['score']:.0f}/100 {badge}")
        print(f"   CA: {c['address']}")
    
    # Summary by tier
    print("\n" + "="*75)
    print("📊 TIER BREAKDOWN:")
    close_100k = len([c for c in candidates if c['mc'] >= 70000])
    good_range = len([c for c in candidates if 50000 <= c['mc'] < 70000])
    watch_range = len([c for c in candidates if 30000 <= c['mc'] < 50000])
    early_range = len([c for c in candidates if c['mc'] < 30000])
    
    print(f"  🚀 Close to 100k (70k-90k):  {close_100k} tokens")
    print(f"  ⭐ Good position (50k-70k):   {good_range} tokens")
    print(f"  📈 Watch list (30k-50k):      {watch_range} tokens")
    print(f"  👀 Early stage (10k-30k):      {early_range} tokens")
    
    # Best candidates
    print("\n" + "="*75)
    print("🏆 TOP 5 OPPORTUNITIES:")
    print("="*75)
    for i, c in enumerate(candidates[:5], 1):
        action = "BUY" if c['vol_ratio'] > 0.5 else "WATCH"
        print(f"{i}. {c['symbol']} - ${c['mc']:,.0f} MC → needs {c['multiplier']:.1f}x [{action}]")
        print(f"   CA: {c['address']}")
        
else:
    print("\n❌ No tokens found in 10k-90k MC range")

# Also show tokens already at/near 100k
print("\n" + "="*75)
print("💎 TOKENS AT/NEAR 100K TARGET (90k-150k):")
print("="*75)

at_target = []
for token in tokens:
    try:
        mc = float(token.get('mc', 0) or 0)
        if 90000 <= mc <= 150000:
            symbol = token.get('symbol', '???')[:12]
            v24h = float(token.get('v24hUSD', 0) or 0)
            progress = (mc / TARGET_MC) * 100
            at_target.append({
                'symbol': symbol,
                'mc': mc,
                'v24h': v24h,
                'progress': progress
            })
    except:
        continue

if at_target:
    at_target.sort(key=lambda x: x['mc'], reverse=True)
    for c in at_target[:10]:
        print(f"  • {c['symbol']}: ${c['mc']:,.0f} MC ({c['progress']:.0f}% of target)")
else:
    print("  No tokens currently in 90k-150k range")

print("\n" + "="*75)
print("✅ SCAN COMPLETE - Check DexScreener for latest movement")
print("="*75)
