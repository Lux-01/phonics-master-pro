#!/usr/bin/env python3
"""
🚀 LIVE 100K POTENTIAL SCANNER - V5
Uses DexScreener pairs endpoint for Solana
"""

import requests
from datetime import datetime

TARGET_MC = 100000

print("="*80)
print("🚀 LIVE 100K POTENTIAL SCANNER - Solana")  
print(f"Target: ${TARGET_MC:,} MC | Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80)

tokens = []
print("\n📊 Fetching Solana pairs from DexScreener...")

try:
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        pairs = data.get('pairs', [])
        
        print(f"✅ Got {len(pairs)} Solana pairs")
        
        # Extract unique tokens
        seen = set()
        for p in pairs:
            if not p:
                continue
                
            base = p.get('baseToken', {})
            if not base:
                continue
                
            addr = base.get('address', '')
            if not addr or addr in seen:
                continue
            
            # Skip SOL, USDC, USDT
            sym = base.get('symbol', '').upper()
            if sym in ['SOL', 'USDC', 'USDT']:
                continue
            
            seen.add(addr)
            
            # Get market cap
            mc = float(p.get('marketCap', 0) or p.get('fdv', 0) or 0)
            v24h = float(p.get('volume', {}).get('h24', 0) or 0)
            price = float(p.get('priceUsd', 0) or p.get('priceNative', 0) or 0)
            
            tokens.append({
                'symbol': base.get('symbol', '???'),
                'name': base.get('name', 'Unknown'),
                'address': addr,
                'mc': mc,
                'v24h': v24h,
                'price': price,
                'dex': p.get('dexId', 'DexScreener')
            })
            
        print(f"✅ Extracted {len(tokens)} unique tokens")
        
except Exception as e:
    print(f"❌ Error: {e}")
    tokens = []

if not tokens:
    print("\n❌ No data available")
    exit(0)

# Filter for 100k potential
print("\n" + "="*80)
print("🔍 ANALYZING 100K POTENTIAL...")
print("="*80)

candidates = []

for t in tokens:
    mc = t['mc']
    v24h = t['v24h']
    
    # Range: 10k to 90k
    if 10000 < mc < 90000:
        multiplier = TARGET_MC / mc
        vol_ratio = v24h / mc if mc > 0 else 0
        
        # Score: lower multiplier = easier target
        score = (100 - (multiplier * 8)) + (vol_ratio * 15)
        score = min(max(score, 0), 100)
        
        candidates.append({
            **t,
            'multiplier': multiplier,
            'vol_ratio': vol_ratio,
            'score': score
        })

if candidates:
    # Sort
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🎯 {len(candidates)} TOKENS WITH 100K POTENTIAL:")
    print("-"*80)
    
    for i, c in enumerate(candidates[:15], 1):
        # Badge
        if c['mc'] >= 70000:
            badge = "🚀 CLOSE"
        elif c['mc'] >= 50000:
            badge = "⭐ GOOD"
        elif c['mc'] >= 30000:
            badge = "📈 WATCH"
        else:
            badge = "👀 EARLY"
        
        # Action
        if c['vol_ratio'] > 0.5:
            action = "💰 HIGH MOMENTUM"
        elif c['vol_ratio'] > 0.2:
            action = "⚡ MODERATE"
        else:
            action = "👀 LOW VOL"
        
        print(f"\n{i}. {c['symbol']}")
        print(f"   Current: ${c['mc']:,.0f} MC → Needs {c['multiplier']:.1f}x for 100k")
        print(f"   Volume: ${c['v24h']:,.0f} (Ratio: {c['vol_ratio']:.2f}) | {action}")
        print(f"   Score: {c['score']:.0f}/100 | {badge}")
        print(f"   CA: {c['address']}")
        print(f"   Dex: {c['dex']}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TALLY:")
    close_tier = len([c for c in candidates if c['mc'] >= 70000])
    mid_tier = len([c for c in candidates if 40000 <= c['mc'] < 70000])
    early_tier = len([c for c in candidates if c['mc'] < 40000])
    
    print(f"  Close (70k+): {close_tier}")
    print(f"  Mid (40k-70k): {mid_tier}")
    print(f"  Early (10k-40k): {early_tier}")
    print(f"  Total: {len(candidates)}")
    
    # Best 3
    if candidates:
        print("\n" + "="*80)
        print("🏆 TOP 3 PICKS:")
        print("="*80)
        for i, c in enumerate(candidates[:3], 1):
            risk = "LOW" if c['mc'] > 60000 else "MED" if c['mc'] > 40000 else "HIGH"
            print(f"{i}. {c['symbol']} - ${c['mc']:,.0f} MC | x{c['multiplier']:.1f} to 100k | Risk: {risk}")
            print(f"   CA: {c['address']}")
            
else:
    print("\n⚠️ No tokens found in 10k-90k MC range")
    print(f"\nTokens checked: {len(tokens)}")
    
    # Show distribution
    below_10k = len([t for t in tokens if t['mc'] > 0 and t['mc'] <= 10000])
    above_90k = len([t for t in tokens if t['mc'] >= 90000])
    
    print(f"  Below 10k MC: {below_10k}")
    print(f"  Above 90k MC: {above_90k}")

print("\n" + "="*80)
print("✅ Scan complete - Monitor these for breakout potential")
print("="*80)
