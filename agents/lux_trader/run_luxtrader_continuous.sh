#!/bin/bash
# LuxTrader v3.0 - Continuous Trading System
# Runs every 5 minutes to catch all signals

LOG_FILE="/tmp/luxtrader_continuous.log"
STATE_FILE="/home/skux/.openclaw/workspace/agents/lux_trader/live_state.json"

echo "$(date): Starting LuxTrader continuous scan..." >> $LOG_FILE

cd /home/skux/.openclaw/workspace/agents/lux_trader

# Check if already running
if pgrep -f "luxtrader_live.py" > /dev/null; then
    echo "$(date): LuxTrader already running, skipping..." >> $LOG_FILE
    exit 0
fi

# Run LuxTrader
python3 luxtrader_live.py >> $LOG_FILE 2>&1

echo "$(date): LuxTrader scan complete" >> $LOG_FILE
