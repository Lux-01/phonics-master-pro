#!/bin/bash
# LG TV Setup Script
# Helps find and connect to your LG TV

echo "📺 LG TV Setup for Lux"
echo "======================"
echo ""

# Check if IP provided
if [ -z "$1" ]; then
    echo "No IP address provided. Let's find your TV..."
    echo ""
    
    # Try to discover TV on network
    echo "Scanning network for LG TVs (port 3000)..."
    
    # Get local network
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    NETWORK=$(echo $LOCAL_IP | cut -d. -f1-3)
    
    echo "Local IP: $LOCAL_IP"
    echo "Scanning: $NETWORK.0/24"
    echo ""
    
    # Scan for port 3000 (LG webOS)
    echo "Possible LG TVs:"
    for i in {1..254}; do
        (timeout 1 bash -c "echo >/dev/tcp/$NETWORK.$i/3000" 2>/dev/null && echo "  Found: $NETWORK.$i") &
    done
    wait
    
    echo ""
    echo "If your TV is listed above, run:"
    echo "  ./setup_lgtv.sh <IP_ADDRESS>"
    echo ""
    echo "Or manually enter your TV's IP address:"
    read -p "TV IP: " TV_IP
else
    TV_IP=$1
fi

echo ""
echo "Setting up connection to LG TV at $TV_IP..."
echo ""

# Check if pywebostv installed
python3 -c "import pywebostv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required package (pywebostv)..."
    pip3 install pywebostv
fi

# Run connection test
echo "Testing connection..."
echo ""
python3 << EOF
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace')
from lgtv_controller import LGTVController

print(f"Connecting to TV at $TV_IP...")
print("Make sure your TV is ON and on the same network.")
print("")

tv = LGTVController("$TV_IP")
if tv.connect():
    print("✅ Successfully connected!")
    info = tv.get_info()
    print(f"   Model: {info.get('model', 'Unknown')}")
    print(f"   Software: {info.get('software', 'Unknown')}")
    tv.disconnect()
    
    # Save IP to config
    import json
    import os
    config = {"tv_ip": "$TV_IP"}
    os.makedirs(os.path.expanduser("~/.openclaw"), exist_ok=True)
    with open(os.path.expanduser("~/.openclaw/lgtv_config.json"), "w") as f:
        json.dump(config, f)
    
    print("")
    print("💾 TV IP saved to ~/.openclaw/lgtv_config.json")
    print("")
    print("You can now control your TV with:")
    print("  python3 embodiment_with_tv.py $TV_IP")
    print("  python3 lgtv_controller.py $TV_IP")
else:
    print("❌ Connection failed!")
    print("")
    print("Troubleshooting:")
    print("  1. Make sure TV is ON")
    print("  2. Check TV and computer are on same WiFi network")
    print("  3. On TV: Settings > Network > Mobile TV On > Enable")
    print("  4. Try restarting your TV")
EOF

echo ""
echo "Setup complete!"
