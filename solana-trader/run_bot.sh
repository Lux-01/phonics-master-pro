#!/bin/bash
cd /home/skux/.openclaw/workspace/solana-trader
while true; do
  echo "[$(date)] Starting bot..." >> trading_logs/swing_bot_20260222.log
  node swing_bot.js 2>&1 | tee -a trading_logs/swing_bot_20260222.log
  echo "[$(date)] Bot crashed, restarting in 5 seconds..." >> trading_logs/swing_bot_20260222.log
  sleep 5
done
