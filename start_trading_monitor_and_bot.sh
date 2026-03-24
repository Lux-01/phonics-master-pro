#!/bin/bash
# Start Swing Trader Monitor + Bot together
# Usage: bash start_trading_monitor_and_bot.sh
# Or set as cron to run at 11:55 PM daily

cd /home/skux/.openclaw/workspace/solana-trader

cd /home/skux/.openclaw/workspace/solana-trader

echo "🚀 Starting Swing Trader Monitor + Bot..."
echo ""

# Start monitor server in background
echo "[1/3] Starting monitor server..."
nohup node monitor_server.js > trading_logs/monitor_server.log 2>&1 &
sleep 2

# Check if monitor started
if pgrep -f "monitor_server.js" > /dev/null; then
    echo "✅ Monitor server running on http://localhost:8080"
else
    echo "❌ Monitor failed to start"
    exit 1
fi

# Wait until midnight (trading window starts)
echo ""
echo "[2/3] Waiting for trading window (12:00 AM)..."
current_hour=$(date +%H)
while [ "$current_hour" != "00" ]; do
    echo "   Current time: $(date '+%H:%M') - waiting..."
    sleep 30
    current_hour=$(date +%H)
done

# Start the trading bot
echo ""
echo "[3/3] Starting swing bot v2.3..."
nohup node swing_bot_v2.3.js >> trading_logs/swing_bot_$(date +%Y%m%d).log 2>&1 &
sleep 2

# Check if bot started
if pgrep -f "swing_bot_v2.3.js" > /dev/null; then
    echo "✅ Swing bot started successfully"
else
    echo "❌ Bot failed to start"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "👀 Monitor Dashboard: http://localhost:8080"
echo "🤖 Bot Log: tail -f trading_logs/swing_bot_$(date +%Y%m%d).log"
echo "🛑 To stop: pkill -f 'monitor_server.js'; pkill -f 'swing_bot_v2.3.js'"
echo "════════════════════════════════════════════════"