#!/usr/bin/env python3
"""
SKYLAR POSITION TRACKER
Monitor active positions and show P&L with exit signals
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List

# Load executed trades
with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_live_executed.json', 'r') as f:
    data = json.load(f)

# Filter successful trades
positions = [t for t in data['trades'] if t['status'] == 'SUCCESS']

print("="*70)
print("📊 SKYLAR POSITION TRACKER")
print("="*70)
print(f"Wallet: {data['wallet']}")
print(f"Total Positions: {len(positions)}")
print(f"Strategy: 15% Take Profit | -7% Stop Loss")
print("="*70)

# Show each position with exit levels
print("\n📈 CURRENT POSITIONS:")
print("-"*70)

for pos in positions:
    entry_time = pos['timestamp']
    token = pos['token']
    address = pos['tokenAddress']
    entry_sol = float(pos['inputSol'])
    grade = pos['grade']
    score = pos['score']
    
    # Calculate exit levels
    tp_price = entry_sol * 1.15  # +15%
    sl_price = entry_sol * 0.93  # -7%
    
    print(f"\n🎯 Trade #{pos['tradeNum']}")
    print(f"   Token: {token}")
    print(f"   Address: {address}")
    print(f"   Grade: {grade} (Score: {score})")
    print(f"   Entry: {entry_sol:.4f} SOL at {entry_time}")
    print(f"   Current: HOLDING 🟡")
    print(f"   📈 Take Profit (+15%): Sell when worth {tp_price:.4f} SOL")
    print(f"   📉 Stop Loss (-7%): Sell if drops to {sl_price:.4f} SOL")
    print(f"   💵 Exit USD Value: ~${entry_sol * 150:.2f} (est $150/SOL)")
    print(f"   🔗 Tx: {pos['solscanLink']}")

# Summary
print("\n" + "="*70)
print("📊 PORTFOLIO SUMMARY")
print("="*70)

total_invested = sum(float(p['inputSol']) for p in positions)
target_profit = total_invested * 0.15  # +15%
max_loss = total_invested * 0.07      # -7%

print(f"\nTotal Invested: {total_invested:.4f} SOL")
print(f"Target Profit (+15%): +{target_profit:.4f} SOL")
print(f"Max Risk (-7%): -{max_loss:.4f} SOL")
print(f"Target Portfolio Value: {total_invested + target_profit:.4f} SOL")
print(f"Stop Loss Portfolio Value: {total_invested - max_loss:.4f} SOL")

# Time tracking
print(f"\n⏰ Time Since Entry:")
entry_time = datetime.fromisoformat(positions[0]['timestamp'].replace('Z', '+00:00'))
now = datetime.now(entry_time.tzinfo)
elapsed = now - entry_time
print(f"   {elapsed.seconds // 60} minutes ago")

# Exit strategy
print("\n" + "="*70)
print("🎯 EXIT STRATEGY")
print("="*70)
print("""
IMMEDIATE ACTIONS NEEDED:

✅ MONITOR THESE LEVELS:
   • Use Birdeye or DexScreener to check token prices
   • Wallet: 8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5

✅ SELL WHEN:
   • ANY token hits +15% → Take profit immediately
   • ANY token drops -7% → Cut loss immediately
   • 4 hours pass → Time stop, evaluate then sell

✅ QUICK CHECK:
   1. Go to birdeye.so
   2. Connect wallet
   3. View token positions
   4. Watch for +15% or -7%
   5. Swap back to SOL via Jupiter when target hit

✅ CURRENT STATUS:
   🟡 HOLDING - Waiting for exit signal
   🟢 SELL when +15%
   🔴 SELL when -7%
""")

# Create exit tracker JSON
exit_data = {
    "timestamp": datetime.now().isoformat(),
    "wallet": data['wallet'],
    "total_positions": len(positions),
    "total_invested_sol": total_invested,
    "take_profit_target": total_invested * 1.15,
    "stop_loss_limit": total_invested * 0.93,
    "target_pnl_sol": target_profit,
    "max_loss_sol": max_loss,
    "positions": [
        {
            "trade_num": p['tradeNum'],
            "token": p['token'],
            "address": p['tokenAddress'],
            "entry_sol": float(p['inputSol']),
            "take_profit_sol": float(p['inputSol']) * 1.15,
            "stop_loss_sol": float(p['inputSol']) * 0.93,
            "entry_time": p['timestamp'],
            "solscan": p['solscanLink']
        }
        for p in positions
    ]
}

with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_exit_tracker.json', 'w') as f:
    json.dump(exit_data, f, indent=2)

print("\n✅ Exit tracker saved: skylar_exit_tracker.json")
print("="*70)
