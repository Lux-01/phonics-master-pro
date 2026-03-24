#!/bin/bash
# Solana Alpha Hunter v5.3 - Daily 9PM Scan
# Post-Rug Protection Edition: Age filter, mint verification, LP depth check

LOGFILE="/home/skux/.openclaw/workspace/scan_v53.log"
WORKDIR="/home/skux/.openclaw/workspace"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') - Starting v5.3 Daily Scan ===" >> "$LOGFILE"
cd "$WORKDIR" && /usr/bin/python3 solana_alpha_hunter_v53.py >> "$LOGFILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') - Scan Complete ===" >> "$LOGFILE"
