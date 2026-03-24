#!/bin/bash
# Start The Adaptive Edge Trading System
# This launches the monitor server on localhost:3456

set -e

echo "🦞 Starting The Adaptive Edge..."

# Check if we're in the workspace directory
if [ ! -f "adaptive_edge_monitor.js" ]; then
    echo "❌ Error: Must run from /workspace directory"
    echo "   cd /home/skux/.openclaw/workspace"
    exit 1
fi

# Create log directory if needed
mkdir -p trading_logs

# Check if secrets exist
if [ ! -f "./solana-trader/.secrets/wallet.key" ]; then
    echo "❌ Error: Wallet key not found"
    exit 1
fi

if [ ! -f "./solana-trader/.secrets/jupiter.key" ]; then
    echo "❌ Error: Jupiter API key not found"
    exit 1
fi

if [ ! -f "./solana-trader/.secrets/helius.key" ]; then
    echo "❌ Error: Helius RPC key not found"
    exit 1
fi

echo "✅ Secrets verified"

# Check if already running
MONITOR_PID=$(lsof -ti:3456 2>/dev/null || echo "")
if [ -n "$MONITOR_PID" ]; then
    echo "⚠️  Monitor already running on PID $MONITOR_PID"
    echo "   Visit: http://localhost:3456"
    exit 0
fi

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║         The Adaptive Edge v1.0           ║"
echo "╠═══════════════════════════════════════════╣"
echo "║  Config:                                  ║"
echo "║    • Risk: 10% max                       ║"
echo "║    • Trade Size: 0.15-0.25 SOL            ║"
echo "║    • Max Trades: 5/day                   ║"
echo "║    • Daily Loss: -5% limit               ║"
echo "║                                           ║"
echo "║  URL: http://localhost:3456             ║"
echo "║                                           ║"
echo "║  Press Ctrl+C to stop                    ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Start the monitor server
node adaptive_edge_monitor.js
