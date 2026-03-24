#!/usr/bin/env python3
"""
🔥 Quick Meme Coin Scanner v2
Using DexScreener API
"""

import requests
import json
from datetime import datetime

def get_dexscreener_trending():
    """Get trending from DexScreener"""
    print("🔍 Scanning DexScreener trending...")
    
    try:
        # Get Solana trending
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter for Solana tokens
            solana_tokens = [t for t in data if t.get('chainId') == 'solana']
            print(f"   Found {len(solana_tokens)} Solana tokens")
            return solana_tokens[:15]
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
    print("🚀 QUICK MEME COIN SCANNER v2")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Get trending tokens
    tokens = get_dexscreener_trending()
    
    if not tokens:
        print("\n❌ No tokens found from DexScreener")
        # Fallback: use a known working token for testing
        print("\n⚠️ Using fallback test token...")
        return None
    
    print("\n🎯 Analyzing tokens...")
    
    candidates = []
    
    for token in tokens:
        symbol = token.get('symbol', '')
        name = token.get('name', '')
        address = token.get('tokenAddress', '')
        
        # Skip major tokens
        if symbol in ['USDC', 'USDT', 'SOL', 'BTC', 'ETH', 'BONK']:
            continue
        
        # Get detailed info
        info = get_token_info(address)
        if info and len(info) > 0:
            pair = info[0]
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            volume = pair.get('volume', {}).get('h24', 0)
            price = pair.get('priceUsd', 0)
            
            # Filter criteria
            if liquidity > 50000 and volume > 10000:
                candidates.append({
                    'symbol': symbol,
                    'name': name,
                    'address': address,
                    'price': float(price) if price else 0,
                    'liquidity': liquidity,
                    'volume_24h': volume,
                    'score': liquidity / 100000 + volume / 10000
                })
    
    if not candidates:
        print("\n❌ No suitable candidates")
        return None
    
    # Sort by score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n📊 Top Candidates:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"   {i}. {c['symbol']} - ${c['price']:.8f} | Liq: ${c['liquidity']:,.0f}")
    
    # Pick top one
    selected = candidates[0]
    
    print(f"\n🎯 SELECTED: {selected['symbol']}")
    print(f"   Address: {selected['address']}")
    print(f"   Price: ${selected['price']:.8f}")
    print(f"   Liquidity: ${selected['liquidity']:,.0f}")
    
    # Save
    with open('/tmp/meme_coin_pick.json', 'w') as f:
        json.dump(selected, f, indent=2)
    
    return selected

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✅ Ready to trade: {result['symbol']}")
    else:
        print("\n❌ Scan failed")
