#!/usr/bin/env python3
"""Test learning by simulating trade outcomes"""
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from lux_trader import LuxTrader
from learning_engine import LearningEngine
from pathlib import Path

print("🧪 Testing Learning Engine\n")

trader = LuxTrader()

# Simulate 5 trades with outcomes
test_scenarios = [
    {'symbol': 'WIN1', 'address': 'W1', 'price': 0.001, 'score': 85, 'outcome_pnl': +0.15},   # Win
    {'symbol': 'WIN2', 'address': 'W2', 'price': 0.0005, 'score': 82, 'outcome_pnl': +0.22},  # Big win
    {'symbol': 'LOSS1', 'address': 'L1', 'price': 0.002, 'score': 78, 'outcome_pnl': -0.07}, # Stop loss
    {'symbol': 'WIN3', 'address': 'W3', 'price': 0.0015, 'score': 80, 'outcome_pnl': +0.18},  # Win
    {'symbol': 'LOSS2', 'address': 'L2', 'price': 0.0008, 'score': 76, 'outcome_pnl': -0.07}, # Stop loss
]

for i, scenario in enumerate(test_scenarios, 1):
    # Create trade
    trade = trader.execute_paper_trade(scenario)
    if trade:
        # Simulate price movement
        exit_price = trade.entry_price * (1 + scenario['outcome_pnl'])
        trade.exit_price = exit_price
        trade.exit_time = __import__('datetime').datetime.now().isoformat()
        trade.pnl_pct = scenario['outcome_pnl']
        trade.status = 'CLOSED'
        trade.outcome = 'win' if scenario['outcome_pnl'] > 0 else 'loss'
        trade.exit_reason = 'target_hit' if scenario['outcome_pnl'] > 0 else 'stop_loss'
        
        print(f"✅ Trade #{i}: {scenario['symbol']} → {scenario['outcome_pnl']:+.0%}")

# Save trades
from dataclasses import asdict
import json

trader.portfolio.clear()  # Clear open positions
with open(trader.trades_file, 'w') as f:
    json.dump([asdict(t) for t in trader.trades], f, indent=2)

print("\n📊 Performance Summary:")
trader.print_status()

print("\n🧠 Running Learning Engine:")
print("=" * 60)
engine = LearningEngine(trader.data_dir)
analysis = engine.analyze()

if 'error' not in analysis:
    print("\n🔄 Evolving Strategy:")
    engine.evolve_strategy(analysis)
    
    print("\n💡 Final Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")

print("=" * 60)
print("\n📁 Files created:")
for f in trader.data_dir.glob('*.json'):
    print(f"  {f.name}")
