#!/bin/bash
# Raphael Pre-Trade Safety Check
# Usage: ./check_before_trade.sh <token_symbol> <mint_address>

TOKEN="$1"
MINT="$2"

if [ -z "$TOKEN" ] || [ -z "$MINT" ]; then
    echo "Usage: ./check_before_trade.sh <token_symbol> <mint_address>"
    exit 1
fi

echo "🔍 Raphael Pre-Trade Check"
echo "Token: $TOKEN"
echo "Mint:  $MINT"
echo ""

# Run rug check
python3 /home/skux/.openclaw/workspace/agents/raphael/raphael_rugcheck.py "$MINT" "$TOKEN"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ RUG CHECK PASSED"
    echo "Raphael can proceed with trade"
    
    # Log to file
    echo "$(date): ✅ $TOKEN ($MINT) - APPROVED" >> /tmp/raphael_approvals.log
    exit 0
else
    echo "❌ RUG CHECK FAILED"
    echo "Raphael: SKIP THIS TRADE"
    
    # Log to file
    echo "$(date): ❌ $TOKEN ($MINT) - REJECTED" >> /tmp/raphael_approvals.log
    exit 1
fi
