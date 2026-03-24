#!/bin/bash
# Restart Raphael Monitor with all new features

echo "🦎 Restarting Raphael Monitor..."

# Kill existing
pkill -9 -f "simple_monitor.py" 2>/dev/null
lsof -t -i:3456 | xargs -r kill -9 2>/dev/null
sleep 1

# Start new instance
cd /home/skux/.openclaw/workspace/agents/raphael
python3 simple_monitor.py &
PID=$!
echo "✅ Monitor started on PID: $PID"
echo ""
echo "Dashboard: http://localhost:3456"
echo ""
echo "Features:"
echo "  • Green/red status light for Raphael"
echo "  • Mint addresses in positions"
echo "  • Rug check status display"
echo "  • Auto-refreshes every 3 seconds"
echo ""
echo "To stop: pkill -f simple_monitor.py"
echo "Logs: tail -f /tmp/raphael_monitor.log"
