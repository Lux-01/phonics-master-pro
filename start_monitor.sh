#!/bin/bash
# Start Raphael Monitor with Status Light

cd /home/skux/.openclaw/workspace/agents/raphael

# Kill any existing monitor
pkill -f "simple_monitor.py" 2>/dev/null
pkill -f "monitor_bridge.js" 2>/dev/null

sleep 1

# Start the Python monitor in background, detached from terminal
nohup python3 simple_monitor.py > /tmp/raphael_monitor.log 2>&1 &
disown

echo "Monitor started on PID: $!"
echo "URL: http://localhost:3456"
echo ""
echo "To stop: pkill -f simple_monitor.py"
