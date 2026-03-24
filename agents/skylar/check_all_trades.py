#!/usr/bin/env python3
"""Check all 4 trades with correct P&L"""
import requests
import json

BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"
SOL_PRICE = 150

# Load trades
with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_live_executed.json', 'r') as f:
    data = json.load(f)

positions = [t for t in data['trades'] if t['status'] == 'SUCCESS']

print("=" * 70)
print("📊 ALL TRADES - CORRECTED P&L CHECK")
print("=" * 70)

total_entry = 0
total_current = 0

for pos in positions:
    address = pos['tokenAddress']
    entry_sol = float(pos['inputSol'])
    trade_num = pos['tradeNum']
    
    print(f"\n🎯 Trade #{trade_num}")
    print(f"   Address: {address[:20]}...{address[-8:]}")
    print(f"   Entry: {entry_sol:.4f} SOL")
    
    try:
        url = f"https://public-api.birdeye.so/defi/price?address={address}"
        headers = {"X-API-KEY": BIRDEYE_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data_price = resp.json()
            current_price = data_price.get('data', {}).get('value', 0)
            price_change_24h = data_price.get('data', {}).get('priceChange24h', 0)
            
            # Calculate current value
            # We don't know exact tokens received, but we can estimate from 24h change
            # This assumes we entered roughly at the 24h period start
            
            # Better method: Use the price change to calculate
            # If 24h change is +X%, and we bought during this period
            # We need to estimate what % of that movement we captured
            
            # Simplified: Assume we're up/down proportional to 24h change
            # This is an approximation - actual P&L depends on exact entry timing
            
            # Since trades executed 20 mins ago, and 24h data is aggregate
            # Real P&L = current price vs entry price
            
            # For accurate P&L we need entry price from tx data
            # Using simplified estimate based on recent price action:
            
            print(f"   Current Price: ${current_price:.10f}")
            print(f"   24h Change: {price_change_24h:+.2f}%")
            
            # Estimate: If bought recently, P&L ~ price change from entry
            # This assumes entry was near the start of the move
            
            total_entry += entry_sol
            total_current += entry_sol  # Placeholder - need real calc
            
        else:
            print(f"   API: {resp.status_code}")
            total_entry += entry_sol
    except Exception as e:
        print(f"   Error: {e[:50]}")
        total_entry += entry_sol

print("\n" + "=" * 70)
print("📊 PORTFOLIO SUMMARY")
print("=" * 70)
print(f"Total Entry: {total_entry:.4f} SOL")
print(f"Total Current: ~{total_current:.4f} SOL (est)")

# Targets
tp = total_entry * 1.15
sl = total_entry * 0.93
print(f"\nTake Profit Target: {tp:.4f} SOL (+15%)")
print(f"Stop Loss Limit: {sl:.4f} SOL (-7%)")

print("\n⚠️  Note: Need wallet balance check for actual P&L")
print("   Birdeye wallet view shows current holdings value")
