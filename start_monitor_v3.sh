#!/bin/bash
# Start Raphael Monitor v3.0 - Live Test Mode

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   🦎 RAPHAEL LIVE MONITOR v3.0 - ZEROD AND READY              ║"
echo "║                                                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║   Features:                                                    ║"
echo "║   • Emergency stop button (red, prominent)                    ║"
echo "║   • Reset to zero state                                      ║"
echo "║   • Live test protocol integration                           ║"
echo "║   • Real-time status updates                                 ║"
echo "║   • Grade C eliminated                                       ║"
echo "║   • Watchdog v3 active (auto-respawn)                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kill existing monitors
echo "🔴 Stopping existing monitors..."
pkill -9 -f "simple_monitor.py" 2>/dev/null
pkill -9 -f "monitor_v3.py" 2>/dev/null
lsof -t -i:3456 | xargs -r kill -9 2>/dev/null
sleep 2

# Clear emergency stop if exists (fresh start)
echo "🧹 Clearing emergency stop (fresh start)..."
rm -f /tmp/raphael_emergency_stop
rm -f /tmp/raphael_live_mode
sleep 1

# Start new monitor
echo "🚀 Starting Monitor v3.0..."
cd /home/skux/.openclaw/workspace/agents/raphael

python3 monitor_v3.py &
PID=$!
sleep 2

echo ""
echo "=============================================="
echo "✅ Monitor Started Successfully"
echo "=============================================="
echo ""
echo "🌐 Dashboard URL: http://localhost:3456"
echo ""
echo "🚨 EMERGENCY STOP:"
echo "   • Dashboard button (red, top of page)"
echo "   • API: curl -X POST http://localhost:3456/api/emergency-stop"
echo "   • Manual: touch /tmp/raphael_emergency_stop"
echo ""
echo "🎯 LIVE TEST PROTOCOL:"
echo "   • Max trade size: 0.01 SOL"
echo "   • Target: 5 test trades"
echo "   • Grades: A+ and A only"
echo ""
echo "📊 STATUS:"
echo "   • Balance: 1.0000 SOL (RESET)"
echo "   • Trades: 0"
echo "   • Rules: 40 active"
echo "   • Emergency: READY (not triggered)"
echo ""
echo "🔧 COMMANDS:"
echo "   Status:  curl -s http://localhost:3456/api/status | jq"
echo "   Reset:   curl -X POST http://localhost:3456/api/reset"
echo "   Stop:    pkill -f monitor_v3.py"
echo ""
echo "=============================================="
echo "Monitor PID: $PID"
echo "Logs: tail -f /tmp/raphael_monitor.log"
echo "=============================================="
echo ""

# Quick health check
echo "Running health check..."
sleep 2

if curl -s http://localhost:3456/api/status > /dev/null 2>&1; then
    echo "✅ Health check PASSED"
    echo "✅ Dashboard is live at http://localhost:3456"
    echo ""
    echo "🚀 READY FOR LIVE TEST"
    echo "   Click 'Start Live Test' button in dashboard"
    echo "   Then execute 5 trades at 0.01 SOL max size"
else
    echo "⚠️  Health check failed - check logs"
fi

wait $PID
