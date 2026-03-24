#!/bin/bash
# Start Raphael Monitor v4.0 - Fixed & Production Ready

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🦎 RAPHAEL MONITOR v4.0 - FIXED & READY                      ║"
echo "║                                                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║   fixes Applied:                                               ║"
echo "║   • Port conflict resolved                                     ║"
echo "║   • Autotrader properly integrated                             ║"
echo "║   • Emergency stop persistence fixed                           ║"
echo "║   • Better error handling                                     ║"
echo "║   • State management improved                                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kill any existing processes on port 3456
echo "🔴 Stopping any existing monitors..."
lsof -t -i:3456 2>/dev/null | xargs -r kill -9 2>/dev/null
pkill -9 -f "monitor_v3" 2>/dev/null
pkill -9 -f "monitor_v4" 2>/dev/null
sleep 2

# Clear old log
echo "🧹 Clearing old logs..."
rm -f /tmp/raphael_monitor_v4.log

# Reset state (fresh start)
read -p "🔄 Reset to zero state? (recommended) [Y/n]: " reset
if [[ -z "$reset" || "$reset" == "Y" || "$reset" == "y" ]]; then
    echo "🔄 Resetting state..."
    rm -f /tmp/raphael_state.json
    rm -f /tmp/raphael_live_state.json
    rm -f /tmp/raphael_emergency_stop
fi

echo ""
echo "🚀 Starting Raphael Monitor v4.0..."
cd /home/skux/.openclaw/workspace/agents/raphael

python3 monitor_v4.py &
echo $! > /tmp/raphael_monitor.pid

PID=$!
sleep 3

echo ""
echo "=============================================="

# Quick health check
if curl -s http://localhost:3456/api/status > /dev/null 2>&1; then
    echo "✅ Monitor v4.0 Started Successfully"
    echo ""
    echo "🌐 Dashboard: http://localhost:3456"
    echo ""
    echo "🎮 COMMANDS:"
    echo "   • Start Trading: Click ▶️ START AUTO-TRADING in dashboard"
    echo "   • Emergency Stop: Click STOP ALL TRADING (red button)"
    echo "   • Reset System: Click 🔄 RESET SYSTEM"
    echo ""
    echo "📊 MONITOR STATUS API:"
    echo "   curl -s http://localhost:3456/api/status | jq"
    echo ""
    echo "📝 LOGS:"
    echo "   tail -f /tmp/raphael_monitor_v4.log"
    echo ""
    echo "🟢 Ready for LIVE trading!"
else
    echo "⚠️  Health check failed - check logs:"
    echo "   tail -20 /tmp/raphael_monitor_v4.log"
    exit 1
fi

echo "=============================================="
echo "Monitor PID: $PID"
echo "=============================================="
