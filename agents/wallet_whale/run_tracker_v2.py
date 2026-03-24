#!/usr/bin/env python3
"""
Whale Tracker v2.0 Launcher
Supports: start, stop, status, config, trades, test-telegram
"""

import json
import os
import sys
import subprocess
import signal
import time
from datetime import datetime

PID_FILE = "/home/skux/.openclaw/workspace/agents/wallet_whale/tracker.pid"
CONFIG_FILE = "/home/skux/.openclaw/workspace/agents/wallet_whale/whale_config.json"

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            return int(f.read().strip())
    return None

def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

def start_tracker():
    """Start the whale tracker in background"""
    pid = get_pid()
    if pid and is_running(pid):
        print("⚠️ Tracker already running (PID: {pid})")
        return
    
    print("🚀 Starting Whale Tracker v2.0...")
    
    # Start in background
    process = subprocess.Popen(
        [sys.executable, "/home/skux/.openclaw/workspace/agents/wallet_whale/whale_tracker_v2.py"],
        stdout=open("/home/skux/.openclaw/workspace/agents/wallet_whale/tracker.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    print(f"✅ Tracker started (PID: {process.pid})")
    print(f"📋 Log: agents/wallet_whale/tracker.log")
    print(f"\nWallets being monitored:")
    config = load_config()
    for w in config.get("target_wallets", []):
        if w.get("enabled", True):
            print(f"   • {w.get('name', 'Unknown')} (weight: {w.get('weight', 1.0)})")

def stop_tracker():
    """Stop the whale tracker"""
    pid = get_pid()
    if not pid:
        print("⚠️ Tracker not running")
        return
    
    if not is_running(pid):
        print("⚠️ Stale PID file, cleaning up")
        os.remove(PID_FILE)
        return
    
    print(f"🛑 Stopping tracker (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        if is_running(pid):
            os.kill(pid, signal.SIGKILL)
        print("✅ Tracker stopped")
    except Exception as e:
        print(f"❌ Error stopping: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def show_status():
    """Show tracker status"""
    pid = get_pid()
    config = load_config()
    
    print("\n" + "="*60)
    print("🐳 WHALE TRACKER v2.0 STATUS")
    print("="*60)
    
    if pid and is_running(pid):
        print(f"Status: 🟢 RUNNING (PID: {pid})")
    else:
        print("Status: 🔴 STOPPED")
    
    print(f"\n📊 Configuration:")
    print(f"   Check interval: {config['monitoring']['check_interval_seconds']}s")
    print(f"   Trigger: {config['trigger_rules']['min_buys_to_trigger']}+ buys in {config['trigger_rules']['time_window_seconds']}s")
    print(f"   Multi-whale: {config['trigger_rules'].get('multi_whale_threshold', 2)}+ wallets")
    print(f"   Cooldown: {config['trigger_rules']['cooldown_minutes_between_trades']} min")
    print(f"   Entry size: {config['skylar_strategy']['entry_size_sol']} SOL")
    
    print(f"\n👛 Monitored Wallets:")
    for w in config.get("target_wallets", []):
        status = "🟢" if w.get("enabled", True) else "🔴"
        print(f"   {status} {w.get('name', 'Unknown')} (weight: {w.get('weight', 1.0)})")
    
    print(f"\n📱 Telegram: {'🟢 ENABLED' if config.get('telegram', {}).get('enabled') else '🔴 DISABLED'}")
    
    # Show recent trades
    triggered_file = config["files"]["triggered_file"]
    if os.path.exists(triggered_file):
        try:
            with open(triggered_file) as f:
                trades = json.load(f)
            print(f"\n📈 Recent Trades: {len(trades)} total")
            for trade in trades[-3:]:
                print(f"   {trade.get('timestamp', 'N/A')[:10]}: {trade.get('token_symbol', 'UNKNOWN')} ({trade.get('status', 'unknown')})")
        except:
            pass
    
    print("="*60)

def show_config():
    """Show current configuration"""
    config = load_config()
    print(json.dumps(config, indent=2))

def show_trades():
    """Show trade history"""
    config = load_config()
    triggered_file = config["files"]["triggered_file"]
    
    if not os.path.exists(triggered_file):
        print("No trades yet")
        return
    
    try:
        with open(triggered_file) as f:
            trades = json.load(f)
        
        print(f"\n📊 TRADE HISTORY ({len(trades)} trades)\n")
        
        for trade in trades[-10:]:
            ts = trade.get('timestamp', 'N/A')
            symbol = trade.get('token_symbol', 'UNKNOWN')
            status = trade.get('status', 'unknown')
            size = trade.get('entry_size_sol', 0)
            
            emoji = "✅" if status == "executed" else "❌"
            print(f"{emoji} {ts[:16]} | {symbol} | {size} SOL | {status}")
    
    except Exception as e:
        print(f"Error reading trades: {e}")

def test_telegram():
    """Test Telegram alerts"""
    try:
        from telegram_alerts import TelegramAlerter
        config = load_config()
        
        alerter = TelegramAlerter(config.get("telegram", {}))
        
        print("📱 Testing Telegram alerts...")
        
        # Test whale alert
        alerter.alert_whale_detected(
            "Test Whale", "TEST", "TEST123456789",
            5, 2.5, "HIGH"
        )
        print("✅ Whale alert sent")
        
        # Test multi-whale alert
        alerter.alert_multi_whale("TEST", "TEST123456789", 3, 12)
        print("✅ Multi-whale alert sent")
        
        print("\nCheck your Telegram for test messages!")
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        print("Make sure TELEGRAM_BOT_TOKEN is set in environment")

def add_wallet(address, name, weight=1.0):
    """Add a new whale wallet"""
    config = load_config()
    
    # Check if already exists
    for w in config["target_wallets"]:
        if w["address"] == address:
            print(f"⚠️ Wallet already exists: {w.get('name', 'Unknown')}")
            return
    
    config["target_wallets"].append({
        "address": address,
        "name": name,
        "weight": weight,
        "enabled": True
    })
    
    save_config(config)
    print(f"✅ Added wallet: {name} ({address[:20]}...)")

def remove_wallet(name):
    """Remove a whale wallet"""
    config = load_config()
    
    original_count = len(config["target_wallets"])
    config["target_wallets"] = [w for w in config["target_wallets"] if w.get("name") != name]
    
    if len(config["target_wallets"]) < original_count:
        save_config(config)
        print(f"✅ Removed wallet: {name}")
    else:
        print(f"⚠️ Wallet not found: {name}")

def show_help():
    print("""
🐳 Whale Tracker v2.0 - Commands

Usage: python3 run_tracker_v2.py [command]

Commands:
  start              Start the tracker in background
  stop               Stop the tracker
  status             Show tracker status and config
  config             Show full configuration
  trades             Show trade history
  test-telegram      Test Telegram alerts
  add-wallet         Add a new whale wallet
  remove-wallet      Remove a whale wallet
  help               Show this help

Examples:
  python3 run_tracker_v2.py start
  python3 run_tracker_v2.py status
  python3 run_tracker_v2.py add-wallet <address> <name> [weight]
  python3 run_tracker_v2.py remove-wallet <name>
""")

# === MAIN ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_tracker()
    elif command == "stop":
        stop_tracker()
    elif command == "status":
        show_status()
    elif command == "config":
        show_config()
    elif command == "trades":
        show_trades()
    elif command == "test-telegram":
        test_telegram()
    elif command == "add-wallet":
        if len(sys.argv) < 4:
            print("Usage: add-wallet <address> <name> [weight]")
            sys.exit(1)
        weight = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
        add_wallet(sys.argv[2], sys.argv[3], weight)
    elif command == "remove-wallet":
        if len(sys.argv) < 3:
            print("Usage: remove-wallet <name>")
            sys.exit(1)
        remove_wallet(sys.argv[2])
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
