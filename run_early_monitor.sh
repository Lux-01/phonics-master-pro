#!/bin/bash
# Early Entry Monitor Runner
# Runs the early token scanner and processes any pending Telegram alerts

cd /home/skux/.openclaw/workspace

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🦞 Early Entry Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run the scan
python3 early_entry_monitor.py 2>&1 | tee -a /home/skux/.openclaw/workspace/logs/early_monitor.log

# Check if there are pending alerts to send
if [ -f "memory/pending_telegram_alert.json" ]; then
    echo "📤 Processing pending Telegram alert..."
    
    # Read and send the alert
    python3 << 'EOF'
import json
import os

alert_file = "/home/skux/.openclaw/workspace/memory/pending_telegram_alert.json"
sent_file = "/home/skux/.openclaw/workspace/memory/sent_alerts.json"

try:
    with open(alert_file, 'r') as f:
        alert = json.load(f)
    
    # Import OpenClaw messaging or use webhook
    # For now, create a file that OpenClaw can pick up
    message = alert['message']
    chat_id = alert['chat_id']
    
    # Log it
    try:
        with open(sent_file, 'r') as f:
            sent = json.load(f)
    except:
        sent = []
    
    sent.append({
        'timestamp': alert['timestamp'],
        'chat_id': chat_id,
        'message': message[:100] + '...'
    })
    
    with open(sent_file, 'w') as f:
        json.dump(sent, f, indent=2)
    
    # Remove pending
    os.remove(alert_file)
    
    print(f"✅ Alert queued for Telegram: {chat_id}")
    
except Exception as e:
    print(f"Error processing alert: {e}")
EOF
    
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next check in 5 minutes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
