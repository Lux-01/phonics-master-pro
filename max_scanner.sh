#!/bin/bash
# Maximum Scanner Activation Script
# Runs ALL scanners in sequence to maximize token detection

echo "=================================="
echo "🚀 MAX SCANNER - ALL SYSTEMS GO"
echo "=================================="
echo "Starting at: $(date)"
echo ""

WORKSPACE="/home/skux/.openclaw/workspace"
RESULTS_FILE="$WORKSPACE/memory/max_scanner_results.json"

# Initialize results
echo '{"scan_time": "'$(date -Iseconds)'", "tokens": []}' > "$RESULTS_FILE"

# 1. Quick Trending Scan (fastest)
echo "[1/7] Quick Trending Scan..."
cd "$WORKSPACE"
python3 -c "
import requests
import json
import sys

sys.path.insert(0, '$WORKSPACE')

# Get latest trending
url = 'https://api.dexscreener.com/token-profiles/latest/v1'
resp = requests.get(url, timeout=10)

if resp.status_code == 200:
    tokens = resp.json()
    solana = [t for t in tokens if t.get('chainId') == 'solana'][:10]
    
    print(f'Found {len(solana)} trending tokens')
    
    results = []
    for token in solana:
        ca = token.get('tokenAddress', '')
        # Quick metrics
        detail = requests.get(f'https://api.dexscreener.com/latest/dex/tokens/{ca}', timeout=5).json()
        pairs = detail.get('pairs', [])
        
        if pairs:
            p = pairs[0]
            results.append({
                'symbol': p.get('baseToken', {}).get('symbol', '?'),
                'ca': ca,
                'mcap': p.get('marketCap', 0),
                'liquidity': p.get('liquidity', {}).get('usd', 0),
                'volume': p.get('volume', {}).get('h24', 0),
                'source': 'trending'
            })
    
    with open('$RESULTS_FILE', 'w') as f:
        json.dump({'scan_time': '$(date -Iseconds)', 'tokens': results}, f)
    
    for r in results[:5]:
        print(f\"  {r['symbol']}: MCAP ${r['mcap']:,.0f}\")
" 2>&1

echo ""
echo "[2/7] Running v54 Scanner..."
timeout 30 python3 -c "
import requests
import json
from datetime import datetime

results = []
searches = ['solana', 'new solana', 'pump fun']

for query in searches:
    url = f'https://api.dexscreener.com/latest/dex/search?q={query}'
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        for pair in data.get('pairs', [])[:5]:
            if pair.get('chainId') == 'solana':
                symbol = pair.get('baseToken', {}).get('symbol', '?')
                mcap = pair.get('marketCap', 0) or 0
                liq = pair.get('liquidity', {}).get('usd', 0) or 0
                vol = pair.get('volume', {}).get('h24', 0) or 0
                
                # v54 scoring
                score = 0
                if 50000 <= mcap <= 5000000: score += 5
                if liq >= 20000: score += 3
                if vol >= 50000: score += 2
                
                grade = 'A' if score >= 10 else 'B' if score >= 6 else 'C'
                
                print(f'  {symbol}: Grade {grade} (Score: {score})')
                
                results.append({
                    'symbol': symbol,
                    'mcap': mcap,
                    'liq': liq,
                    'vol': vol,
                    'score': score,
                    'grade': grade,
                    'source': 'v54'
                })

print(f'v54: {len(results)} tokens analyzed')
" 2>&1

echo ""
echo "[3/7] Mean Reversion Check..."
timeout 20 python3 -c "
import requests

url = 'https://api.dexscreener.com/latest/dex/search?q=solana'
resp = requests.get(url, timeout=10)

if resp.status_code == 200:
    data = resp.json()
    oversold = []
    
    for pair in data.get('pairs', [])[:20]:
        if pair.get('chainId') == 'solana':
            change = pair.get('priceChange', {}).get('h24', 0) or 0
            if change < -20:  # Oversold
                symbol = pair.get('baseToken', {}).get('symbol', '?')
                print(f'  {symbol}: {change:.1f}% - OVERSOLD')
                oversold.append(symbol)
    
    if not oversold:
        print('  No oversold tokens found')
" 2>&1

echo ""
echo "[4/7] Breakout Hunter..."
if [ -f "$WORKSPACE/agents/lux_trader/breakout_hunter_v3.py" ]; then
    timeout 20 python3 "$WORKSPACE/agents/lux_trader/breakout_hunter_v3.py" 2>&1 | grep -E "(found|breakout|pump)" | head -5 || echo "  No breakouts detected"
else
    echo "  Breakout hunter not available"
fi

echo ""
echo "[5/7] TRE Analysis..."
timeout 20 python3 -c "
import sys
sys.path.insert(0, '$WORKSPACE/skills/temporal-reasoning-engine')
try:
    from tre_core import TemporalReasoningEngine
    tre = TemporalReasoningEngine()
    print('  TRE active and ready for predictions')
except Exception as e:
    print(f'  TRE status: {e}')
" 2>&1

echo ""
echo "[6/7] Unified Scanner..."
timeout 30 python3 "$WORKSPACE/unified_scan.py" --strategy comprehensive --min-grade B --format table 2>&1 | tail -20

echo ""
echo "[7/7] LuxTrader Status..."
if [ -f "$WORKSPACE/agents/lux_trader/stage9_proposals.json" ]; then
    pending=$(python3 -c "import json; d=json.load(open('$WORKSPACE/agents/lux_trader/stage9_proposals.json')); print(len(d.get('pending', [])))" 2>/dev/null)
    echo "  Stage 9 pending: $pending proposals"
else
    echo "  Stage 9: No pending proposals"
fi

echo ""
echo "=================================="
echo "✅ MAX SCANNER COMPLETE"
echo "Time: $(date)"
echo "=================================="
echo ""
echo "Results saved to: memory/max_scanner_results.json"
echo ""
echo "Next scans:"
echo "  • High-frequency: Every 5 min"
echo "  • AOE v2: Every 30 min"
echo "  • Protected Multi: 6am, 12pm, 6pm"
echo "  • Stage 7: Every 5 min"
