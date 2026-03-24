#!/bin/bash
# v5.5 Combined Full Scan - Fundamentals + Charts

cd /home/skux/.openclaw/workspace

export PATH="$HOME/.local/bin:$PATH"

echo "================================================================================"
echo "🚀 SOLANA ALPHA HUNTER v5.5 - Chart Analysis Edition"
echo "🕐 $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"
echo ""

# Step 1: Run v5.4 fundamentals scan
echo "[1/3] Running v5.4 fundamentals scan..."
bash run_v54_combined.sh 2>&1 | tee scan_v54_fundamentals.log

# Step 2: Enhance with chart analysis
echo ""
echo "[2/3] Adding 15m chart analysis (15 candles)..."
python3 v55_chart_analyzer.py 2>&1 | tee scan_v55_charts.log

# Step 3: Generate enhanced alert
echo ""
echo "[3/3] Generating v5.5 enhanced results..."

if [ -f "alpha_results_v55.json" ]; then
    echo "✅ v5.5 results saved"
    
    # Show Grade A+ with chart analysis
    python3 << 'EOF'
import json

try:
    with open('alpha_results_v55.json') as f:
        results = json.load(f)
    
    print("\n🏆 v5.5 TOP GRADES (Fundamentals + Charts):")
    
    # Get best tokens
    best = sorted([t for t in results if t.get('grade_v55', '').startswith('A')], 
                  key=lambda x: x.get('score_v55', 0), reverse=True)[:5]
    
    for i, t in enumerate(best, 1):
        name = t.get('name', '?')
        grade = t.get('grade_v55', '?')
        fund_score = t.get('score_v54', 0)
        total_score = t.get('score_v55', 0)
        charts = t.get('chart_signals', {})
        
        print(f"\n{i}. {name}")
        print(f"   Grade: {grade} | Fundamentals: {fund_score}/20 | Total: {total_score}/30")
        
        if charts:
            print(f"   📊 RSI: {charts.get('rsi')} | Trend: {charts.get('trend')}")
            print(f"   🚀 Breakout: {charts.get('breakout')} | Above VWAP: {charts.get('vwap') != 0}")
            
        reasons = t.get('chart_reasons', [])
        if reasons:
            print(f"   💡 {', '.join(reasons)}")
    
    # Breakout specialists
    print("\n📈 BREAKOUT SETUPS:")
    breakouts = [t for t in results if t.get('chart_signals', {}).get('breakout')]
    for t in breakouts[:3]:
        name = t.get('name', '?')
        grade = t.get('grade_v55', '?')
        print(f"   • {name} ({grade}) - Breaking out!")

except Exception as e:
    print(f"Error: {e}")
EOF
else
    echo "❌ v5.5 results not found"
fi

echo ""
echo "================================================================================"
echo "✅ v5.5 Complete"
echo "📁 Files:"
echo "   - alpha_results_v54.json (fundamentals)"
echo "   - alpha_results_v55.json (fundamentals + charts)"
echo "================================================================================"
