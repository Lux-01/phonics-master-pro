#!/usr/bin/env python3
"""
🚀 100K POTENTIAL SCANNER V4
Direct DexScreener trending page
"""

import requests
from datetime import datetime

TARGET_MC = 100000

print("="*80)
print("🚀 100K SCANNER - DexScreener Token Profiles API")
print("="*80)

# Get token profiles (new endpoint)
print("\n📡 Fetching token profiles...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

pairs = []

# Try the trending endpoint
try:
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        tokens = data if isinstance(data, list) else data.get('tokens', [])
        print(f"✅ Got {len(tokens)} tokens from token-profiles")
        
        # Try to get pairs from token data
        for t in tokens:
            if isinstance(t, dict):
                pairs.append({
                    'symbol': t.get('symbol', '???'),
                    'name': t.get('name', 'Unknown'),
                    'address': t.get('tokenAddress', t.get('address', '')),
                    'mc': float(t.get('marketCap', t.get('mc', 0)) or 0),
                    'v24h': float(t.get('volume24hUSD', t.get('v24hUSD', 0)) or 0),
                    'price': float(t.get('priceUSD', t.get('price', 0)) or 0)
                })
except Exception as e:
    print(f"⚠️ token-profiles failed: {e}")

# Also try pairs endpoint
if not pairs:
    try:
        print("📡 Trying pairs endpoint...")
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            raw_pairs = data.get('pairs', [])
            print(f"✅ Got {len(raw_pairs)} pairs from Solana")
            
            seen = set()
            for p in raw_pairs[:100]:
                base = p.get('baseToken', {})
                if not base:
                    continue
                    
                addr = base.get('address')
                if addr in seen:
                    continue
                seen.add(addr)
                
                fdv = float(p.get('fdv', 0) or 0)
                mc = float(p.get('marketCap', fdv) or 0)
                
                pairs.append({
                    'symbol': base.get('symbol', '???'),
                    'name': base.get('name', 'Unknown'),
                    'address': addr,
                    'mc': mc,
                    'v24h': float(p.get('volume', {}).get('h24', 0) or 0),
                    'price': float(p.get('priceUsd', 0) or p.get('priceNative', 0) or 0)
                })
                
    except Exception as e:
        print(f"⚠️ pairs endpoint failed: {e}")

if not pairs:
    print("\n❌ No data from DexScreener APIs")
    print("\nTrying Jupiter token list...")
    
    try:
        # Try Jupiter strict list
        url = "https://api.jup.ag/coins?list=strict"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            tokens = data.get('coins', [])
            print(f"✅ Got {len(tokens)} tokens from Jupiter")
            
            for t in tokens:
                pairs.append({
                    'symbol': t.get('symbol', '???'),
                    'name': t.get('name', 'Unknown'),
                    'address': t.get('address', ''),
                    'mc': 0,  # Jupiter doesn't give MC
                    'v24h': 0,
                    'price': 0
                })
    except Exception as e:
        print(f"⚠️ Jupiter failed: {e}")

if not pairs:
    print("\n❌ All APIs failed. Market might be quiet or APIs are down.")
    exit(0)

# Filter for 100k potential
print("\n" + "="*80)
print("🔍 FILTERING FOR 100K POTENTIAL...")
print("="*80)

candidates = []

for token in pairs:
    mc = token.get('mc', 0)
    v24h = token.get('v24h', 0)
    
    # Check 10k to 90k range
    if 10000 <= mc < 90000:
        multiplier = TARGET_MC / mc if mc > 0 else 0
        vol_ratio = v24h / mc if mc > 0 else 0
        
        score = (100 - multiplier * 5) + vol_ratio * 25
        score = min(max(score, 0), 100)
        
        candidates.append({
            **token,
            'multiplier': multiplier,
            'vol_ratio': vol_ratio,
            'score': score
        })

if candidates:
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🎯 FOUND {len(candidates)} CANDIDATES FOR 100K:")
    print("-"*80)
    
    for i, c in enumerate(candidates[:20], 1):
        badge = "🚀 CLOSE" if c['mc'] >= 70000 else "⭐ GOOD" if c['mc'] >= 50000 else "📈 WATCH"
        print(f"\n{i}. {c['symbol']}")
        print(f"   MC: ${c['mc']:,.0f} | Needs {c['multiplier']:.1f}x | ${c['v24h']:,.0f} vol")
        print(f"   Score: {c['score']:.0f}/100 {badge}")
        print(f"   CA: {c['address']}")
    
    # Summary
    print("\n" + "="*80)
    close_range = len([c for c in candidates if c['mc'] >= 70000])
    good_range = len([c for c in candidates if 50000 <= c['mc'] < 70000])
    watch_range = len([c for c in candidates if c['mc'] < 50000])
    
    print(f"Close (70k+): {close_range}")
    print(f"Good (50-70k): {good_range}")
    print(f"Watch (<50k): {watch_range}")
    print(f"Total: {len(candidates)}")
else:
    print("\n⚠️ No tokens found in 10k-90k MC range")
    print(f"\nTokens scanned: {len(pairs)}")
    
    # Show what we did find
    if pairs:
        print("\nSample tokens found:")
        for c in pairs[:5]:
            print(f"  • {c['symbol']}: ${c['mc']:,.0f} MC")

print("\n" + "="*80)
print("✅ SCAN COMPLETE")
print("="*80)
