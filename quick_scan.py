#!/usr/bin/env python3
"""Quick scanner using DexScreener API"""

import requests
import json
from datetime import datetime

print('🔍 SCANNING FOR TOKENS - Using DexScreener API')
print('=' * 70)

# DexScreener API - get trending pairs
try:
    url = 'https://api.dexscreener.com/latest/dex/search?q=USDC'
    r = requests.get(url, timeout=30)
    
    if r.status_code == 200:
        data = r.json()
        pairs = data.get('pairs', [])
        
        print(f'Found {len(pairs)} pairs with USDC liquidity\n')
        print('Scanning for high-opportunity tokens...\n')
        
        opportunities = []
        
        for pair in pairs[:50]:
            base = pair.get('baseToken', {})
            quote = pair.get('quoteToken', {})
            liquidity = pair.get('liquidity', {})
            volume = pair.get('volume', {})
            price_change = pair.get('priceChange', {})
            
            symbol = base.get('symbol', 'N/A')
            try:
                mcap = float(pair.get('fdv', 0)) or float(pair.get('marketCap', 0))
            except:
                mcap = 0
            try:
                liq = float(liquidity.get('usd', 0))
            except:
                liq = 0
            try:
                vol_24h = float(volume.get('h24', 0))
            except:
                vol_24h = 0
                
            if mcap == 0 or liq == 0:
                continue
                
            if mcap < 15000 or mcap > 500000:
                continue
                
            if liq < 10000:
                continue
                
            h24 = price_change.get('h24', '0')
            try:
                change_24h = float(h24)
            except:
                change_24h = 0
            
            liq_ratio = liq / mcap if mcap > 0 else 0
            vol_ratio = vol_24h / mcap if mcap > 0 else 0
            
            score = 0
            grade = 'C'
            
            if 15000 <= mcap <= 100000:
                score += 20
            if liq >= 10000:
                score += 25
            if liq_ratio >= 0.3:
                score += 20
            if vol_ratio >= 0.1:
                score += 15
            if abs(change_24h) < 50:
                score += 10
            if 4 <= (datetime.now().hour - pair.get('pairCreatedAt', datetime.now().hour)) <= 24:
                score += 10
            
            if score >= 90:
                grade = 'A+'
            elif score >= 75:
                grade = 'A'
            elif score >= 60:
                grade = 'A-'
            elif score >= 50:
                grade = 'B'
            
            if grade in ['A', 'A+', 'A-']:
                opportunities.append({
                    'symbol': symbol,
                    'name': base.get('name', 'Unknown'),
                    'address': base.get('address', ''),
                    'mcap': mcap,
                    'liquidity': liq,
                    'liq_ratio': liq_ratio,
                    'vol_24h': vol_24h,
                    'vol_ratio': vol_ratio,
                    'price': pair.get('priceUsd', 0),
                    'change_24h': change_24h,
                    'score': score,
                    'grade': grade
                })
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        print(f'Found {len(opportunities)} Grade A/A+ opportunities\n')
        print('-' * 70)
        
        for opp in opportunities[:5]:
            print()
            print(f"Token: {opp['symbol']} - Grade {opp['grade']} (Score: {opp['score']})")
            print(f"  Address: {opp['address'][:50]}...")
            print(f"  Market Cap: ${opp['mcap']:,.0f}")
            print(f"  Liquidity: ${opp['liquidity']:,.0f} ({opp['liq_ratio']*100:.0f}% ratio)")
            print(f"  24h Volume: ${opp['vol_24h']:,.0f}")
            print(f"  24h Change: {opp['change_24h']:+.1f}%")
            print(f"  Price: ${float(opp['price']):.8f}")
        
        if len(opportunities) == 0:
            print('No Grade A tokens found in current data.')
    else:
        print(f'API Error: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')
