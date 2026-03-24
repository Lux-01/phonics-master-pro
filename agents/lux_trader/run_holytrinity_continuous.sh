#!/bin/bash
# Holy Trinity - Continuous Trading System
# Runs every 5 minutes to catch all signals

LOG_FILE="/tmp/holytrinity_continuous.log"

echo "$(date): Starting Holy Trinity continuous scan..." >> $LOG_FILE

cd /home/skux/.openclaw/workspace/agents/lux_trader

# Check if already running
if pgrep -f "holy_trinity_live.py" > /dev/null; then
    echo "$(date): Holy Trinity already running, skipping..." >> $LOG_FILE
    exit 0
fi

# Run Holy Trinity
python3 holy_trinity_live.py >> $LOG_FILE 2>&1

echo "$(date): Holy Trinity scan complete" >> $LOG_FILE
