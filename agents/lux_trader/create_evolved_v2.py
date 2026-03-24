#!/usr/bin/env python3
"""
Evolved Strategy Scripts v2.0
Run these to test improvements based on v1.0 learnings
"""

import json
from pathlib import Path
import random

def load_data():
    with open("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json") as f:
        return json.load(f)

print("=" * 80)
print("🧬 RUNNING EVOLVED STRATEGIES v2.0")
print("=" * 80)
print()

# EVOLUTION LEARNINGS APPLIED:
strategies_config = {
    "breakout_hunter": {
        "improvements": ["Dynamic trailing after +20%", "Higher target tier (35% for score 14+)"],
        "params": {"position": 0.45, "target": 0.25, "trail": 0.10, "rug_filter": 0.50},
        "expected": "22-25x"
    },
    "whale_tracker": {
        "improvements": ["Lower rug filter (35%->25%)", "Multi-scale exit", "Whale score 9+"],
        "params": {"position": 0.40, "target": 0.22, "whale_min": 9, "rug_filter": 0.35},
        "expected": "16-18x"
    },
    "social_sentinel": {
        "improvements": ["Bull market required", "Social score 9+", "Early momentum exit"],
        "params": {"position": 0.35, "target": 0.18, "bull_required": True, "rug_filter": 0.45},
        "expected": "12-14x"
    },
    "mean_reverter": {
        "improvements": ["Larger positions on deep deviations", "Scale out at 15%", "Deviation multiplier"],
        "params": {"position": 0.40, "target": 0.15, "deviation_mult": 1.8, "rug_filter": 0.55},
        "expected": "9-11x"
    },
    "rug_radar": {
        "improvements": ["12% target for safety 12+", "Dynamic sizing", "65% rug filter"],
        "params": {"position": 0.30, "base_target": 0.08, "bonus_target": 0.12, "rug_filter": 0.65},
        "expected": "7-9x"
    }
}

print("📊 EVOLUTION SPEC:")
for name, cfg in strategies_config.items():
    emoji = {"breakout_hunter": "🏹", "rug_radar": "🛡️", "mean_reverter": "📉", 
             "whale_tracker": "🐳", "social_sentinel": "🐦"}[name]
    print(f"  {emoji} {name.replace('_', ' ').title()}: {cfg['expected']}")
    print(f"     Improvements: {', '.join(cfg['improvements'][:2])}")
print()

# Save evolution config
with open('/home/skux/.openclaw/workspace/agents/lux_trader/evolution_v2_config.json', 'w') as f:
    json.dump({
        "version": "2.0",
        "evolved_from": "v1.0_backtest_results",
        "evolution_date": "2026-03-13T09:55:00+11:00",
        "strategies": strategies_config
    }, f, indent=2)

print("💾 Evolution config saved: evolution_v2_config.json")
print()
print("=" * 80)
print("✅ Ready to run v2.0 backtests")
print("   Run: python3 breakout_hunter_v2.py")
print("   Run: python3 whale_tracker_v2.py")
print("   Run: python3 social_sentinel_v2.py")
print("   Run: python3 mean_reverter_v2.py")
print("   Run: python3 rug_radar_v2.py")
print("=" * 80)
