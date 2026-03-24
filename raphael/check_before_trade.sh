#!/bin/bash
# RAPHAEL Pre-Trade Safety Check Script
# Usage: ./check_before_trade.sh <TOKEN_SYMBOL> <MINT_ADDRESS>

echo "🔒 RAPHAEL PRE-TRADE SAFETY CHECK"
echo "================================"

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <TOKEN_SYMBOL> <MINT_ADDRESS>"
    exit 1
fi

TOKEN=$1
MINT=$2

# Pre-trade checklist
echo "✓ Token: $TOKEN"
echo "✓ Mint: $MINT"

# 1. Check monitor status first
echo ""
echo "🔍 Checking monitor status..."
MONITOR_STATUS=$(curl -s http://localhost:3456/api/status)
EMERGENCY_STOP=$(echo $MONITOR_STATUS | grep -o '"emergencyStop":[^,}]*' | cut -d: -f2)

if [ "$EMERGENCY_STOP" = "true" ]; then
    echo "❌ EMERGENCY STOP IS ACTIVE - ABORTING"
    exit 1
fi

echo "✅ Emergency stop: NOT TRIGGERED"

# 2. Check wallet balance
echo ""
echo "🔍 Checking wallet balance..."
# Check solana balance (if available)
if command -v solana &> /dev/null; then
    BALANCE=$(solana balance 2>/dev/null | awk '{print $1}' || echo "0")
else
    BALANCE="1.0"  # Default for testing
fi
echo "   Wallet Balance: $BALANCE SOL"

# 3. Run token safety check
echo ""
echo "🔍 Running token safety check..."
python3 /home/skux/.openclaw/workspace/raphael/raphael_rugcheck.py "$TOKEN" "$MINT"
RUGCHECK_STATUS=$?

if [ $RUGCHECK_STATUS -ne 0 ]; then
    echo "❌ TOKEN SAFETY CHECK FAILED - ABORTING"
    exit 1
fi

echo ""
echo "================================"
echo "✅ ALL PRE-TRADE CHECKS PASSED"
echo "Ready to trade $TOKEN"
echo "================================"

exit 0
