#!/bin/bash
# 🔥 CHECK STATUS OF PARALLEL TRADING SYSTEMS

SCRIPT_DIR="/home/skux/.openclaw/workspace/agents/lux_trader"

echo "=================================="
echo "🔥 PARALLEL SYSTEMS STATUS"
echo "=================================="
echo ""

# Check LuxTrader
echo "📊 LUXTRADER v3.0"
echo "------------------"
LUXTRADER_PID=$(pgrep -f "luxtrader_live.py" || echo "")
if [ -z "$LUXTRADER_PID" ]; then
    echo "Status: ❌ NOT RUNNING"
else
    echo "Status: ✅ RUNNING (PID: $LUXTRADER_PID)"
fi

if [ -f "$SCRIPT_DIR/live_state.json" ]; then
    echo "State file: ✅ Found"
    python3 -c "
import json
with open('$SCRIPT_DIR/live_state.json') as f:
    state = json.load(f)
print(f\"Capital: {state.get('total_capital', 'N/A'):.4f} SOL\")
print(f\"Trades: {state.get('total_trades', 0)}\")
print(f\"Wins: {state.get('wins', 0)} | Losses: {state.get('losses', 0)}\")
print(f\"Daily PnL: {state.get('daily_pnl', 0):.4f} SOL\")
print(f\"Daily Trades: {state.get('daily_trades', 0)}\")
"
else
    echo "State file: ❌ Not found"
fi

echo ""
echo "📊 HOLY TRINITY"
echo "------------------"
TRINITY_PID=$(pgrep -f "holy_trinity_live.py" || echo "")
if [ -z "$TRINITY_PID" ]; then
    echo "Status: ❌ NOT RUNNING"
else
    echo "Status: ✅ RUNNING (PID: $TRINITY_PID)"
fi

if [ -f "$SCRIPT_DIR/holy_trinity_state.json" ]; then
    echo "State file: ✅ Found"
    python3 -c "
import json
with open('$SCRIPT_DIR/holy_trinity_state.json') as f:
    state = json.load(f)
print(f\"Capital: {state.get('total_capital', 'N/A'):.4f} SOL\")
print(f\"Trades: {state.get('total_trades', 0)}\")
print(f\"Wins: {state.get('wins', 0)} | Losses: {state.get('losses', 0)}\")
print(f\"Daily PnL: {state.get('daily_pnl', 0):.4f} SOL\")
print(f\"Daily Trades: {state.get('daily_trades', 0)}\")
"
else
    echo "State file: ❌ Not found"
fi

echo ""
echo "=================================="

# Handle arguments
if [ "$1" == "--stop" ]; then
    echo ""
    echo "🛑 STOPPING ALL SYSTEMS..."
    
    # Stop LuxTrader
    LUXTRADER_PID=$(pgrep -f "luxtrader_live.py" || echo "")
    if [ ! -z "$LUXTRADER_PID" ]; then
        echo "Stopping LuxTrader (PID: $LUXTRADER_PID)..."
        kill $LUXTRADER_PID 2>/dev/null
        echo "✅ LuxTrader stopped"
    fi
    
    # Stop Holy Trinity
    TRINITY_PID=$(pgrep -f "holy_trinity_live.py" || echo "")
    if [ ! -z "$TRINITY_PID" ]; then
        echo "Stopping Holy Trinity (PID: $TRINITY_PID)..."
        kill $TRINITY_PID 2>/dev/null
        echo "✅ Holy Trinity stopped"
    fi
    
    # Remove PID files
    rm -f "$SCRIPT_DIR/.luxtrader.pid"
    rm -f "$SCRIPT_DIR/.holy_trinity.pid"
    
    echo ""
    echo "✅ ALL SYSTEMS STOPPED"
fi

echo "=================================="
