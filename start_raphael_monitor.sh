#!/bin/bash
# Start Raphael's Monitor

echo "🦎 Starting Raphael's Monitor..."

cd /home/skux/.openclaw/workspace/agents/raphael

# Check if monitor is already running
MONITOR_PID=$(lsof -ti:3456 2>/dev/null || echo "")
if [ -n "$MONITOR_PID" ]; then
    echo "⚠️  Monitor already running on PID $MONITOR_PID"
    echo "   Visit: http://localhost:3456"
    exit 0
fi

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║         🦎 RAPHAEL MONITOR v1.0          ║"
echo "╠═══════════════════════════════════════════╣"
echo "║  Raphael is LIVE                         ║"
echo "║  Mission: 1 SOL → 50 SOL                ║"
echo "║                                           ║"
echo "║  Monitor URL: http://localhost:3456    ║"
echo "║                                           ║"
echo "║  Press Ctrl+C to stop monitor            ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Start monitor
node monitor_bridge.js
