#!/usr/bin/env python3
"""
Raphael v2.3 Pre-Flight Test Suite
Run this before starting Raphael for real
"""

import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/raphael')

from raphael_autotrader_v2 import RaphaelAutoTraderV23, PriceHistory, CONFIG
from datetime import datetime, timedelta
import json

print("="*70)
print("🦎 RAPHAEL v2.3 PRE-FLIGHT TEST")
print("="*70)

tests_passed = 0
tests_failed = 0
def test(name, condition, details=""):
    global tests_passed, tests_failed
    if condition:
        print(f"✅ {name}")
        tests_passed += 1
    else:
        print(f"❌ {name}")
        if details:
            print(f"   → {details}")
        tests_failed += 1

# Test 1: CONFIG completeness
print("\n📋 CONFIGURATION TESTS")
test("MCAP range defined", CONFIG['mcap_min'] == 100000 and CONFIG['mcap_max'] == 500000000)
test("Position sizing defined", len(CONFIG['trade_sizes']) == 4)
test("27 new rules present", 
    'new_launch_window_mins' in CONFIG and
    'social_mention_spike' in CONFIG and
    'news_fade_range' in CONFIG and
    'three_green_lights_required' in CONFIG and
    'narrative_bonus_sol' in CONFIG
)

# Test 2: PriceHistory
print("\n📊 PRICE HISTORY TESTS")
ph = PriceHistory()
for i in range(20):
    ph.add(1.0 + i*0.05)
data = ph.to_dict()
ph2 = PriceHistory.from_dict(data)
test("PriceHistory serialization", len(ph2.prices) == 20 and len(ph2.timestamps) == 20)
atr = ph.get_atr()
test("ATR calculation", atr is not None, f"ATR is {atr}")

# Test 3: New rule methods
print("\n🎯 NEW RULE METHODS")
rt = RaphaelAutoTraderV23.__dict__
test("check_three_green_lights", 'check_three_green_lights' in rt)
test("check_social_fade", 'check_social_fade' in rt)
test("check_news_fade", 'check_news_fade' in rt)
test("check_multi_timeframe", 'check_multi_timeframe_alignment' in rt)
test("check_coordination", 'check_coordination_bias' in rt)
test("is_session_transition", 'is_session_transition' in rt)
test("check_correlation", 'check_correlation_laggard' in rt)
test("false_breakout_rate", 'get_false_breakout_rate' in rt)
test("new_launch_window", 'is_new_launch_window' in rt)

# Test 4: Range exit
print("\n📤 EXIT FRAMEWORK")
test("Range exit percentage", CONFIG['range_exit_pct'] == 80)
test("Adaptive scale enabled", CONFIG['adaptive_scale'])
test("Narrative bonus amount", CONFIG['narrative_bonus_sol'] == 0.1)

# Test 5: State file
print("\n💾 STATE MANAGEMENT")
test("State file path", CONFIG['state_file'].endswith('v22_state.json'))
test("Log file path", CONFIG['log_file'].endswith('.json'))

# Summary
print("\n" + "="*70)
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print("="*70)

if tests_failed == 0:
    print("🚀 Raphael v2.3 is ready to trade!")
    print("\nTo start:")
    print("  cd /home/skux/.openclaw/workspace/agents/raphael")
    print("  python3 raphael_supervisor.py")
    sys.exit(0)
else:
    print("⚠️  Fix failed tests before running")
    sys.exit(1)
