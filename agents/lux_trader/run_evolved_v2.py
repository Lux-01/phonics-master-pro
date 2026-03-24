#!/usr/bin/env python3
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
