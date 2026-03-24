#!/bin/bash
# Trading Agent Wrapper - Runs agent and sends alerts via Telegram

cd /home/skux/.openclaw/workspace

# Run the agent in background and capture output
python3 trading_agent_v2.py > /tmp/trading_agent.log 2>&1 &
PID=$!

echo "Trading Agent started (PID: $PID) at $(date)"
echo "Log file: /tmp/trading_agent.log"

# Keep the process running - cron will manage this
sleep 14400  # 4 hours = trading window duration

# Kill the agent after 4 hours
if kill -0 $PID 2>/dev/null; then
    kill $PID
    echo "Trading Agent stopped at $(date)"
fi