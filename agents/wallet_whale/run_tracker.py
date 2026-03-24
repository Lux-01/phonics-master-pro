#!/usr/bin/env python3
"""
WHALE TRACKER LAUNCHER
Run wallet monitor with various modes
"""

import asyncio
import argparse
import json
import os
import sys

# Add parent to path
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/wallet_whale')

from whale_tracker_skylar import WhaleTracker, CONFIG

def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     🐋 WALLET WHALE TRACKER v1.0 - SKYLAR COPY TRADER        ║
╠════════════════════════════════════════════════════════════════╣
║  Target: JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv         ║
║  Trigger: 4+ buys of same token in 30 seconds                ║
║  Action: Copy with 0.3 SOL using Skylar's exit strategy      ║
╚════════════════════════════════════════════════════════════════╝
    """)

def print_config():
    print(f"""
⚙️ CURRENT CONFIGURATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Target Wallet:
   {CONFIG['target_wallet']}

🎪 Skylar Wallet:
   {CONFIG['skylar_wallet']}

📊 Trigger Rules:
   • Min buys to trigger: {CONFIG['min_buys_to_trigger']}
   • Time window: {CONFIG['time_window_seconds']} seconds
   • Cooldown: {CONFIG['cooldown_minutes_between_trades']} minutes

💰 Trading Config:
   • Entry size: {CONFIG['entry_size_sol']} SOL
   • Target profit: +{CONFIG['target_profit_pct']}%
   • Stop loss: -{CONFIG['stop_loss_pct']}%
   • Time stop: {CONFIG['time_stop_hours']} hours
   • Slippage: {CONFIG['slippage_bps']/100}%

🔄 Monitoring:
   • Check interval: {CONFIG['check_interval_seconds']} seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def save_trigger_manual(token_address: str, size_sol: float = 0.3):
    """Manually trigger a trade (for testing)"""
    data = {
        "timestamp": "2026-03-07T20:35:00Z",
        "token_address": token_address,
        "size_sol": size_sol,
        "status": "MANUAL_TRIGGER",
        "result": {
            "success": True,
            "token": token_address,
            "size_sol": size_sol,
            "strategy": {
                "tp": "+15%",
                "sl": "-7%",
                "time_stop": "4h"
            }
        }
    }
    
    with open(CONFIG["triggered_file"], "a") as f:
        f.write(json.dumps(data, indent=2) + "\n---\n")
    
    print(f"✓ Manual trigger saved: {token_address}")
    print(f"  Size: {size_sol} SOL")
    print(f"  TP: +15% | SL: -7% | Time stop: 4h")

def show_status():
    """Show tracker status from state file"""
    if os.path.exists(CONFIG["state_file"]):
        with open(CONFIG["state_file"], 'r') as f:
            state = json.load(f)
        
        print(f"""
📈 TRACKER STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Last update: {state.get('last_update', 'N/A')}
   Triggered tokens: {len(state.get('triggered_tokens', []))}
   Last trigger: {state.get('last_trigger_time', 'None')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
    else:
        print("❌ No state file found. Tracker hasn't run yet.")

def show_trades():
    """Show all triggered trades"""
    if os.path.exists(CONFIG["triggered_file"]):
        with open(CONFIG["triggered_file"], 'r') as f:
            trades = json.load(f)
        
        trade_list = trades.get('trades', [])
        
        print(f"""
💼 TRIGGERED TRADES ({len(trade_list)} total):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        for i, trade in enumerate(trade_list[-10:], 1):  # Show last 10
            status = trade.get('status', 'UNKNOWN')
            emoji = "✅" if status == "EXECUTED" else "❌"
            ts = trade.get('timestamp', 'N/A')[:19]
            token = trade.get('trigger_data', {}).get('token_address', 'UNKNOWN')[:20]
            print(f"{emoji} Trade #{i} | {ts}")
            print(f"   Token: {token}...")
            print(f"   Status: {status}")
            print()
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    else:
        print("❌ No trades triggered yet.")

async def run_tracker():
    """Main tracker loop"""
    tracker = WhaleTracker()
    await tracker.run_monitor()

def main():
    parser = argparse.ArgumentParser(description="Wallet Whale Tracker for Skylar")
    parser.add_argument("--mode", choices=["monitor", "config", "status", "trades", "manual"], 
                       default="monitor", help="Operation mode")
    parser.add_argument("--token", type=str, help="Token address for manual trigger")
    parser.add_argument("--size", type=float, default=0.3, help="Manual trade size in SOL")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.mode == "config":
        print_config()
    elif args.mode == "status":
        show_status()
    elif args.mode == "trades":
        show_trades()
    elif args.mode == "manual":
        if not args.token:
            print("❌ Error: --token required for manual mode")
            sys.exit(1)
        save_trigger_manual(args.token, args.size)
    else:
        print_config()
        print("\n🚀 Starting tracker...")
        asyncio.run(run_tracker())

if __name__ == "__main__":
    main()
