#!/bin/bash
# v5.4 Monitor - Track token survival and sentiment

cd /home/skux/.openclaw/workspace

export PATH="$HOME/.local/bin:$PATH"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "================================================================================"
echo "🚀 SOLANA ALPHA HUNTER v5.4 - Survivor Monitor"
echo "🕐 $TIMESTAMP"
echo "================================================================================"

# Run v5.4 monitor
python3 solana_alpha_hunter_v54.py 2>&1 | tee -a scan_v54.log

echo ""
echo "================================================================================"
echo "✅ v5.4 Monitor complete: $TIMESTAMP"
echo "================================================================================"
