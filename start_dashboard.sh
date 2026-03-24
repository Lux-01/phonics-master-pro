#!/bin/bash
cd /home/skux/.openclaw/workspace/market_dashboard
python3 -m http.server 8080 &
echo "Dashboard started on http://localhost:8080"
