#!/usr/bin/env python3
"""
Check real-time P&L for Skylar positions
"""

import json
import requests
from datetime import datetime

BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BIRDEYE_URL = "https://public-api.birdeye.so"

# Load positions
with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_live_executed.json', 'r') as f:
    data = json.load(f)

positions = [t for t in data['trades'] if t['status'] == 'SUCCESS']

print("="*70)
print("💰 LIVE P&L CHECK - SKYLAR POSITIONS")
print("="*70)
print(f"Checking {len(positions)} positions...")
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*70)

total_pnl_pct = 0
total_pnl_sol = 0

print("\n📊 POSITION BREAKDOWN:")
print("-"*70)

for pos in positions:
    token = pos['token']
    address = pos['tokenAddress']
    entry_sol = float(pos['inputSol'])
    
    print(f"\n🎯 Trade #{pos['tradeNum']}: {token}")
    print(f"   Address: {address}")
    print(f"   Entry: {entry_sol:.4f} SOL")
    
    # Try to get current price from Birdeye
    try:
        url = f"{BIRDEYE_URL}/defi/price?address={address}"
        headers = {"X-API-KEY": BIRDEYE_API_KEY}
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 200:
            price_data = resp.json()
            current_price = price_data.get('data', {}).get('value', 0)
            price_change = price_data.get('data', {}).get('priceChange24h', 0)
            
            # Estimate position value (simplified calc)
            # Since we bought at entry_sol worth, we track relative change
            
            print(f"   Current Price: ${current_price:.8f}")
            print(f"   24h Change: {price_change:+.1f}%")
            
            # Simple P&L estimation based on price change
            # This assumes we got ~fair value at entry
            pnl_pct = price_change
            pnl_sol = entry_sol * (pnl_pct / 100)
            
            total_pnl_pct += pnl_pct
            total_pnl_sol += pnl_sol
            
            status = "🔴 SELL" if pnl_pct >= 15 else ("🔴 CUT" if pnl_pct <= -7 else "🟡 HOLD")
            
            print(f"   💹 Estimated P&L: {pnl_pct:+.1f}% | {pnl_sol:+.4f} SOL")
            print(f"   📍 Status: {status}")
            
            if pnl_pct >= 15:
                print(f"   ✅ TAKE PROFIT! Sell now for +15%!")
            elif pnl_pct <= -7:
                print(f"   ⚠️ STOP HIT! Sell to limit loss at -7%")
                
        else:
            print(f"   ⚠️ Price data unavailable (API status: {resp.status_code})")
            print(f"   🟡 Status: HOLDING - Check manually on Birdeye")
    except Exception as e:
        print(f"   ⚠️ Could not fetch price: {e}")
        print(f"   🟡 Status: HOLDING")

# Summary
avg_pnl_pct = total_pnl_pct / len(positions) if positions else 0

print("\n" + "="*70)
print("📊 PORTFOLIO P&L SUMMARY")
print("="*70)
print(f"Total Invested: {sum(float(p['inputSol']) for p in positions):.4f} SOL")
print(f"Avg Position P&L: {avg_pnl_pct:+.1f}%")
print(f"Est. Total P&L: {total_pnl_sol:+.4f} SOL")

if avg_pnl_pct >= 15:
    print("\n🟢🟢🟢 TAKE PROFIT ON ALL POSITIONS! 🟢🟢🟢")
elif avg_pnl_pct > 0:
    print("\n🟢 In Profit - Monitor for +15% targets")
elif avg_pnl_pct > -7:
    print("\n🟡 Small Loss - Watch for -7% stop")
else:
    print("\n🔴 STOP LOSS HIT - Consider cutting losses")

print("\n✅ Check your wallet on Birdeye:")
print(f"   https://birdeye.so/profile/{data['wallet']}")
print("="*70)
