#!/bin/bash
# AOE Monitor Runner
# Runs the opportunity scanner and sends alerts

cd /home/skux/.openclaw/workspace

# Run the scanner
python3 aoe_monitor.py

# Capture exit code
EXIT_CODE=$?

# If alerts generated (exit 0), send notification
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎯 AOE: High-score opportunities detected!"
    # Notification would be sent here
    # For now, alert is logged to console and file
fi

exit $EXIT_CODE
