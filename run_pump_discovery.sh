#!/bin/bash
# 📱 PUMP GROUP DISCOVERY DAILY SCAN
# Runs all pump group discovery methods

cd /home/skux/.openclaw/workspace

echo "╔======================================================================╗"
echo "║          🚀 PUMP GROUP DISCOVERY SCAN - $(date '+%Y-%m-%d %H:%M')         ║"
echo "╚======================================================================╝"
echo

# Run Telegram scanner
echo "📱 Running Telegram scanner..."
python3 telegram_pump_scanner.py > telegram_scan_$(date +%Y%m%d).log 2>&1

if [ -f telegram_pump_groups_$(date +%Y%m%d).json ]; then
    COUNT=$(cat telegram_pump_groups_$(date +%Y%m%d).json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('total_found', 0))")
    echo "✅ Found $COUNT Telegram groups"
else
    echo "⚠️  Telegram scan completed (check logs)"
fi

echo
echo "🔍 Checking Twitter monitor..."
python3 twitter_pump_monitor.py > twitter_scan_$(date +%Y%m%d).log 2>&1

echo
echo "📊 Summary:"
echo "  - Telegram groups: $(ls telegram_pump_groups_*.json 2>/dev/null | wc -l) saved"
echo "  - Scan logs: telegram_scan_*.log, twitter_scan_*.log"
echo

# Send notification if groups found
if [ -f telegram_pump_groups_$(date +%Y%m%d).json ]; then
    COUNT=$(cat telegram_pump_groups_$(date +%Y%m%d).json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('total_found', 0))")
    if [ "$COUNT" -gt 0 ]; then
        echo "📢 New pump groups found! Check telegram_pump_groups_$(date +%Y%m%d).json"
    fi
fi

echo
echo "Next scan: Tomorrow at $(date -d '+1 day' '+%Y-%m-%d 06:00')"
echo
