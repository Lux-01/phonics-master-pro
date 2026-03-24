#!/usr/bin/env python3
"""Bridge Demo Script"""

import json
import os
from datetime import datetime
from luxbridge_sender import LuxBridge

def print_section(title):
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def show_current_alert():
    bridge_path = "/mnt/c/Users/HighE/DesktopMateLux/alerts.json"
    try:
        with open(bridge_path, 'r') as f:
            data = json.load(f)
        print("📄 Current Alert File:")
        print(json.dumps(data, indent=2))
    except:
        print("📄 No current alert")
    print()

def demo_grade_a():
    print_section("🚀 DEMO: Grade A Token Alert")
    bridge = LuxBridge()
    
    token = {
        'ca': '6fejB7foXnPUZQYHvi7pbjRUp2E5jmfaxjSxrtyopump',
        'name': 'AlphaCoin',
        'grade': 'A+',
        'mcap': 125000,
        'liq': 45000,
        'holders': 850
    }
    
    print(f"Sending: Grade {token['grade']} token found!")
    bridge.grade_a_alert(token)
    print("✅ Sent!")
    print()
    show_current_alert()

def demo_checkpoint():
    print_section("🎯 DEMO: Checkpoint Alert")
    bridge = LuxBridge()
    
    token = {
        'ca': 'test123checkpoint',
        'name': 'SurvivorCoin',
        'age_hours': 24,
        'grade': 'A'
    }
    
    print(f"Sending: Token survived 24h checkpoint!")
    bridge.checkpoint_alert(token, 24)
    print("✅ Sent!")
    print()
    show_current_alert()

def demo_survivor():
    print_section("🏆 DEMO: Survivor Alert")
    bridge = LuxBridge()
    
    survivor = {
        'ca': 'survivor456',
        'name': 'DiamondHands',
        'mcap_change_pct': 245,
        'checkpoints': {'6': {}, '12': {}, '24': {}}
    }
    
    print(f"Sending: 24h+ survivor with +245% gain!")
    bridge.survivor_alert(survivor)
    print("✅ Sent!")
    print()
    show_current_alert()

if __name__ == "__main__":
    print("=" * 80)
    print("  🎮 LUX BRIDGE LIVE DEMO")
    print("  Connects OpenClaw → Desktop Mate Avatar")
    print("=" * 80)
    print()
    print("📂 Bridge Location:")
    print("   Windows: C:\\Users\\HighE\\DesktopMateLux\\alerts.json")
    print("   WSL: /mnt/c/Users/HighE/DesktopMateLux/alerts.json")
    print()
    
    # Show current state
    print("Current alert file:")
    show_current_alert()
    
    # Run demos
    demo_grade_a()
    demo_checkpoint()
    demo_survivor()
    
    # Summary
    print_section("📊 SUMMARY")
    print("✅ Bridge is working!")
    print()
    print("What happens:")
    print("  1. I detect a crypto win (Grade A, checkpoint, survivor)")
    print("  2. I write JSON to the bridge file")
    print("  3. Desktop Mate Lua script watches the file")
    print("  4. Avatar plays matching animation")
    print()
    print("Alert types supported:")
    print("  • grade_a → Happy/excited animation")
    print("  • checkpoint → Nod/thumbs up")
    print("  • survivor → Dance/celebrate")
    print("  • heartbeat → Wave/idle")
    print()
    print("=" * 80)
