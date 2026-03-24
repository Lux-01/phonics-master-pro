#!/bin/bash
# 🔥 RUN HOLY TRINITY + LUXTRADER v3.0 IN PARALLEL

SCRIPT_DIR="/home/skux/.openclaw/workspace/agents/lux_trader"
LOG_DIR="/home/skux/.openclaw/workspace/agents/lux_trader/parallel_logs"
mkdir -p "$LOG_DIR"

echo "=================================="
echo "🔥 PARALLEL TRADING SYSTEMS"
echo "=================================="
echo ""

# Check if LuxTrader is running
echo "Checking LuxTrader v3.0..."
LUXTRADER_PID=$(pgrep -f "luxtrader_live.py" || echo "")

if [ -z "$LUXTRADER_PID" ]; then
    echo "⚠️  LuxTrader v3.0 not running"
    echo "Starting LuxTrader v3.0..."
    cd "$SCRIPT_DIR"
    python3 luxtrader_live.py > "$LOG_DIR/luxtrader_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
    LUXTRADER_PID=$!
    echo "✅ LuxTrader started (PID: $LUXTRADER_PID)"
else
    echo "✅ LuxTrader v3.0 already running (PID: $LUXTRADER_PID)"
fi

echo ""
echo "Starting Holy Trinity..."

# Check if Holy Trinity is already running
TRINITY_PID=$(pgrep -f "holy_trinity_live.py" || echo "")

if [ -z "$TRINITY_PID" ]; then
    cd "$SCRIPT_DIR"
    python3 holy_trinity_live.py > "$LOG_DIR/holy_trinity_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
    TRINITY_PID=$!
    echo "✅ Holy Trinity started (PID: $TRINITY_PID)"
else
    echo "✅ Holy Trinity already running (PID: $TRINITY_PID)"
fi

echo ""
echo "=================================="
echo "🚀 BOTH SYSTEMS RUNNING"
echo "=================================="
echo ""
echo "LuxTrader v3.0:"
echo "  - Position size: 0.6% of capital"
echo "  - Max trades/day: 5"
echo "  - Signal: Score ≥75"
echo "  - State: $SCRIPT_DIR/live_state.json"
echo ""
echo "Holy Trinity:"
echo "  - Position size: 10.5-11.46% of capital"
echo "  - Max trades/day: 3"
echo "  - Signal: Composite ≥80"
echo "  - State: $SCRIPT_DIR/holy_trinity_state.json"
echo ""
echo "Logs: $LOG_DIR"
echo ""
echo "Commands:"
echo "  ./check_parallel.sh --status    # Check status"
echo "  ./check_parallel.sh --stop      # Stop both"
echo ""
echo "To run a scan:"
echo "  python3 luxtrader_live.py"
echo "  python3 holy_trinity_live.py"
echo ""
echo "PIDs: LuxTrader=$LUXTRADER_PID, HolyTrinity=$TRINITY_PID"
echo "=================================="

# Save PIDs
echo "$LUXTRADER_PID" > "$SCRIPT_DIR/.luxtrader.pid"
echo "$TRINITY_PID" > "$SCRIPT_DIR/.holy_trinity.pid"
