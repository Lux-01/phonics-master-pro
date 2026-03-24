#!/bin/bash
# Start web server for Restored Right website - ACCESSIBLE FROM HOST
# WSL IP: 172.26.93.172

cd /home/skux/.openclaw/workspace/restored_right_redesign || exit 1

# Kill existing server
pkill -f "http.server" 2>/dev/null || true
sleep 1

echo "Starting Restored Right Sydney website server..."
echo ""
echo "🔗 URLs to access the website:"
echo "   Inside WSL:  http://127.0.0.1:8888"
echo "   From Host:   http://172.26.93.172:8888"
echo ""
echo "📱 All 6 pages:"
echo "   http://172.26.93.172:8888/index.html - Home"
echo "   http://172.26.93.172:8888/services.html - Services"
echo "   http://172.26.93.172:8888/about.html - About"
echo "   http://172.26.93.172:8888/emergency.html - Emergency"
echo "   http://172.26.93.172:8888/areas.html - Service Areas"
echo "   http://172.26.93.172:8888/contact.html - Contact/Quote"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 8888 --bind 0.0.0.0
