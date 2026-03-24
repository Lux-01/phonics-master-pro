#!/bin/bash
# Trading Signal Generator for Tem
# Runs scanner and filters for Grade A opportunities
# Sends signals via Telegram

cd /home/skux/.openclaw/workspace

echo "🔍 Scanning for trading signals..."

# Run v5.4 scanner
bash run_v54_combined.sh > /tmp/scan_output.txt 2>&1

# Check results
if [ -f alpha_results_v54.json ]; then
    # Parse results and filter for best opportunities
    python3 << 'PYTHON'
import json
import sys

try:
    with open('alpha_results_v54.json', 'r') as f:
        tokens = json.load(f)
    
    signals = []
    
    for token in tokens:
        # Filter criteria
        age = token.get('age_hours', 0)
        top10 = token.get('top10_pct', 100)
        grade = token.get('grade', 'F')
        score = token.get('score', 0)
        mcap = token.get('mcap', 0)
        liq = token.get('liq', 0)
        
        # STRICT filters (post-rug lesson)
        if age < 2:
            continue  # Skip tokens < 2 hours old
        if top10 > 50:
            continue  # Skip whale concentration > 50%
        if 'A' not in grade:
            continue  # Only Grade A
        if mcap < 20000 or mcap > 500000:
            continue  # MCAP range $20K-$500K
        if liq < 10000:
            continue  # Min $10K liquidity
            
        # Calculate signal strength
        strength = "WEAK"
        if score >= 16 and age >= 6 and top10 < 35:
            strength = "STRONG"
        elif score >= 15 and age >= 3:
            strength = "MODERATE"
        
        signals.append({
            'name': token.get('name', '?'),
            'symbol': token.get('symbol', '?'),
            'ca': token['ca'],
            'mcap': mcap,
            'age': age,
            'top10': top10,
            'score': score,
            'grade': grade,
            'strength': strength,
            'liq': liq,
            'vol24': token.get('vol24', 0)
        })
    
    # Sort by score descending
    signals.sort(key=lambda x: x['score'], reverse=True)
    
    # Output for Telegram
    if signals:
        print("🎯 TRADING SIGNALS FOUND\n")
        print("=" * 50)
        
        for i, sig in enumerate(signals[:3], 1):  # Top 3 only
            emoji = "🔥" if sig['strength'] == "STRONG" else "✅" if sig['strength'] == "MODERATE" else "⚠️"
            print(f"\n{emoji} SIGNAL #{i}: {sig['name']} ({sig['symbol']})")
            print(f"Strength: {sig['strength']}")
            print(f"Grade: {sig['grade']} | Score: {sig['score']}")
            print(f"Age: {sig['age']:.1f}h | Top 10%: {sig['top10']:.1f}%")
            print(f"MCAP: ${sig['mcap']:,} | Liq: ${sig['liq']:,}")
            print(f"Volume 24h: ${sig['vol24']:,}")
            print(f"\nCA: `{sig['ca']}`")
            print(f"\nEntry: 0.02 SOL (LuxTrader)")
            print(f"Target: +15% | Stop: -7%")
            print(f"Time Stop: 4 hours")
            print("-" * 50)
    else:
        print("⚠️ No signals meeting criteria")
        print("\nFilters applied:")
        print("- Age: > 2 hours")
        print("- Top 10%: < 50%")
        print("- Grade: A only")
        print("- MCAP: $20K-$500K")
        print("- Liquidity: > $10K")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
PYTHON
else
    echo "❌ Scan failed - no results file"
fi
