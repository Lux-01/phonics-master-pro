#!/bin/bash
# Combined v5.3 + v5.4 - New scan + tracking

cd /home/skux/.openclaw/workspace

export PATH="$HOME/.local/bin:$PATH"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "================================================================================"
echo "🚀 SOLANA ALPHA HUNTER v5.4 COMBINED"
echo "🕐 $TIMESTAMP"
echo "================================================================================"

echo ""
echo "[1/3] Running v5.3 new token scan..."
bash run_v53_daily.sh 2>&1 | tee scan_v53.log

echo ""
echo "[2/3] Processing results through v5.4 tracker..."
# This will ingest any new Grade A tokens for tracking
python3 << 'EOF'
import json
import sys

# Load v5.3 results
try:
    with open('alpha_results_v53.json', 'r') as f:
        results = json.load(f)
    
    print(f"✓ v5.3 found {len(results)} tokens")
    
    # Import and process through v5.4
    sys.path.insert(0, '/home/skux/.openclaw/workspace')
    from solana_alpha_hunter_v54 import TokenTracker, V54Analyzer, SentimentAnalyzer
    
    enhanced = []
    for token in results:
        print(f"  Processing: {token.get('ca', 'unknown')[:20]}...")
        try:
            enhanced_token = V54Analyzer.analyze_token(token)
            enhanced.append(enhanced_token)
            print(f"    ✓ Grade {enhanced_token.get('final_grade')} ({enhanced_token.get('score_v54')}/25)")
            if enhanced_token.get('bonuses'):
                print(f"    Bonuses: {', '.join(enhanced_token.get('bonuses', []))}")
        except Exception as e:
            print(f"    ⚠️ Error: {e}")
            enhanced.append(token)
    
    # Save enhanced results
    with open('alpha_results_v54.json', 'w') as f:
        json.dump(enhanced, f, indent=2)
    
    print(f"✓ Saved {len(enhanced)} enhanced results to alpha_results_v54.json")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

echo ""
echo "[3/3] Running survivor monitor..."
bash run_v54_monitor.sh 2>&1

echo ""
echo "================================================================================"
echo "✅ v5.4 Combined complete: $TIMESTAMP"
echo "💡 New results: alpha_results_v54.json"
echo "💡 Survivors: tracked_tokens.json"
echo "================================================================================"
