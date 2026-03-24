#!/bin/bash
# Raphael Monitor Watchdog
# Restarts the monitor if it dies

LOG="/tmp/raphael_monitor.log"
PID_FILE="/tmp/raphael_monitor.pid"

check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

start_monitor() {
    echo "[$(date)] Starting Raphael monitor..." >> "$LOG"
    cd /home/skux/.openclaw/workspace/agents/raphael
    nohup node monitor_bridge.js >> "$LOG" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 2
    if curl -s http://localhost:3456/api/status >/dev/null 2>&1; then
        echo "✅ Monitor started successfully"
        return 0
    else
        echo "❌ Monitor failed to start"
        return 1
    fi
}

case "${1:-start}" in
    start)
        if check_running; then
            echo "Monitor already running (PID $(cat $PID_FILE))"
            echo "Dashboard: http://localhost:3456"
            exit 0
        fi
        start_monitor
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm "$PID_FILE"
            echo "Monitor stopped"
        fi
        ;;
    status)
        if check_running; then
            echo "✅ Running (PID $(cat $PID_FILE))"
            curl -s http://localhost:3456/api/status | jq '{balance, positions: (.positions | length)}' 2>/dev/null || echo "Status unavailable"
        else
            echo "❌ Not running"
        fi
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    watch)
        # Run watchdog loop
        echo "Starting watchdog loop..."
        while true; do
            if ! check_running; then
                echo "[$(date)] Monitor down, restarting..." >> "$LOG"
                start_monitor
            fi
            sleep 10
        done
        ;;
esac