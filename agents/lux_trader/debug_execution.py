#!/usr/bin/env python3
"""
🔍 DEBUG LOGGER for LuxTrader Execution
Helps diagnose why trades fail
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

DEBUG_LOG = "/home/skux/.openclaw/workspace/agents/lux_trader/execution_debug.log"

def log_debug(stage: str, data: Dict[str, Any], level: str = "INFO"):
    """Log debug information with timestamp"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "level": level,
        "data": data
    }
    
    with open(DEBUG_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also print for visibility
    print(f"[{level}] {stage}: {json.dumps(data, default=str)[:100]}")


def analyze_0_001_failure():
    """Analyze why 0.001 SOL test trade failed"""
    print("\n" + "="*60)
    print("🔍 ANALYZING 0.001 SOL TEST TRADE FAILURE")
    print("="*60)
    
    findings = []
    
    # Check 1: Network connectivity
    print("\n1. Checking network connectivity...")
    try:
        import requests
        response = requests.get("https://quote-api.jup.ag/v6", timeout=5)
        findings.append(("Jupiter API Reachable", True, f"Status: {response.status_code}"))
    except Exception as e:
        findings.append(("Jupiter API Reachable", False, str(e)))
    
    # Check 2: Solana libraries
    print("\n2. Checking Solana libraries...")
    try:
        from solders.keypair import Keypair
        findings.append(("Solana Libraries", True, "solders available"))
    except ImportError:
        findings.append(("Solana Libraries", False, "solders not installed"))
    
    # Check 3: Private key storage
    print("\n3. Checking private key storage...")
    key_file = os.path.expanduser("~/.openclaw/secrets/trading_key.json")
    if os.path.exists(key_file):
        findings.append(("Key File Exists", True, key_file))
        # Check permissions
        import stat
        mode = os.stat(key_file).st_mode
        if mode & 0o777 == 0o600:
            findings.append(("Key File Permissions", True, "600 (secure)"))
        else:
            findings.append(("Key File Permissions", False, f"{oct(mode)} (should be 600)"))
    else:
        findings.append(("Key File Exists", False, f"Not found: {key_file}"))
    
    # Check 4: Jupiter executor import
    print("\n4. Checking Jupiter executor...")
    try:
        from jupiter_executor import execute_buy
        findings.append(("Jupiter Executor", True, "Import successful"))
    except Exception as e:
        findings.append(("Jupiter Executor", False, str(e)))
    
    # Check 5: Full auto executor import
    print("\n5. Checking full auto executor...")
    try:
        from full_auto_executor import execute_buy_auto
        findings.append(("Full Auto Executor", True, "Import successful"))
    except Exception as e:
        findings.append(("Full Auto Executor", False, str(e)))
    
    # Check 6: Current execution path
    print("\n6. Checking execution path...")
    try:
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')
        from luxtrader_live import LuxTraderLive, MODE
        trader = LuxTraderLive()
        findings.append(("LuxTrader Import", True, f"MODE={MODE}"))
        
        # Check if execute_trade calls Jupiter
        import inspect
        source = inspect.getsource(trader.execute_trade)
        if "execute_buy" in source or "Jupiter" in source:
            findings.append(("Execution Path", True, "Calls Jupiter executor"))
        else:
            findings.append(("Execution Path", False, "Does not call Jupiter"))
    except Exception as e:
        findings.append(("LuxTrader Import", False, str(e)))
    
    # Print findings
    print("\n" + "="*60)
    print("📊 FINDINGS")
    print("="*60)
    
    for name, status, details in findings:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {details}")
    
    # Root cause analysis
    print("\n" + "="*60)
    print("🔬 ROOT CAUSE ANALYSIS")
    print("="*60)
    
    failed_checks = [f for f in findings if not f[1]]
    
    if failed_checks:
        print(f"\nFound {len(failed_checks)} issues:")
        for name, _, details in failed_checks:
            print(f"  ❌ {name}: {details}")
        
        # Primary cause
        if any("Jupiter API" in f[0] for f in failed_checks):
            print("\n🎯 PRIMARY CAUSE: Network connectivity")
            print("   This session has DNS issues reaching Jupiter API.")
            print("   Cron jobs should work fine (different network context).")
        
        if any("Solana Libraries" in f[0] for f in failed_checks):
            print("\n🎯 PRIMARY CAUSE: Missing dependencies")
            print("   Install: pip install solders base58")
        
        if any("Key File" in f[0] for f in failed_checks):
            print("\n🎯 PRIMARY CAUSE: Private key not stored")
            print("   Run: python3 secure_key_manager.py --store")
        
        if any("Execution Path" in f[0] for f in failed_checks):
            print("\n🎯 PRIMARY CAUSE: Code not calling Jupiter")
            print("   execute_trade() method needs to call execute_buy()")
    else:
        print("\n✅ All checks passed!")
        print("   The 0.001 test should work.")
        print("   If it still fails, check the debug log:")
        print(f"   {DEBUG_LOG}")
    
    return findings


if __name__ == "__main__":
    analyze_0_001_failure()
