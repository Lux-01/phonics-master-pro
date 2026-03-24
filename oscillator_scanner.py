#!/usr/bin/env python3
"""
Oscillator Scanner v1.1
Finds coins that pump-then-drop repeatedly (range-bound oscillators)
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace')

from chart_analyzer import ChartAnalyzer
import requests
import json
from datetime import datetime
import time

def fetch_trending_from_birdeye():
    """Fetch trending tokens from Birdeye API"""
    print("📡 Fetching from Birdeye API...")
    
    # Use the working key
    api_key = "6335463fca7340f9a2c73eacd5a37f64"
    headers = {"X-API-KEY": api_key, "accept": "application/json"}
    
    try:
        # Use token list endpoint with offset/limit
        url = "https://public-api.birdeye.so/defi/tokenlist"
        params = {
            "sort_by": "v24hChangePercent",
            "sort_type": "desc",
            "offset": 0,
            "limit": 50
        }
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        tokens = data.get('data', {}).get('tokens', [])
        print(f"✅ Found {len(tokens)} tokens")
        
        # Filter for valid memecoins
        solana_tokens = []
        seen_cas = set()
        
        for token in tokens:
            ca = token.get('address', '')
            symbol = token.get('symbol', '?')
            name = token.get('name', '?')
            
            if not ca or ca in seen_cas:
                continue
            
            # Skip common tokens
            if symbol.upper() in ['SOL', 'WSOL', 'USDC', 'USDT', 'WETH', 'ETH', 'BTC', 'WBTC']:
                continue
            
            liq = float(token.get('liquidity', 0) or token.get('v24hUSD', 0) * 0.1 or 0)
            fdv = float(token.get('marketCap', 0) or 0)
            price = float(token.get('price', 0) or 0)
            
            # Filter: need liquidity and reasonable FDV
            if liq < 5000 or fdv > 100000000 or fdv < 10000:  # min $5k liq, max $100M FDV, min $10k FDV
                continue
            
            solana_tokens.append({
                'ca': ca,
                'symbol': symbol,
                'name': name,
                'liquidity': liq,
                'fdv': fdv if fdv > 0 else 1000000,
                'price': price
            })
            seen_cas.add(ca)
        
        print(f"📊 {len(solana_tokens)} valid tokens after filtering")
        return solana_tokens[:50]  # Return top 50
        
    except Exception as e:
        print(f"❌ Birdeye failed: {e}")
        return []

def fetch_trending_tokens_dexscreener():
    """Fetch trending Solana tokens from DexScreener search"""
    print("📡 Trying DexScreener search...")
    
    try:
        # Expanded search terms to get more tokens
        search_terms = [
            'solana', 'meme', 'memecoin', 'token', 'pump', 'ai', 
            'pepe', 'doge', 'shib', 'billion', 'moon', 'alpha',
            'based', 'squad', 'based', 'viral', 'fomo', 'ape'
        ]
        all_tokens = []
        seen_cas = set()
        
        for term in search_terms:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={term}"
                r = requests.get(url, timeout=15)
                if r.status_code != 200:
                    continue
                
                data = r.json()
                pairs = data.get('pairs', [])
                
                for pair in pairs:
                    if pair.get('chainId') != 'solana':
                        continue
                    
                    base_token = pair.get('baseToken', {})
                    ca = base_token.get('address', '')
                    symbol = base_token.get('symbol', '?')
                    name = base_token.get('name', '?')
                    
                    if not ca or ca in seen_cas:
                        continue
                    
                    # Skip common tokens
                    if symbol.upper() in ['SOL', 'WSOL', 'USDC', 'USDT', 'WETH', 'ETH', 'BTC', 'WBTC']:
                        continue
                    
                    liq = float(pair.get('liquidity', {}).get('usd', 0))
                    fdv = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 0)
                    price = float(pair.get('priceUsd', 0) or 0)
                    
                    # Broader filter: $1k+ liq, $10M max FDV
                    if liq < 1000 or fdv > 100000000 or fdv < 1000:
                        continue
                    
                    all_tokens.append({
                        'ca': ca,
                        'symbol': symbol,
                        'name': name,
                        'liquidity': liq,
                        'fdv': fdv if fdv > 0 else 1000000,
                        'price': price
                    })
                    seen_cas.add(ca)
                    
            except Exception as e:
                continue
        
        if all_tokens:
            print(f"✅ Found {len(all_tokens)} tokens from DexScreener")
            # Sort by liquidity
            all_tokens.sort(key=lambda x: x['liquidity'], reverse=True)
            return all_tokens[:100]  # Return top 100 instead of 30
            
    except Exception as e:
        print(f"❌ DexScreener search failed: {e}")
    
    return []

def fetch_popular_tokens_fallback():
    """Fallback: Use a curated list of popular Solana tokens"""
    print("📡 Using fallback token list...")
    
    # Curated list of known Solana tokens
    curated_tokens = [
        {"ca": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "symbol": "BONK", "name": "Bonk"},
        {"ca": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", "symbol": "BONK2", "name": "Bonk V2"},
        {"ca": "SHDWSC8V1DtmwnzXBMCR1k63m7YzVusjEi15yDqbNLs", "symbol": "DOGWIF", "name": "Dog Wif Coin"},
    ]
    
    tokens = []
    for token_info in curated_tokens:
        try:
            ca = token_info['ca']
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                pairs = data.get('pairs', [])
                if pairs:
                    pair = pairs[0]
                    liq = float(pair.get('liquidity', {}).get('usd', 0))
                    fdv = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 0)
                    price = float(pair.get('priceUsd', 0) or 0)
                    
                    if liq >= 5000 and fdv <= 100000000:
                        tokens.append({
                            'ca': ca,
                            'symbol': token_info['symbol'],
                            'name': token_info['name'],
                            'liquidity': liq,
                            'fdv': fdv if fdv > 0 else 1000000,
                            'price': price
                        })
        except:
            continue
    
    print(f"✅ Found {len(tokens)} tokens from fallback list")
    return tokens

def fetch_smallcaps_dexscreener():
    """Fetch small-cap tokens from DexScreener using expanded search"""
    print("📡 Scanning DexScreener for small-cap oscillators...")
    
    try:
        # Expanded search terms to find small-cap tokens
        search_terms = [
            'solana', 'meme', 'token', 'ai', 'pepe', 'doge', 
            'cat', 'frog', 'based', 'wojak', 'chad', 'moon',
            'pump', 'viral', 'alpha', 'degen', 'ape', 'coin'
        ]
        
        all_tokens = []
        seen_cas = set()
        
        for term in search_terms:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={term}"
                r = requests.get(url, timeout=15)
                if r.status_code != 200:
                    continue
                
                data = r.json()
                pairs = data.get('pairs', [])
                
                for pair in pairs:
                    if pair.get('chainId') != 'solana':
                        continue
                    
                    base_token = pair.get('baseToken', {})
                    ca = base_token.get('address', '')
                    symbol = base_token.get('symbol', '?')
                    name = base_token.get('name', '?')
                    
                    if not ca or ca in seen_cas:
                        continue
                    
                    # Skip common tokens
                    if symbol.upper() in ['SOL', 'WSOL', 'USDC', 'USDT', 'WETH', 'ETH', 'BTC']:
                        continue
                    
                    liq = float(pair.get('liquidity', {}).get('usd', 0))
                    fdv = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 0)
                    price = float(pair.get('priceUsd', 0) or 0)
                    
                    # STRICT FILTER: Small caps ONLY ($5k - $2M FDV)
                    if liq < 3000 or fdv > 2000000 or fdv < 5000:
                        continue
                    
                    all_tokens.append({
                        'ca': ca,
                        'symbol': symbol,
                        'name': name,
                        'liquidity': liq,
                        'fdv': fdv if fdv > 0 else 500000,
                        'price': price
                    })
                    seen_cas.add(ca)
                    
            except Exception as e:
                continue
        
        if all_tokens:
            print(f"✅ Found {len(all_tokens)} small-cap tokens ($5k-$2M FDV)")
            # Sort by liquidity (more liquidity = more tradable)
            all_tokens.sort(key=lambda x: x['liquidity'], reverse=True)
            return all_tokens[:100]
            
    except Exception as e:
        print(f"❌ DexScreener scan failed: {e}")
    
    return []

def fetch_tokens_from_dex():
    """Fetch trending tokens - try multiple sources"""
    
    # Use DexScreener small-cap scanner
    tokens = fetch_smallcaps_dexscreener()
    if tokens:
        return tokens
    
    # Fallback to DexScreener search
    return fetch_trending_tokens_dexscreener()

def scan_oscillators():
    """Main scan function"""
    print("\n" + "=" * 70)
    print("🔄 OSCILLATOR SCANNER v1.1")
    print("=" * 70)
    print()
    
    tokens = fetch_tokens_from_dex()
    if not tokens:
        print("❌ No tokens fetched")
        return []
    
    print()
    print(f"🔍 Analyzing {min(100, len(tokens))} charts...")
    print("-" * 70)
    
    oscillators = []
    analyzer = ChartAnalyzer(timeframe='15m')
    
    for i, token in enumerate(tokens[:100], 1):
        ca = token['ca']
        symbol = token['symbol']
        name = token['name']
        
        print(f"\n[{i}/{min(100, len(tokens))}] {symbol} - {name[:30]}")
        print(f"       Liq: ${token['liquidity']/1000:.1f}k | FDV: ${token['fdv']/1000000:.2f}M")
        
        try:
            signals, chart_score, analysis = analyzer.analyze_token_chart(ca)
            
            if signals.oscillator_detected:
                osc_score = signals.oscillator_score
                print(f"   ├─ OSCILLATOR! Score: {osc_score}/10")
                print(f"   ├─ Range: {signals.range_pct:.1f}% | {signals.sr_touches} S/R touches")
                print(f"   ├─ RSI: {signals.rsi} | Trend: {signals.trend}")
                
                if osc_score >= 5:
                    oscillators.append({
                        'name': name,
                        'symbol': symbol,
                        'ca': ca,
                        'liquidity': token['liquidity'],
                        'fdv': token['fdv'],
                        'range_pct': signals.range_pct,
                        'oscillator_score': osc_score,
                        'sr_touches': signals.sr_touches,
                        'rsi': signals.rsi,
                        'trend': signals.trend,
                        'support': signals.support,
                        'resistance': signals.resistance,
                        'chart_score': chart_score,
                        'price': token['price']
                    })
                    print(f"   └─ ✅ SAVED (Score >= 5)")
                else:
                    print(f"   └─ Score too low ({osc_score} < 5)")
            else:
                print(f"   └─ Not oscillating (Score: {signals.oscillator_score})")
            
            # Rate limiting delay to avoid 429 errors (3s for Birdeye free tier)
            time.sleep(3.0)
                
        except Exception as e:
            print(f"   └─ ⚠️ Error: {str(e)[:50]}")
    
    # Sort by oscillator score
    oscillators.sort(key=lambda x: x['oscillator_score'], reverse=True)
    return oscillators

def display_results(oscillators):
    """Display results"""
    print()
    print("=" * 80)
    print("🔄 TOP OSCILLATORS")
    print("=" * 80)
    
    if not oscillators:
        print("\n❌ No oscillators found")
        return
    
    print()
    print(f"{'#':<3} {'Token':<10} {'Range':<8} {'Score':<6} {'RSI':<6} {'Action'}")
    print("-" * 80)
    
    for i, osc in enumerate(oscillators, 1):
        symbol = osc['symbol'][:9]
        range_pct = osc['range_pct']
        score = osc['oscillator_score']
        rsi = osc['rsi']
        
        if osc['rsi'] < 35:
            action = "🟢 BUY"
        elif osc['rsi'] > 65:
            action = "🔴 SELL"
        else:
            action = "🟡 WAIT"
        
        print(f"{i:<3} {symbol:<10} {range_pct:>6.1f}% {score:>4}   {rsi:>5.1f}  {action}")
    
    print()
    print("-" * 80)
    
    # Detail view for top 3
    print("\n🎯 TOP 3 DETAILS:")
    print("-" * 60)
    
    for pick in oscillators[:3]:
        print(f"\n  {pick['symbol']} ({pick['name'][:20]})")
        print(f"  CA: {pick['ca']}")
        print(f"  Score: {pick['oscillator_score']}/10 | Range: {pick['range_pct']:.1f}% | {pick['sr_touches']} touches")
        print(f"  RSI: {pick['rsi']:.1f} | Trend: {pick['trend']}")
        if pick['support']:
            print(f"  Support: ${min(pick['support']):.10f}")
        if pick['resistance']:
            print(f"  Resistance: ${min(pick['resistance']):.10f}")
        print(f"  Price: ${pick['price']:.10f}")
        
        # Strategy
        print()
        if pick['rsi'] < 35:
            print("  📉 OVERSOLD - Consider buying near support")
        elif pick['rsi'] > 65:
            print("  📈 OVERBOUGHT - Consider taking profits")
        else:
            print("  ⏳ MID-RANGE - Wait for better entry")

def save_results(oscillators):
    """Save results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'/home/skux/.openclaw/workspace/oscillator_results_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'oscillator_count': len(oscillators),
            'oscillators': oscillators
        }, f, indent=2)
    
    return filename

def main():
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "🔄 OSCILLATOR SCANNER v1.1" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    
    oscillators = scan_oscillators()
    display_results(oscillators)
    
    if oscillators:
        filename = save_results(oscillators)
        print()
        print("=" * 80)
        print("💾 Saved:", filename)
        print("\n📋 MEAN REVERSION STRATEGY:")
        print("   1. Buy near support when RSI < 40")
        print("   2. TP at middle of range or resistance")
        print("   3. SL: 7% below support")
        print("   4. Time stop: 2 hours max")
        print("=" * 80)
    else:
        print("\n❌ No oscillators found. Market may be trending strongly.")

if __name__ == "__main__":
    main()
