#!/usr/bin/env python3
"""
Skylar Position Monitor v1.0
Alerts on old/stuck positions
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/skylar')
from skylar_strategy import SkylarTrader

def check_positions():
    """Check active positions for warnings"""
    active_file = Path("/home/skux/.openclaw/workspace/agents/skylar/skylar_active.json")
    
    if not active_file.exists():
        print("No active positions file")
        return
    
    with open(active_file) as f:
        data = json.load(f)
    
    positions = data.get("positions", [])
    
    if not positions:
        print("✅ No active positions")
        return
    
    print(f"\n🤖 Checking {len(positions)} active positions...")
    print("=" * 60)
    
    warnings = []
    
    for pos in positions:
        entry_time = datetime.fromtimestamp(pos.get("entryTime", 0)/1000)
        age = datetime.now() - entry_time
        days = age.days
        hours = age.seconds // 3600
        
        token = pos.get("token", "UNKNOWN")
        trade_num = pos.get("tradeNum")
        address = pos.get("tokenAddress", "")
        
        print(f"\n  Trade #{trade_num}: {token}")
        print(f"    Entry: {entry_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Age: {days}d {hours}h")
        print(f"    Address: {address}")
        print(f"    Size: {pos.get('inputSol')} SOL")
        
        # Check warnings
        if days >= 12:
            warnings.append(f"🔴 Trade #{trade_num}: {days} days old - REVIEW IMMEDIATELY")
        elif days >= 7:
            warnings.append(f"🟡 Trade #{trade_num}: {days} days old - Consider review")
        elif days >= 1:
            warnings.append(f"🟢 Trade #{trade_num}: {days}d {hours}h old - Normal")
    
    if warnings:
        print("\n" + "=" * 60)
        print("⚠️  WARNINGS:")
        for w in warnings:
            print(f"  {w}")
    
    print(f"\n💡 Recommendation:")
    print(f"   Check Solscan for token prices")
    print(f"   Current wallet: 8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5")


if __name__ == "__main__":
    check_positions()
