#!/usr/bin/env python3
"""
🚀 UNIVERSAL SELL EXECUTOR
Tries multiple methods in order:
1. Jupiter Ultra API
2. Jupiter Standard API
3. Raydium Direct
4. Pump.fun Direct
5. Manual fallback
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from typing import Dict
from ultra_executor import execute_sell_ultra
from full_auto_executor import execute_sell_auto
from raydium_executor import execute_sell_raydium
from pumpfun_executor import execute_sell_pumpfun

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"


def execute_universal_sell(token_address: str, amount_tokens: float,
                           token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """
    Try all sell methods in order of preference
    """
    print(f"\n{'='*60}")
    print("🚀 UNIVERSAL SELL EXECUTOR")
    print(f"{'='*60}")
    print(f"Token: {token_symbol}")
    print(f"Amount: {amount_tokens:.6f} tokens")
    print(f"Wallet: {WALLET}")
    
    results = []
    
    # Method 1: Jupiter Ultra API
    print(f"\n📍 Method 1: Jupiter Ultra API")
    try:
        result = execute_sell_ultra(WALLET, token_address, amount_tokens, token_symbol, token_decimals)
        results.append(("Ultra API", result))
        if result.get('status') == 'executed':
            print("✅ Ultra API SUCCESS!")
            return result
        print(f"⚠️ Ultra failed: {result.get('error', result.get('message', 'Unknown'))}")
    except Exception as e:
        print(f"❌ Ultra exception: {e}")
        results.append(("Ultra API", {'status': 'failed', 'error': str(e)}))
    
    # Method 2: Jupiter Standard API
    print(f"\n📍 Method 2: Jupiter Standard API")
    try:
        result = execute_sell_auto(WALLET, token_address, amount_tokens, token_symbol)
        results.append(("Standard API", result))
        if result.get('status') == 'executed':
            print("✅ Standard API SUCCESS!")
            return result
        print(f"⚠️ Standard failed: {result.get('error', result.get('message', 'Unknown'))}")
    except Exception as e:
        print(f"❌ Standard exception: {e}")
        results.append(("Standard API", {'status': 'failed', 'error': str(e)}))
    
    # Method 3: Raydium Direct
    print(f"\n📍 Method 3: Raydium Direct")
    try:
        result = execute_sell_raydium(WALLET, token_address, amount_tokens, token_symbol, token_decimals)
        results.append(("Raydium", result))
        if result.get('status') == 'executed':
            print("✅ Raydium SUCCESS!")
            return result
        print(f"⚠️ Raydium not available: {result.get('message', 'Not implemented')}")
    except Exception as e:
        print(f"❌ Raydium exception: {e}")
        results.append(("Raydium", {'status': 'failed', 'error': str(e)}))
    
    # Method 4: Pump.fun Direct
    print(f"\n📍 Method 4: Pump.fun Direct")
    try:
        result = execute_sell_pumpfun(WALLET, token_address, amount_tokens, token_symbol)
        results.append(("Pump.fun", result))
        if result.get('status') == 'executed':
            print("✅ Pump.fun SUCCESS!")
            return result
        print(f"⚠️ Pump.fun not available: {result.get('message', 'Not implemented')}")
    except Exception as e:
        print(f"❌ Pump.fun exception: {e}")
        results.append(("Pump.fun", {'status': 'failed', 'error': str(e)}))
    
    # All methods failed
    print(f"\n{'='*60}")
    print("❌ ALL METHODS FAILED")
    print(f"{'='*60}")
    
    # Return best fallback (manual link)
    manual_url = f"https://jup.ag/swap/{token_address}-SOL"
    
    return {
        "status": "manual_required",
        "message": "All automated methods failed",
        "manual_url": manual_url,
        "results": results
    }


def test_universal_sell(token_address: str, amount_tokens: float, token_symbol: str = "TEST"):
    """Test the universal sell executor"""
    result = execute_universal_sell(token_address, amount_tokens, token_symbol)
    
    print(f"\n{'='*60}")
    print("📊 FINAL RESULT")
    print(f"{'='*60}")
    print(f"Status: {result.get('status')}")
    
    if result.get('status') == 'executed':
        print(f"✅ SUCCESS!")
        print(f"Tx: {result.get('transaction_signature', 'N/A')}")
        print(f"Explorer: {result.get('explorer_url', 'N/A')}")
    else:
        print(f"⚠️ Manual execution required")
        print(f"URL: {result.get('manual_url', 'N/A')}")
    
    return result


if __name__ == "__main__":
    import json
    
    print("Universal Sell Executor Test")
    print("="*60)
    
    # Test with the migrated token
    token = "CnN6E68w6QytynScJbHUzBFDpPged8dneVji8oqMpump"
    amount = 5151.86
    
    result = test_universal_sell(token, amount, "TEST")
    
    print(f"\nFull result:\n{json.dumps(result, indent=2, default=str)}")
