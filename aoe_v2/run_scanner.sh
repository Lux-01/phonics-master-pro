#!/bin/bash
# AOE v2 Scanner - Cron wrapper script
# Runs every 30 minutes

LOG_FILE="/tmp/aoe_scan_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="/tmp/aoe_scan.pid"

# Prevent overlapping runs
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "[$(date)] Scan already running (PID: $PID), skipping..." >> "$LOG_FILE"
        exit 0
    fi
fi

echo $$ > "$PID_FILE"

cd /home/skux/.openclaw/workspace/aoe_v2 || exit 1

{
    echo "========================================"
    echo "AOE Scan Started: $(date)"
    echo "========================================"
    
    # Run scanner with verbose output
    python3 main.py --mode scan --verbose 2>&1
    
    EXIT_CODE=$?
    
    echo ""
    echo "Exit code: $EXIT_CODE"
    echo "Completed: $(date)"
    echo "========================================"
} >> "$LOG_FILE" 2>&1

rm -f "$PID_FILE"

# Keep only last 20 log files
find /tmp -name 'aoe_scan_*.log' -type f -mtime +1 -delete 2>/dev/null

exit 0
