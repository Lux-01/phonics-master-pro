#!/usr/bin/env python3
"""
Full 100-token oscillator scan with results
"""
from chart_analyzer import ChartAnalyzer
import requests
import time
import json
from datetime import datetime

print('='*70)
print('🔄 OSCILLATOR SCANNER - FULL 100 TOKEN SCAN')
print('='*70)
print()

# Get tokens from expanded search
search_terms = ['solana', 'meme', 'token', 'pump', 'ai', 'pepe', 'doge', 'moon']
all_tokens = []
seen_cas = set()

for term in search_terms:
    try:
        url = f'https://api.dexscreener.com/latest/dex/search?q={term}'
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
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
                if symbol.upper() in ['SOL', 'WSOL', 'USDC', 'USDT', 'WETH', 'ETH', 'BTC']:
                    continue
                liq = float(pair.get('liquidity', {}).get('usd', 0))
                fdv = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 0)
                if liq >= 1000 and fdv <= 50000000:
                    all_tokens.append({'ca': ca, 'symbol': symbol, 'name': name, 'liquidity': liq, 'fdv': fdv})
                    seen_cas.add(ca)
    except:
        pass

print(f'📊 Found {len(all_tokens)} unique tokens')
print(f'🔍 Analyzing top {min(100, len(all_tokens))} with 3s delays...')
print('-'*70)

analyzer = ChartAnalyzer(timeframe='15m')
oscillators = []

for i, token in enumerate(all_tokens[:100], 1):
    print(f'\n[{i}/{min(100, len(all_tokens))}] {token["symbol"]} - {token["name"][:25]}')
    print(f'       Liq: ${token["liquidity"]/1000:.1f}k | FDV: ${token["fdv"]/1000000:.2f}M')
    
    try:
        signals, chart_score, analysis = analyzer.analyze_token_chart(token['ca'])
        
        if signals.oscillator_detected:
            print(f'   ├─ 🔄 OSCILLATOR! Score: {signals.oscillator_score}/10')
            print(f'   ├─ Range: {signals.range_pct:.1f}% | {signals.sr_touches} S/R touches')
            print(f'   ├─ RSI: {signals.rsi} | Trend: {signals.trend}')
            
            if signals.oscillator_score >= 5:
                oscillators.append({
                    'name': token['name'],
                    'symbol': token['symbol'],
                    'ca': token['ca'],
                    'liquidity': token['liquidity'],
                    'fdv': token['fdv'],
                    'range_pct': signals.range_pct,
                    'oscillator_score': signals.oscillator_score,
                    'sr_touches': signals.sr_touches,
                    'rsi': signals.rsi,
                    'trend': signals.trend,
                    'support': signals.support,
                    'resistance': signals.resistance,
                    'chart_score': chart_score
                })
                print(f'   └─ ✅ SAVED (Score >= 5)')
            else:
                print(f'   └─ Score too low ({signals.oscillator_score} < 5)')
        else:
            print(f'   └─ Not oscillating (Score: {signals.oscillator_score})')
            
    except Exception as e:
        print(f'   └─ ⚠️ Error: {str(e)[:50]}')
    
    # 3 second rate limit delay
    if i < min(100, len(all_tokens)):
        time.sleep(3.0)

# Sort and display results
oscillators.sort(key=lambda x: x['oscillator_score'], reverse=True)

print()
print('='*80)
print('🔄 TOP OSCILLATORS')
print('='*80)

if not oscillators:
    print('\n❌ No oscillators found in 100 tokens scanned')
else:
    print(f'\n✅ Found {len(oscillators)} oscillators!')
    print()
    print(f"{'#':<4} {'Token':<12} {'Range':<8} {'Score':<6} {'RSI':<6} {'Action'}")
    print('-'*80)
    
    for i, osc in enumerate(oscillators[:20], 1):
        symbol = osc['symbol'][:11]
        range_pct = osc['range_pct']
        score = osc['oscillator_score']
        rsi = osc['rsi']
        
        if rsi < 35:
            action = '🟢 BUY'
        elif rsi > 65:
            action = '🔴 SELL'
        else:
            action = '🟡 WAIT'
        
        print(f"{i:<4} {symbol:<12} {range_pct:>6.1f}% {score:>4}   {rsi:>5.1f}  {action}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'/home/skux/.openclaw/workspace/oscillator_results_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_scanned': min(100, len(all_tokens)),
            'oscillator_count': len(oscillators),
            'oscillators': oscillators
        }, f, indent=2)
    
    print(f'\n💾 Saved to: {filename}')

print()
print('='*80)
print('📋 NEXT STEP: Alternative data sources')
print('='*80)
print('DexScreener search only finds trending tokens.')
print('Alternatives for finding range-bound tokens:')
print('  1. Check v5.5 daily results for multi-day patterns')
print('  2. Use CoinGecko /coins/markets with price_change filters')
print('  3. Query tokens with 0-5% 24h change (sideways action)')
print('  4. Dune Analytics: sideways-moving Solana tokens query')
print('  5. Helius: scan for tokens with low volatility in last N blocks')
print()
