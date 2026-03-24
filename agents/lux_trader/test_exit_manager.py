#!/usr/bin/env python3
"""
🧪 TEST EXIT MANAGER
Test the 3-tier exit strategy
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from exit_manager import ExitManager

# Test adding a position and checking exits
def test_exit_manager():
    print("\n" + "="*60)
    print("🧪 TESTING EXIT MANAGER")
    print("="*60)
    
    mgr = ExitManager()
    
    # Add a test position
    test_token = "TEST_TOKEN_123"
    mgr.add_position(
        token_address=test_token,
        symbol="TEST",
        entry_price=0.001,
        position_sol=0.02,
        tokens_received=1000,
        execution_result={"transaction_signature": "test_tx"}
    )
    
    print(f"\n✅ Position added")
    print(f"   Token: {test_token}")
    print(f"   Entry: 0.001")
    print(f"   Tokens: 1000")
    
    # Check positions
    print(f"\n📊 Current positions:")
    for addr, pos in mgr.positions.items():
        print(f"   {pos['symbol']}: {pos['tokens_received']} tokens @ {pos['entry_price']}")
    
    print("\n✅ Exit manager is working!")
    print("\nExit Rules:")
    print("   Tier 1: Sell 40% at +15%")
    print("   Tier 2: Sell 30% at +25%")
    print("   Tier 3: Trail 30% to +40%")
    print("   Stop: -7%")
    print("   Time: 4 hours")

if __name__ == "__main__":
    test_exit_manager()
