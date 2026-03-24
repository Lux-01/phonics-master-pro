#!/usr/bin/env python3
"""
Manual Test Trade - Step by Step with Full Error Reporting
Tests: 0.01 SOL → USDC swap
"""

import json
import sys
import traceback

print("=" * 70)
print("RAPHAEL MANUAL TEST TRADE")
print("Testing: 0.01 SOL → USDC")
print("=" * 70)

# Step 1: Load wallet
print("\n" + "=" * 70)
print("STEP 1: LOAD WALLET")
print("=" * 70)

try:
    sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/raphael')
    from raphael_trader import RaphaelTrader
    print("✅ raphael_trader module imported successfully")
except Exception as e:
    print(f"❌ FAILED to import raphael_trader: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    trader = RaphaelTrader()
    print(f"✅ RaphaelTrader initialized")
except Exception as e:
    print(f"❌ FAILED to initialize RaphaelTrader: {e}")
    traceback.print_exc()
    sys.exit(1)

if not trader.wallet:
    print("❌ FAILED: Wallet not loaded!")
    print(f"   Balance: {trader.balance}")
    sys.exit(1)

print(f"✅ Wallet loaded successfully!")
print(f"   Address: {trader.wallet_address}")
print(f"   Balance: {trader.balance:.6f} SOL")

# Step 2: Get quote from Jupiter
print("\n" + "=" * 70)
print("STEP 2: GET QUOTE FROM JUPITER")
print("=" * 70)

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
AMOUNT_SOL = 0.01

try:
    quote = trader.get_quote(USDC_MINT, AMOUNT_SOL)
    if quote:
        print(f"✅ Quote received from Jupiter")
        print(f"   Quote data: {json.dumps(quote, indent=2)[:500]}...")
    else:
        print("❌ FAILED: Quote returned None (check raphael_trader.py get_quote method)")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAILED to get quote: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Execute swap
print("\n" + "=" * 70)
print("STEP 3: EXECUTE SWAP")
print("=" * 70)

try:
    result = trader.execute_swap(quote)
    if result:
        print(f"✅ Swap executed!")
        print(f"   Result: {json.dumps(result, indent=2)}")
    else:
        print("❌ FAILED: execute_swap returned None")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAILED to execute swap: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("TEST COMPLETE - ALL STEPS PASSED!")
print("=" * 70)
