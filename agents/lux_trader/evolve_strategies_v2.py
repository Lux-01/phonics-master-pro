#!/usr/bin/env python3
"""
✨ EVOLVED STRATEGIES v2.0
Based on 6-month backtest learnings
"""

import json
from pathlib import Path
import random

def load_data():
    data_file = Path("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json")
    with open(data_file) as f:
        return json.load(f)

print("=" * 80)
print("🧬 EVOLVING 5 STRATEGIES TO v2.0")
print("=" * 80)
print()

# Load v1.0 results to inform evolution
try:
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/rug_radar_results.json') as f:
        rug_v1 = json.load(f)
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/breakout_hunter_results.json') as f:
        breakout_v1 = json.load(f)
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/mean_reverter_results.json') as f:
        mean_v1 = json.load(f)
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/whale_tracker_results.json') as f:
        whale_v1 = json.load(f)
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/social_sentinel_results.json') as f:
        social_v1 = json.load(f)
    
    print("📊 v1.0 PERFORMANCE:")
    print(f"  🏹 Breakout:   {breakout_v1['multiplier']:.1f}x (80% WR, 2 rugs)")
    print(f"  📉 Mean-Rev:   {mean_v1['multiplier']:.1f}x (64% WR, 1 rug)")
    print(f"  🛡️ Rug-Radar:  {rug_v1['multiplier']:.1f}x (83% WR, 4 rugs)")
    print(f"  🐳 Whale:      {whale_v1['multiplier']:.1f}x")
    print(f"  🐦 Social:     {social_v1['multiplier']:.1f}x")
    print()
except Exception as e:
    print(f"⚠️  Could not load v1.0 results: {e}")
    print("   Running with default improvements")
    print()

# EVOLUTION PATTERNS LEARNED:
evolution_learnings = {
    "breakout_hunter": {
        "worked": ["40% position size", "Let winners run to 25-30%", "Low rug rate (2)"],
        "improve": ["Add trailing stop after +15%", "Tighten entry criteria to score 12+"],
        "new_params": {"position_pct": 0.45, "min_score": 12, "trail_activation": 0.15}
    },
    "rug_radar": {
        "worked": ["82.6% win rate", "Quick 8% exits", "Strict A+ filtering"],
        "improve": ["Add dynamic sizing based on safety score", "Increase target for safety score 13+ to 12%"],
        "new_params": {"position_pct": 0.30, "dynamic_target": True, "safety_bonus": 0.04}
    },
    "mean_reverter": {
        "worked": ["Only 1 rug", "64% win rate acceptable"],
        "improve": ["Require deeper oversold (-10% vs -5%)", "Larger positions on strong deviations"],
        "new_params": {"position_pct": 0.35, "min_deviation": -0.10, "deviation_multiplier": 1.5}
    },
    "whale_tracker": {
        "worked": ["Whale score detection", "Volume spike timing"],
        "improve": ["Stricter whale score (8+ vs 7+)", "Multi-scale exits like breakout"],
        "new_params": {"min_whale_score": 8, "multi_exit": True, "rug_filter_pct": 0.45}
    },
    "social_sentinel": {
        "worked": ["Narrative momentum capturing", "Freshness filtering"],
        "improve": ["Require bull market phase", "Earlier exits on fading momentum"],
        "new_params": {"require_bull": True, "momentum_cutoff": 0.08, "early_exit": True}
    }
}

# Save evolution spec
with open('/home/skux/.openclaw/workspace/agents/lux_trader/strategies_v2_evolution.json', 'w') as f:
    json.dump({
        "version": "2.0",
        "evolved_at": "2026-03-13T09:50:00+11:00",
        "based_on": "6_month_backtest_v1",
        "strategies": evolution_learnings
    }, f, indent=2)

print("🧬 EVOLUTION SPEC SAVED")
print()
print("Key Improvements for v2.0:")
print()

for strategy, learnings in evolution_learnings.items():
    emoji = {"breakout_hunter": "🏹", "rug_radar": "🛡️", "mean_reverter": "📉", 
             "whale_tracker": "🐳", "social_sentinel": "🐦"}[strategy]
    
    print(f"{emoji} {strategy.replace('_', ' ').title()}:")
    print(f"   New params: {learnings['new_params']}")
    print(f"   Focus: {learnings['improve'][0]}")
    print()

print("=" * 80)
print("✅ Evolution complete. Ready to run v2.0 backtests.")
print()

# Now create the evolved strategy runner
runner_code = '''#!/usr/bin/env python3
"""
Run all 5 EVOLVED strategies (v2.0) and compare
"""

import json
from pathlib import Path
import random

def load_data():
    with open("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json") as f:
        return json.load(f)

# Load evolution spec
with open("/home/skux/.openclaw/workspace/agents/lux_trader/strategies_v2_evolution.json") as f:
    evolution = json.load(f)

strategies = []

# 1. BREAKOUT HUNTER v2.0 🏹
def evolved_breakout():
    params = evolution["strategies"]["breakout_hunter"]["new_params"]
    return {
        "name": "Breakout Hunter v2.0",
        "emoji": "🏹",
        "position_pct": params["position_pct"],
        "min_score": params["min_score"],
        "trail_activation": params["trail_activation"],
        "target": 0.25,
        "stop": -0.07,
        "rug_filter": 0.45,
        "improvements": ["Tighter entry (score 12+)", "Trailing stop after +15%", "45% position size"]
    }

# 2. RUG-RADAR v2.0 🛡️
def evolved_rug_radar():
    params = evolution["strategies"]["rug_radar"]["new_params"]
    return {
        "name": "Rug-Radar v2.0", 
        "emoji": "🛡️",
        "position_pct": params["position_pct"],
        "dynamic_target": params["dynamic_target"],
        "safety_bonus": params["safety_bonus"],
        "base_target": 0.08,
        "stop": -0.04,
        "rug_filter": 0.65,
        "improvements": ["Dynamic sizing by safety score", "12% target for score 13+", "65% rug detection"]
    }

# 3. MEAN-REVERTER v2.0 📉
def evolved_mean_reverter():
    params = evolution["strategies"]["mean_reverter"]["new_params"]
    return {
        "name": "Mean-Reverter v2.0",
        "emoji": "📉",
        "position_pct": params["position_pct"],
        "min_deviation": params["min_deviation"],
        "deviation_multiplier": params["deviation_multiplier"],
        "target": 0.15,
        "stop": -0.05,
        "rug_filter": 0.50,
        "improvements": ["Deeper oversold requirement (-10%)", "Larger positions on deviations", "50% rug filter"]
    }

# 4. WHALE TRACKER v2.0 🐳
def evolved_whale_tracker():
    params = evolution["strategies"]["whale_tracker"]["new_params"]
    return {
        "name": "Whale Tracker v2.0",
        "emoji": "🐳",
        "position_pct": 0.35,
        "min_whale_score": params["min_whale_score"],
        "multi_exit": params["multi_exit"],
        "target": 0.20,
        "stop": -0.07,
        "rug_filter": params["rug_filter_pct"],
        "improvements": ["Stricter whale score (8+)", "Multi-scale exits", "45% rug filter"]
    }

# 5. SOCIAL SENTINEL v2.0 🐦
def evolved_social_sentinel():
    params = evolution["strategies"]["social_sentinel"]["new_params"]
    return {
        "name": "Social Sentinel v2.0",
        "emoji": "🐦",
        "position_pct": 0.30,
        "require_bull": params["require_bull"],
        "momentum_cutoff": params["momentum_cutoff"],
        "early_exit": params["early_exit"],
        "target": 0.15,
        "stop": -0.07,
        "rug_filter": 0.40,
        "improvements": ["Require bull market", "Early exit on fading momentum", "40% rug filter"]
    }

print("🚀 EVOLVED STRATEGIES v2.0 READY")
print()
print("Run individual backtests with improved parameters")
print()
'''

with open('/home/skux/.openclaw/workspace/agents/lux_trader/run_evolved_v2.py', 'w') as f:
    f.write(runner_code)

print("📁 Created: run_evolved_v2.py")
print("📁 Created: strategies_v2_evolution.json")
print()
print("Next step: Run v2.0 backtests to validate improvements")
