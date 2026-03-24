#!/bin/bash
# AOE v2.0 Launcher
# Runs the Autonomous Opportunity Engine

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/home/skux/.openclaw/workspace"
AOE_DIR="$WORKSPACE_DIR/aoe_v2"

# Logging
LOG_DIR="$AOE_DIR/data"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/aoe_$(date +%Y%m%d_%H%M%S).log"

echo "=================================="
echo "🔥 AOE v2.0 - Opportunity Engine"
echo "=================================="
echo "Started: $(date)"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "   ✅ Python 3"

# Check workspace exists
if [ ! -d "$AOE_DIR" ]; then
    echo "❌ AOE v2.0 directory not found at $AOE_DIR"
    exit 1
fi
echo "   ✅ AOE directory"

# Check for required modules
cd "$AOE_DIR"

REQUIRED_MODULES=("scanner_base" "scanner_dexscreener" "token_pipeline" "scorer" "alerts" "main")
for module in "${REQUIRED_MODULES[@]}"; do
    if [ ! -f "${module}.py" ]; then
        echo "❌ Missing module: ${module}.py"
        exit 1
    fi
done
echo "   ✅ All modules present"

# Check environment
echo ""
echo "🔐 Environment check:"

if [ -n "$BIRDEYE_API_KEY" ]; then
    echo "   ✅ Birdeye API key set"
else
    echo "   ⚠️  Birdeye API key not set (some scans will be skipped)"
fi

if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "   ✅ Telegram configured for alerts"
else
    echo "   ⚠️  Telegram not configured (alerts disabled)"
fi

echo ""
echo "🚀 Running AOE Scan..."
echo "Log: $LOG_FILE"
echo "=================================="

# Run AOE
python3 main.py --mode scan 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ AOE scan completed successfully"
else
    echo "❌ AOE scan failed with code $EXIT_CODE"
fi
echo "Finished: $(date)"
echo "=================================="

exit $EXIT_CODE
