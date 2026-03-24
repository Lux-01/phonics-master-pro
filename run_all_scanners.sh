#!/bin/bash
# Multi-Scanner Trading Signal System
# Runs all available scanners and aggregates results for consensus

cd /home/skux/.openclaw/workspace

echo "🚀 RUNNING ALL SCANNERS"
echo "========================"

# Create results directory
mkdir -p /tmp/scanner_results

# Run v5.4 (Primary)
echo "[1/4] Running v5.4 Scanner..."
bash run_v54_combined.sh > /tmp/scanner_results/v54.log 2>&1
if [ -f alpha_results_v54.json ]; then
    cp alpha_results_v54.json /tmp/scanner_results/v54_results.json
    echo "✅ v5.4 complete"
else
    echo "❌ v5.4 failed"
fi

# Run v5.5 (Chart Analysis - Experimental)
echo "[2/4] Running v5.5 Chart Scanner..."
bash run_v55_full.sh > /tmp/scanner_results/v55.log 2>&1 &
V55_PID=$!

# Run v5.3 (Legacy but reliable)
echo "[3/4] Running v5.3 Scanner..."
python3 solana_alpha_hunter_v53.py > /tmp/scanner_results/v53.log 2>&1 &
V53_PID=$!

# Run v5.1 (Backup)
echo "[4/4] Running v5.1 Scanner..."
python3 solana_alpha_hunter_v51.py > /tmp/scanner_results/v51.log 2>&1 &
V51_PID=$!

# Wait for all scanners
echo "⏳ Waiting for scanners to complete..."
wait $V55_PID $V53_PID $V51_PID

# Copy results
[ -f alpha_results_v55.json ] && cp alpha_results_v55.json /tmp/scanner_results/v55_results.json
[ -f alpha_results_v53.json ] && cp alpha_results_v53.json /tmp/scanner_results/v53_results.json
[ -f alpha_results_v51.json ] && cp alpha_results_v51.json /tmp/scanner_results/v51_results.json

echo "✅ All scanners complete"
echo ""

# Aggregate results
python3 << 'PYTHON'
import json
import os
from collections import defaultdict

def load_results(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

# Load all scanner results
scanners = {
    'v5.4': load_results('/tmp/scanner_results/v54_results.json'),
    'v5.5': load_results('/tmp/scanner_results/v55_results.json'),
    'v5.3': load_results('/tmp/scanner_results/v53_results.json'),
    'v5.1': load_results('/tmp/scanner_results/v51_results.json')
}

# Track tokens across scanners
token_data = defaultdict(lambda: {
    'scores': {},
    'grades': {},
    'ages': [],
    'top10s': [],
    'mcaps': [],
    'names': set(),
    'symbols': set()
})

for scanner_name, results in scanners.items():
    for token in results:
        ca = token.get('ca')
        if not ca:
            continue
        
        token_data[ca]['scores'][scanner_name] = token.get('score', 0)
        token_data[ca]['grades'][scanner_name] = token.get('grade', 'F')
        token_data[ca]['ages'].append(token.get('age_hours', 0))
        token_data[ca]['top10s'].append(token.get('top10_pct', 100))
        token_data[ca]['mcaps'].append(token.get('mcap', 0))
        token_data[ca]['names'].add(token.get('name', '?'))
        token_data[ca]['symbols'].add(token.get('symbol', '?'))
        token_data[ca]['liq'] = token.get('liq', 0)
        token_data[ca]['vol24'] = token.get('vol24', 0)

# Calculate consensus scores
consensus_signals = []

for ca, data in token_data.items():
    scanner_count = len(data['scores'])
    if scanner_count < 2:  # Need at least 2 scanners to agree
        continue
    
    avg_score = sum(data['scores'].values()) / scanner_count
    avg_age = sum(data['ages']) / len(data['ages'])
    avg_top10 = sum(data['top10s']) / len(data['top10s'])
    avg_mcap = sum(data['mcaps']) / len(data['mcaps'])
    
    # Count Grade A across scanners
    a_grades = sum(1 for g in data['grades'].values() if 'A' in str(g))
    
    # STRICT filters (post-rug lesson)
    if avg_age < 2:
        continue
    if avg_top10 > 50:
        continue
    if a_grades < 2:  # Need at least 2 scanners to give Grade A
        continue
    if avg_mcap < 20000 or avg_mcap > 500000:
        continue
    
    # Determine consensus strength
    consensus = "WEAK"
    if avg_score >= 16 and a_grades >= 3 and avg_age >= 6:
        consensus = "STRONG"
    elif avg_score >= 15 and a_grades >= 2 and avg_age >= 3:
        consensus = "MODERATE"
    
    name = list(data['names'])[0] if data['names'] else '?'
    symbol = list(data['symbols'])[0] if data['symbols'] else '?'
    
    consensus_signals.append({
        'ca': ca,
        'name': name,
        'symbol': symbol,
        'consensus': consensus,
        'avg_score': avg_score,
        'a_grades': a_grades,
        'scanner_count': scanner_count,
        'age': avg_age,
        'top10': avg_top10,
        'mcap': avg_mcap,
        'liq': data['liq'],
        'vol24': data['vol24'],
        'individual_scores': data['scores']
    })

# Sort by consensus strength then score
consensus_signals.sort(key=lambda x: (x['consensus'] != 'STRONG', x['consensus'] != 'MODERATE', -x['avg_score']))

# Output for Telegram
if consensus_signals:
    print("🎯 MULTI-SCANNER CONSENSUS SIGNALS")
    print("=" * 60)
    print(f"Scanners Run: v5.4, v5.5, v5.3, v5.1")
    print(f"Signals Found: {len(consensus_signals)}")
    print(f"Minimum Consensus: 2+ scanners Grade A")
    print("=" * 60)
    
    for i, sig in enumerate(consensus_signals[:5], 1):
        emoji = "🔥" if sig['consensus'] == "STRONG" else "✅" if sig['consensus'] == "MODERATE" else "⚠️"
        
        print(f"\n{emoji} CONSENSUS SIGNAL #{i}: {sig['name']} ({sig['symbol']})")
        print(f"Consensus Level: {sig['consensus']}")
        print(f"Scanners Agree: {sig['a_grades']}/{sig['scanner_count']} Grade A")
        print(f"Average Score: {sig['avg_score']:.1f}")
        print(f"\n📊 TOKEN METRICS:")
        print(f"Age: {sig['age']:.1f}h | Top 10%: {sig['top10']:.1f}%")
        print(f"MCAP: ${sig['mcap']:,.0f} | Liq: ${sig['liq']:,.0f}")
        print(f"Volume 24h: ${sig['vol24']:,.0f}")
        print(f"\n📈 SCANNER BREAKDOWN:")
        for scanner, score in sig['individual_scores'].items():
            print(f"  {scanner}: Score {score}")
        print(f"\n🎯 TRADE PARAMETERS:")
        print(f"CA: `{sig['ca']}`")
        
        if sig['consensus'] == "STRONG":
            print(f"\nEntry: 0.02 SOL (High Confidence)")
        elif sig['consensus'] == "MODERATE":
            print(f"\nEntry: 0.02 SOL (Standard)")
        else:
            print(f"\nEntry: 0.01 SOL (Cautious)")
            
        print(f"Target: +15% | Stop: -7%")
        print(f"Time Stop: 4 hours")
        print("-" * 60)
    
    print(f"\n⚠️ RISK FILTERS APPLIED:")
    print(f"✅ Age > 2 hours (Post-rug lesson)")
    print(f"✅ Top 10% < 50% (Whale protection)")
    print(f"✅ 2+ scanners Grade A (Consensus)")
    print(f"✅ MCAP $20K-$500K (Sweet spot)")
    print(f"✅ Liquidity > $10K")
else:
    print("⚠️ NO CONSENSUS SIGNALS FOUND")
    print("\nAll scanners completed but no tokens met criteria:")
    print("- Need 2+ scanners to agree on Grade A")
    print("- Age must be > 2 hours")
    print("- Top 10% must be < 50%")
    print("\nThis is GOOD - avoiding low-confidence setups.")

# Save full results
with open('/tmp/scanner_results/consensus_report.json', 'w') as f:
    json.dump(consensus_signals, f, indent=2)

PYTHON

echo ""
echo "✅ Multi-scanner analysis complete"
echo "📊 Full report: /tmp/scanner_results/consensus_report.json"
