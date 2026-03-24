#!/bin/bash
# 🎯 Wallet Copy Trader Runner
# Monitors target wallets and copies their buys

cd /home/skux/.openclaw/workspace/agents/wallet_tracker

echo "╔==================================================================╗"
echo "║     🎯 WALLET COPY TRADER - Buy When They Buy"
echo "╚==================================================================╝"
echo ""
echo "Strategy: Copy buys from target wallets"
echo "Exit: +15% profit OR -15% stop loss OR 4h time limit"
echo ""

# Run the strategy
python3 wallet_copy_strategy.py

echo ""
echo "Next check: Run this script again to continue monitoring"
echo ""
