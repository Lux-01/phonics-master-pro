#!/usr/bin/env python3
"""
🔥 Quick Meme Coin Scanner
Fast scan to find 1 tradeable meme coin
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace')

import asyncio
import json
import requests
from datetime import datetime

# APIs
BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"
JUPITER_API = "https://lite-api.jup.ag/swap/v1"

def get_trending_tokens():
    """Get trending tokens from Birdeye"""
    print("🔍 Scanning trending tokens...")
    
    try:
        # Get trending tokens
        url = "https://public-api.birdeye.so/defi/token_trending"
        headers = {"X-API-KEY": BIRDEYE_KEY}
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('data', {}).get('tokens', [])
            
            print(f"   Found {len(tokens)} trending tokens")
            return tokens[:20]  # Top 20
    except Exception as e:
        print(f"   Error: {e}")
    
    return []

def filter_meme_coins(tokens):
    """Filter for meme coins with good liquidity"""
    print("\n🎯 Filtering for meme coins...")
    
    candidates = []
    
    for token in tokens:
        symbol = token.get('symbol', '')
        name = token.get('name', '')
        address = token.get('address', '')
        price = token.get('price', 0)
        volume_24h = token.get('volume24h', 0)
        liquidity = token.get('liquidity', 0)
        
        # Skip stablecoins and major tokens
        if symbol in ['USDC', 'USDT', 'SOL', 'BTC', 'ETH', 'BONK', 'WIF']:
            continue
        
        # Look for meme indicators
        is_meme = any([
            'meme' in name.lower(),
            'dog' in name.lower(),
            'cat' in name.lower(),
            'pepe' in name.lower(),
            'moon' in name.lower(),
            'elon' in name.lower(),
            'shib' in symbol.lower(),
            'inu' in symbol.lower(),
            'ai' in symbol.lower(),
            price < 0.01,  # Low price = potential meme
        ])
        
        # Need minimum liquidity
        if liquidity < 50000:  # $50k min
            continue
        
        if is_meme and liquidity > 50000:
            candidates.append({
                'symbol': symbol,
                'name': name,
                'address': address,
                'price': price,
                'liquidity': liquidity,
                'volume_24h': volume_24h,
                'score': liquidity / 1000000 + volume_24h / 100000
            })
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"   Found {len(candidates)} meme coin candidates")
    return candidates

def check_token_safety(token_address):
    """Quick safety check"""
    try:
        url = f"https://public-api.birdeye.so/defi/token_security?address={token_address}"
        headers = {"X-API-KEY": BIRDEYE_KEY}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            is_honeypot = data.get('isHoneypot', False)
            sell_tax = data.get('sellTax', 0)
            
            return {
                'safe': not is_honeypot and sell_tax < 10,
                'is_honeypot': is_honeypot,
                'sell_tax': sell_tax
            }
    except:
        pass
    
    return {'safe': False, 'error': 'Check failed'}

def main():
    print("="*70)
    print("🚀 QUICK MEME COIN SCANNER")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Get trending tokens
    tokens = get_trending_tokens()
    
    if not tokens:
        print("\n❌ No tokens found")
        return None
    
    # Filter for meme coins
    candidates = filter_meme_coins(tokens)
    
    if not candidates:
        print("\n❌ No meme coin candidates found")
        return None
    
    # Check top 3 for safety
    print("\n🔒 Safety checking top candidates...")
    
    for candidate in candidates[:3]:
        print(f"\n   Checking {candidate['symbol']}...")
        safety = check_token_safety(candidate['address'])
        
        if safety.get('safe'):
            print(f"   ✅ SAFE - {candidate['symbol']}")
            print(f"      Price: ${candidate['price']:.8f}")
            print(f"      Liquidity: ${candidate['liquidity']:,.0f}")
            print(f"      Volume 24h: ${candidate['volume_24h']:,.0f}")
            
            # Save to file
            with open('/tmp/meme_coin_pick.json', 'w') as f:
                json.dump(candidate, f, indent=2)
            
            print(f"\n🎯 SELECTED: {candidate['symbol']}")
            print(f"   Address: {candidate['address']}")
            return candidate
        else:
            print(f"   ❌ Unsafe - {safety}")
    
    print("\n⚠️ No safe meme coins found")
    return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✅ Ready to trade: {result['symbol']}")
    else:
        print("\n❌ Scan failed")
