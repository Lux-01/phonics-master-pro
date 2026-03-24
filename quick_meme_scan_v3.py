#!/usr/bin/env python3
"""
🔥 Quick Meme Coin Scanner v3
Relaxed filters for more candidates
"""

import requests
import json
from datetime import datetime

def get_dexscreener_trending():
    """Get trending from DexScreener"""
    print("🔍 Scanning DexScreener...")
    
    try:
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            solana_tokens = [t for t in data if t.get('chainId') == 'solana']
            print(f"   Found {len(solana_tokens)} Solana tokens")
            return solana_tokens[:25]
    except Exception as e:
        print(f"   Error: {e}")
    
    return []

def get_token_info(address):
    """Get detailed token info"""
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{address}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    print("="*70)
    print("🚀 MEME COIN SCANNER v3")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    tokens = get_dexscreener_trending()
    
    if not tokens:
        print("\n❌ No tokens found")
        return None
    
    print("\n🎯 Analyzing...")
    
    candidates = []
    
    for token in tokens:
        symbol = token.get('symbol', '')
        name = token.get('name', '')
        address = token.get('tokenAddress', '')
        
        # Skip majors
        if symbol in ['USDC', 'USDT', 'SOL', 'BTC', 'ETH', 'BONK', 'WIF', 'JUP']:
            continue
        
        # Get detailed info
        info = get_token_info(address)
        if info and len(info) > 0:
            pair = info[0]
            liquidity = pair.get('liquidity', {}).get('usd', 0) or 0
            volume = pair.get('volume', {}).get('h24', 0) or 0
            price = pair.get('priceUsd', 0) or 0
            
            # RELAXED: $10k+ liquidity, any volume
            if liquidity >= 10000:
                candidates.append({
                    'symbol': symbol,
                    'name': name,
                    'address': address,
                    'price': float(price) if price else 0,
                    'liquidity': liquidity,
                    'volume_24h': volume,
                    'score': liquidity / 10000 + volume / 1000
                })
    
    if not candidates:
        print("\n❌ No candidates found")
        return None
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n📊 Top 5 Candidates:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"   {i}. {c['symbol']} - ${c['price']:.8f} | Liq: ${c['liquidity']:,.0f} | Vol: ${c['volume_24h']:,.0f}")
    
    # Pick top one
    selected = candidates[0]
    
    print(f"\n" + "="*70)
    print(f"🎯 SELECTED: {selected['symbol']}")
    print(f"="*70)
    print(f"   Name: {selected['name']}")
    print(f"   Address: {selected['address']}")
    print(f"   Price: ${selected['price']:.8f}")
    print(f"   Liquidity: ${selected['liquidity']:,.0f}")
    print(f"   Volume 24h: ${selected['volume_24h']:,.0f}")
    
    # Save
    with open('/tmp/meme_coin_pick.json', 'w') as f:
        json.dump(selected, f, indent=2)
    
    return selected

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✅ Ready to trade {result['symbol']}!")
    else:
        print("\n❌ Scan failed")
