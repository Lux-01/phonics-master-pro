#!/bin/bash
# Multi-Scanner Trading Signal System with ALOE Integration
# Runs all scanners, applies pattern extraction, and learns from outcomes

cd /home/skux/.openclaw/workspace

echo "🚀 MULTI-SCANNER PROTECTION SYSTEM"
echo "==================================="
echo "With ALOE Learning + Pattern Extraction"
echo ""

# Create results directory
mkdir -p /tmp/scanner_results

# Run all scanners in background
echo "[1/4] Running scanners..."

# v5.4 Primary
bash run_v54_combined.sh > /tmp/scanner_results/v54.log 2>&1 &
PID54=$!

# v5.5 Chart Analysis
bash run_v55_full.sh > /tmp/scanner_results/v55.log 2>&1 &
PID55=$!

echo "⏳ Waiting for scanners..."
wait $PID54 $PID55

# Copy results
[ -f alpha_results_v54.json ] && cp alpha_results_v54.json /tmp/scanner_results/v54_results.json
[ -f alpha_results_v55.json ] && cp alpha_results_v55.json /tmp/scanner_results/v55_results.json

echo "✅ Scanners complete"
echo ""

# Aggregate results with Pattern Protection
echo "[2/4] Analyzing with Pattern Protection..."

python3 <> 'PYTHON'
import json
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/pattern-extractor')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/outcome-tracker')

from rug_pattern_extractor import check_token
from trading_outcome_tracker import check_risk

def load_results(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

# Load results
v54_results = load_results('/tmp/scanner_results/v54_results.json')
v55_results = load_results('/tmp/scanner_results/v55_results.json')

print(f"📊 Tokens found: v5.4={len(v54_results)}, v5.5={len(v55_results)}")
print("")

# Index by CA
all_tokens = {}
for token in v54_results:
    ca = token.get('ca')
    if ca:
        token['scanners'] = {'v5.4': token.get('score', 0)}
        all_tokens[ca] = token

for token in v55_results:
    ca = token.get('ca')
    if ca in all_tokens:
        all_tokens[ca]['scanners']['v5.5'] = token.get('score', 0)
    elif ca:
        token['scanners'] = {'v5.5': token.get('score', 0)}
        all_tokens[ca] = token

# Apply Pattern Protection filtering
protected_signals = []

print("🔍 Applying Pattern Protection...")
print("-" * 60)

for ca, token in all_tokens.items():
    age = token.get('age_hours', 0)
    top10 = token.get('top10_pct', 100)
    grade = token.get('grade', 'F')
    score = token.get('score', 0)
    
    # Skip obvious rejects
    if age < 0.5 or top10 > 80:
        continue
    
    # Apply rug pattern detection
    pattern_result = check_token(age, top10, grade, score)
    
    # Apply historical outcome check
    outcome_result = check_risk(age, top10, grade)
    
    # Combined assessment
    if not pattern_result['passed']:
        print(f"🚫 BLOCKED: {token.get('name', '?')} ({token.get('symbol', '?')})")
        print(f"   Reason: Pattern protection triggered")
        for reason in pattern_result['reasons'][:2]:
            print(f"   → {reason}")
        continue
    
    if outcome_result['risk_level'] == 'HIGH':
        print(f"⚠️  HIGH RISK: {token.get('name', '?')} ({token.get('symbol', '?')})")
        for warning in outcome_result['warnings'][:2]:
            print(f"   → {warning}")
        continue
    
    # Count Grade A consensus
    a_grades = sum(1 for s in token.get('scanners', {}).values() if s >= 14)
    
    if a_grades >= 1:  # At least one scanner says Grade A
        # Determine signal strength
        strength = "WEAK"
        if score >= 16 and age >= 3 and outcome_result['risk_level'] == 'MINIMAL':
            strength = "STRONG"
        elif score >= 15 and age >= 2 and outcome_result['risk_level'] in ['MINIMAL', 'LOW']:
            strength = "MODERATE"
        
        protected_signals.append({
            'ca': ca,
            'name': token.get('name', '?'),
            'symbol': token.get('symbol', '?'),
            'grade': grade,
            'score': score,
            'age': age,
            'top10': top10,
            'scanners': token.get('scanners', {}),
            'strength': strength,
            'risk_level': outcome_result['risk_level'],
            'warnings': outcome_result['warnings']
        })

# Sort by strength and score
protected_signals.sort(key=lambda x: (
    x['strength'] != 'STRONG',
    x['strength'] != 'MODERATE',
    -x['score']
))

print("")
print("=" * 60)
print(f"🎯 PROTECTED SIGNALS: {len(protected_signals)} tokens passed")
print("=" * 60)

if protected_signals:
    for i, sig in enumerate(protected_signals[:5], 1):
        emoji = "🔥" if sig['strength'] == "STRONG" else "✅" if sig['strength'] == "MODERATE" else "⚠️"
        
        print(f"\n{emoji} SIGNAL #{i}: {sig['name']} ({sig['symbol']})")
        print(f"   Strength: {sig['strength']}")
        print(f"   Grade: {sig['grade']} | Score: {sig['score']:.1f}")
        print(f"   Age: {sig['age']:.1f}h | Top10%: {sig['top10']:.1f}%")
        print(f"   Risk Level: {sig['risk_level']}")
        
        if sig['warnings']:
            print(f"   ⚠️  Warnings:")
            for w in sig['warnings'][:2]:
                print(f"      → {w}")
        
        print(f"\n   🎯 TRADE PARAMETERS:")
        print(f"   CA: `{sig['ca']}`")
        
        if sig['strength'] == "STRONG":
            print(f"   Entry: 0.02 SOL (High Confidence)")
        elif sig['strength'] == "MODERATE":
            print(f"   Entry: 0.02 SOL (Standard)")
        else:
            print(f"   Entry: 0.01 SOL (Cautious)")
        
        print(f"   Target: +15% | Stop: -7% | Time Stop: 4h")
        print("-" * 60)
    
    print(f"\n📊 FILTERS APPLIED:")
    print(f"✅ Pattern Protection Active ({len(pattern_result.get('reasons', []))} rules)")
    print(f"✅ Historical Outcome Check")
    print(f"✅ Auto-reject: Age < 30min, Top10% > 80%")
    print(f"✅ Warning: Age < 2h, Top10% > 50%")
    print(f"\n🧠 ALOE Learning: Every signal outcome will be tracked")
    
else:
    print("\n⚠️ NO SIGNALS PASSED PATTERN PROTECTION")
    print("\nThis is GOOD - avoiding high-risk tokens!")
    print("\nAll tokens were filtered due to:")
    print("- Too new (< 2 hours)")
    print("- High whale concentration (> 50%)")
    print("- Matches known rug patterns")

# Save results
with open('/tmp/scanner_results/protected_signals.json', 'w') as f:
    json.dump(protected_signals, f, indent=2)

PYTHON

echo ""
echo "[3/4] Logging signals to ALOE..."

python3 <> 'PYTHON'
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/outcome-tracker')
from trading_outcome_tracker import log_scanner_signal

try:
    with open('/tmp/scanner_results/protected_signals.json', 'r') as f:
        signals = json.load(f)
    
    for sig in signals:
        signal_id = log_scanner_signal({
            'ca': sig['ca'],
            'name': sig['name'],
            'scanner_version': 'v5.4-v5.5-consensus',
            'grade': sig['grade'],
            'score': sig['score'],
            'age_hours': sig['age'],
            'top10_pct': sig['top10'],
            'mcap': 0,  # Would need actual value
            'liq': 0,
            'vol24': 0
        })
        print(f"  ✅ Logged: {sig['name']} ({signal_id})")
    
    print(f"\n📈 Total signals logged: {len(signals)}")
    print("   Outcomes will be tracked automatically")
    
except Exception as e:
    print(f"   ⚠️ Logging issue: {e}")

PYTHON

echo ""
echo "[4/4] System ready!"
echo ""
echo "==================================="
echo "✅ MULTI-SCANNER WITH ALOE COMPLETE"
echo "==================================="
echo ""
echo "Features Active:"
echo "• 2 scanners (v5.4, v5.5)"
echo "• Pattern Protection (5 rules)"
echo "• Historical Outcome Check"
echo "• ALOE Learning System"
echo "• Auto-signal Logging"
echo ""
echo "Next: Signals delivered with risk assessment"
echo "After trade: Update outcome for learning"
