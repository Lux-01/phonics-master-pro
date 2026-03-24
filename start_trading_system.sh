#!/bin/bash
# Combined Trading System - Runs both agent and alert daemon

cd /home/skux/.openclaw/workspace
echo "Starting Solana Trading Agent v2.0..."
echo "Time: $(date)"
echo "Timezone: $(timedatectl | grep Timezone)"
echo "============================================="

# Start the alert daemon in background (captures signals)
python3 telegram_alerts_daemon.py &
DAEMON_PID=$!
echo "Alert daemon started (PID: $DAEMON_PID)"

# Run the trading agent (4 hour session)
python3 trading_agent_v2.py &
AGENT_PID=$!
echo "Trading agent started (PID: $AGENT_PID)"

# Wait for main agent (4 hours)
wait $AGENT_PID

# Clean up daemon
if kill -0 $DAEMON_PID 2>/dev/null; then
    kill $DAEMON_PID
fi

echo "Trading session complete at $(date)"
echo "Check /tmp/trading_signals.json for all signals"