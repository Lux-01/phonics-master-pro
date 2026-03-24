#!/usr/bin/env python3
"""
🎯 100K POTENTIAL SCANNER V3
Using DexScreener API for Solana tokens
"""

import requests
import json
from datetime import datetime

TARGET_MC = 100000

print("="*80)
print("🎯 100K POTENTIAL SCANNER - Solana Memecoins (via DexScreener)")
print(f"Target: ${TARGET_MC:,} Market Cap")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Get latest Solana token pairs from DexScreener
tokens = []
print("\n📊 Fetching Solana tokens from DexScreener...")

try:
    # Get trending pairs on Solana
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    resp = requests.get(url, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        pairs = data.get('pairs', [])
        
        # Get unique tokens (pick best pair per token)
        seen = set()
        for pair in pairs:
            if not pair:
                continue
            base = pair.get('baseToken', {})
            quote = pair.get('quoteToken', {})
            
            # Get the memecoin (not SOL/USDC)
            if base.get('symbol') in ['SOL', 'USDC', 'USDT']:
                continue
            if quote.get('symbol') not in ['SOL', 'USDC', 'USDT']:
                continue
            
            token_addr = base.get('address')
            if token_addr in seen:
                continue
            seen.add(token_addr)
            
            fdv = float(pair.get('fdv', 0) or 0)
            mc = float(pair.get('marketCap', 0) or fdv or 0)
            v24h = float(pair.get('volume', {}).get('h24', 0) or 0)
            
            tokens.append({
                'symbol': base.get('symbol', '???'),
                'name': base.get('name', 'Unknown'),
                'address': token_addr,
                'mc': mc,
                'fdv': fdv,
                'v24h': v24h,
                'pair': pair.get('pairAddress'),
                'dexId': pair.get('dexId'),
                'priceUsd': pair.get('priceUsd', 0),
                'priceChange24h': pair.get('priceChange', {}).get('h24', 0)
            })
        
        print(f"✅ Found {len(tokens)} unique tokens")
        
except Exception as e:
    print(f"⚠️ Error: {e}")

# Filter for 100k potential
print("\n" + "="*80)
print("🔍 ANALYZING FOR 100K POTENTIAL...")
print("="*80)

candidates_100k = []
candidates_big = []

for token in tokens:
    mc = token.get('mc', 0)
    v24h = token.get('v24h', 0)
    
    # Focus on 10k-90k range (room to grow to 100k)
    if 5000 <= mc < 90000:
        multiplier = TARGET_MC / mc if mc > 0 else 0
        vol_ratio = v24h / mc if mc > 0 else 0
        
        # Score: easier to reach + good volume
        score = (100 - min(multiplier * 15, 80)) + min(vol_ratio * 20, 50)
        score = min(max(score, 0), 100)
        
        candidates_100k.append({
            **token,
            'multiplier': multiplier,
            'vol_ratio': vol_ratio,
            'score': score
        })
    
    # Also check tokens that already hit 100k+ (for context)
    elif mc >= TARGET_MC:
        candidates_big.append(token)

# Sort by score
if candidates_100k:
    candidates_100k.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🎯 FOUND {len(candidates_100k)} TOKENS WITH 100K POTENTIAL:")
    print("-"*80)
    
    shown = 0
    for i, c in enumerate(candidates_100k[:25], 1):
        if c['mc'] < 1000:  # Skip very low MC
            continue
        shown += 1
        
        # Badge based on current MC
        if c['mc'] >= 70000:
            badge = "🚀 CLOSE"
        elif c['mc'] >= 50000:
            badge = "⭐ GOOD"
        elif c['mc'] >= 30000:
            badge = "📈 WATCH"
        elif c['mc'] >= 15000:
            badge = "👀 EARLY"
        else:
            badge = "🔥 RISKY"
        
        action = "💰 STRONG" if c['vol_ratio'] > 0.5 else "⚡ MODERATE" if c['vol_ratio'] > 0.2 else "👀 LOW"
        
        print(f"\n{shown}. {c['symbol']} ({c['name'][:20]})")
        print(f"   Current MC: ${c['mc']:,.0f}")
        print(f"   Target: ${TARGET_MC:,} | Needs {c['multiplier']:.1f}x pump")
        print(f"   Volume 24h: ${c['v24h']:,.0f}")
        print(f"   Price: ${c['priceUsd']:.6f} ({c.get('priceChange24h', 0):+.1f}%)")
        print(f"   Score: {c['score']:.0f}/100 | {badge} | {action}")
        print(f"   CA: {c['address']}")
    
    if shown == 0:
        print("   (No qualifying tokens with MC > 1k)")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY BY RANGE:")
    print("="*80)
    
    close_mc = len([c for c in candidates_100k if c['mc'] >= 70000])
    good_mc = len([c for c in candidates_100k if 50000 <= c['mc'] < 70000])
    watch_mc = len([c for c in candidates_100k if 30000 <= c['mc'] < 50000])
    early_mc = len([c for c in candidates_100k if 15000 <= c['mc'] < 30000])
    risky_mc = len([c for c in candidates_100k if c['mc'] < 15000])
    
    print(f"  🚀 Close (70k-90k):      {close_mc} tokens - CLOSE TO TARGET")
    print(f"  ⭐ Good (50k-70k):        {good_mc} tokens - Strong candidates")
    print(f"  📈 Watch (30k-50k):      {watch_mc} tokens - Good momentum")
    print(f"  👀 Early (15k-30k):       {early_mc} tokens - Higher risk/reward")
    print(f"  🔥 Risky (5k-15k):        {risky_mc} tokens - Micro gems")
    print(f"  📦 Total candidates:      {len(candidates_100k)} tokens")
    
    # Top picks
    print("\n" + "="*80)
    print("🏆 TOP 5 RECOMMENDATIONS:")
    print("="*80)
    
    pick_num = 1
    for c in candidates_100k[:5]:
        if c['mc'] < 1000:
            continue
        risk = "LOW" if c['mc'] >= 50000 else "MED" if c['mc'] >= 30000 else "HIGH"
        print(f"{pick_num}. {c['symbol']} - ${c['mc']:,.0f} MC → {c['multiplier']:.1f}x to 100k [Risk: {risk}]")
        pick_num += 1
        
else:
    print("\n❌ No tokens found in 5k-90k MC range")

# Show tokens already past 100k
if candidates_big:
    print("\n" + "="*80)
    print("💎 TOKENS ALREADY AT/ABOVE 100K:")
    print("="*80)
    
    candidates_big.sort(key=lambda x: x['mc'], reverse=True)
    for c in candidates_big[:10]:
        print(f"  • {c['symbol']}: ${c['mc']:,.0f} MC ({c['v24h']:,.0f} 24h vol)")
else:
    print("\n⚠️ No tokens currently above 100k MC in this scan")

print("\n" + "="*80)
print("✅ SCAN COMPLETE")
print("Check DexScreener for real-time charts and trading")
print("="*80)
