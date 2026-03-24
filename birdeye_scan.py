#!/usr/bin/env python3
"""Find tokens using Birdeye API"""

import requests
import json
import time
from datetime import datetime

print('🔍 SCANNING - Birdeye API Latest Tokens')
print('=' * 70)

# Try multiple endpoints
API_KEY = '6335463fca7340f9a2c73eacd5a37f64'
headers = {'X-API-KEY': API_KEY}

# Get trending
try:
    print('Fetching trending tokens...')
    url = 'https://public-api.birdeye.so/defi/tokenlist?sort_by=v24hChangePercent&sort_type=desc&offset=0&limit=20'
    r = requests.get(url, headers=headers, timeout=30)
    
    if r.status_code == 200:
        data = r.json()
        if data.get('success') and data.get('data'):
            tokens = data['data']
            print(f'Found {len(tokens)} tokens with volume\n')
            print('-' * 70)
            
            opportunities = []
            
            for t in tokens:
                try:
                    symbol = t.get('symbol', 'N/A')
                    address = t.get('address', '')
                    mcap = float(t.get('marketCap', 0) or 0)
                    price = float(t.get('price', 0) or 0)
                    v24h = float(t.get('v24h', 0) or 0)
                    v24h_change = float(t.get('v24hChangePercent', 0) or 0)
                    holders = int(t.get('holder', 0) or 0)
                    
                    # Quick filter
                    if mcap < 10000 or mcap > 500000:
                        continue
                    
                    opportunities.append({
                        'symbol': symbol,
                        'address': address,
                        'mcap': mcap,
                        'price': price,
                        'v24h': v24h,
                        'v24h_change': v24h_change,
                        'holders': holders
                    })
                except:
                    pass
            
            print(f'\n{len(opportunities)} tokens in 10K-500K range:\n')
            
            for opp in opportunities[:10]:
                print(f"Token: {opp['symbol']}")
                print(f"  MC: ${opp['mcap']:,.0f} | Holders: {opp['holders']}")
                print(f"  24h Vol: ${opp['v24h']:,.0f} ({opp['v24h_change']:+.1f}%)")
                print(f"  Price: ${opp['price']:.8f}")
                print()
        else:
            print('No tokens returned from API')
    else:
        print(f'Birdeye API error: {r.status_code}')
        print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

print()
print('Alternative: Load from cached signals...')
