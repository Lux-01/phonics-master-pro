#!/usr/bin/env python3
"""
🧪 LUXTRADER LIVE TRADE TEST
One-time manual trade to verify execution works

Token: 9898Wt5zireT7UfkPgGC9yMdYjjohEeagTQXVrQGpump
Amount: 0.001 SOL (~$0.15)
Action: Test connectivity and show manual instructions
"""

import requests
import json
import time
from datetime import datetime

# CONFIG
TEST_TOKEN = "9898Wt5zireT7UfkPgGC9yMdYjjohEeagTQXVrQGpump"
SOL_MINT = "So11111111111111111111111111111111111111112"
AMOUNT_SOL = 0.001
AMOUNT_LAMPORTS = int(AMOUNT_SOL * 1e9)
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

JUPITER_API = "https://quote-api.jup.ag/v6"

def log_trade(action, data):
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "test": "LIVE_EXECUTION_VERIFY",
        "action": action,
        "token": TEST_TOKEN,
        "amount_sol": AMOUNT_SOL,
        "wallet": WALLET,
        "data": data
    }
    with open("/home/skux/.openclaw/workspace/test_live_trade.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    print(f"📝 Logged: {action}")

def test_execution():
    print("=" * 60)
    print("🧪 LUXTRADER LIVE TRADE TEST")
    print("=" * 60)
    print(f"Token: {TEST_TOKEN}")
    print(f"Amount: {AMOUNT_SOL} SOL (~${AMOUNT_SOL * 150:.2f})")
    print(f"Wallet: {WALLET}")
    print("=" * 60)
    
    log_trade("START", {"message": "Test trade initiated"})
    
    # Step 1: Check API connectivity
    print("\n📡 Step 1: Testing Jupiter API connectivity...")
    try:
        test_url = f"{JUPITER_API}/quote"
        test_params = {
            "inputMint": SOL_MINT,
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "amount": AMOUNT_LAMPORTS,
            "slippageBps": 250
        }
        
        response = requests.get(test_url, params=test_params, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Jupiter API is reachable")
            log_trade("API_CHECK", {"status": "reachable"})
        else:
            print(f"   ⚠️ API returned: {response.status_code}")
            log_trade("API_CHECK", {"status": "error", "code": response.status_code})
    except Exception as e:
        print(f"   ❌ Cannot reach Jupiter API: {e}")
        log_trade("API_CHECK", {"status": "failed", "error": str(e)})
    
    # Step 2: Get quote for target token
    print(f"\n📊 Step 2: Getting quote for target token...")
    try:
        quote_params = {
            "inputMint": SOL_MINT,
            "outputMint": TEST_TOKEN,
            "amount": AMOUNT_LAMPORTS,
            "slippageBps": 250
        }
        
        response = requests.get(test_url, params=quote_params, timeout=15)
        
        if response.status_code == 200:
            quote = response.json()
            out_amount = int(quote.get('outAmount', 0))
            price_impact = quote.get('priceImpactPct', '0')
            
            # Estimate decimals
            token_decimals = 9 if out_amount > 1e9 else 6
            expected_out = out_amount / (10 ** token_decimals)
            
            print(f"   ✅ Quote received:")
            print(f"      Expected output: {expected_out:.6f} tokens")
            print(f"      Price impact: {price_impact}%")
            print(f"      Route: {len(quote.get('routePlan', []))} hops")
            
            log_trade("QUOTE", {
                "input_sol": AMOUNT_SOL,
                "expected_output": expected_out,
                "price_impact": price_impact
            })
            
            show_next_steps(expected_out, price_impact)
            
        else:
            print(f"   ❌ Quote failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            log_trade("QUOTE", {"status": "failed", "code": response.status_code})
            
    except Exception as e:
        print(f"   ❌ Quote error: {e}")
        log_trade("QUOTE", {"status": "error", "error": str(e)})

def show_next_steps(expected_out, price_impact):
    print("\n" + "=" * 60)
    print("⚠️  CRITICAL LIMITATION")
    print("=" * 60)
    print()
    print("✅ GOOD NEWS:")
    print("   • Jupiter API is reachable")
    print("   • Trading infrastructure works")
    print("   • Quotes are working")
    print()
    print("❌ THE PROBLEM:")
    print("   I cannot EXECUTE trades because:")
    print("   1. No private key access")
    print("   2. Cannot sign transactions")
    print("   3. No wallet integration")
    print()
    print("=" * 60)
    print("🎯 TO ACTUALLY TRADE, USE ONE OF THESE:")
    print("=" * 60)
    print()
    print("Option 1: Jupiter Web (Easiest)")
    print("-" * 40)
    print(f"1. Open: https://jup.ag")
    print(f"2. Connect your wallet")
    print(f"3. Swap SOL → {TEST_TOKEN[:30]}...")
    print(f"4. Amount: {AMOUNT_SOL} SOL")
    print(f"5. Execute swap")
    print(f"6. Save transaction signature")
    print()
    print("Option 2: Phantom Wallet")
    print("-" * 40)
    print(f"1. Open Phantom extension")
    print(f"2. Go to Swap")
    print(f"3. From: SOL")
    print(f"4. To: Paste token address")
    print(f"   {TEST_TOKEN}")
    print(f"5. Amount: {AMOUNT_SOL}")
    print(f"6. Click Swap")
    print()
    print("=" * 60)
    print("After trading, send me the transaction signature!")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Starting LuxTrader Live Execution Test\n")
    test_execution()
    print("\n📝 Full log saved to: test_live_trade.json")
