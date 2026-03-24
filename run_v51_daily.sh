#!/bin/bash
# Solana Alpha Hunter v5.1 - Daily 9PM Scan
# Wallet Health Filter Edition

LOGFILE="/home/skux/.openclaw/workspace/scan_v51.log"
WORKDIR="/home/skux/.openclaw/workspace"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') - Starting v5.1 Daily Scan ===" >> "$LOGFILE"
cd "$WORKDIR" && /usr/bin/python3 solana_alpha_hunter_v51.py >> "$LOGFILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') - Scan Complete ===" >> "$LOGFILE"
