#!/bin/bash
# Raphael Auto-Trader Watchdog
# Restarts autotrader if it dies

cd /home/skux/.openclaw/workspace/agents/raphael

echo "🦎 Raphael Watchdog Starting..."
echo "================================"
echo "Logs: /tmp/raphael_autotrader.log"
echo "Errors: /tmp/raphael_errors.log"
echo "================================"

while true; do
    echo "$(date '+%H:%M:%S') - Checking if autotrader is running..."
    
    # Check if already running
    if pgrep -f "python3.*raphael_autotrader.py" > /dev/null; then
        echo "$(date '+%H:%M:%S') - Autotrader already running, waiting..."
        sleep 30
        continue
    fi
    
    echo "$(date '+%H:%M:%S') - Starting autotrader..."
    
    # Start autotrader with full error capture
    python3 -u raphael_autotrader.py >> /tmp/raphael_autotrader.log 2>> /tmp/raphael_errors.log
    EXIT_CODE=$?
    
    echo "$(date '+%H:%M:%S') - Autotrader exited with code $EXIT_CODE"
    
    # Log the crash
    echo "[$(date)] CRASH: Exit code $EXIT_CODE" >> /tmp/raphael_crashes.log
    
    echo "$(date '+%H:%M:%S') - Waiting 10 seconds before restart..."
    sleep 10
done
