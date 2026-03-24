#!/usr/bin/env python3
"""
🚀 Dashboard Launcher
Starts the LuxTrader Emergency Dashboard
"""

import sys
import os

# Add lux_trader to path
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from emergency_dashboard import start_dashboard

# Wallet from your config
WALLET_ADDRESS = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
PORT = 7777

print("🚨 Starting LuxTrader Emergency Dashboard...")
print(f"   Wallet: {WALLET_ADDRESS[:20]}...")
print(f"   Port: {PORT}")
print(f"   URL: http://localhost:{PORT}")
print("\n   Press Ctrl+C to stop\n")

try:
    dashboard = start_dashboard(WALLET_ADDRESS, PORT)
    
    # Keep running
    import time
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\n🛑 Stopping dashboard...")
    dashboard.stop()
    print("   Dashboard stopped.")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
