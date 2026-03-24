#!/bin/bash
# Telegram Bot Setup Script for Whale Tracker
# Run this to set up your Telegram bot for whale alerts

echo "🤖 Telegram Bot Setup for Whale Tracker"
echo "=========================================="
echo ""

# Check if already set
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "✅ TELEGRAM_BOT_TOKEN is already set!"
    echo ""
    echo "Current configuration:"
    echo "  Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
    echo ""
    read -p "Do you want to reconfigure? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing configuration."
        exit 0
    fi
fi

echo "📱 Step 1: Create a Telegram Bot"
echo "--------------------------------"
echo ""
echo "1. Open Telegram and search for @BotFather"
echo "2. Send /newbot"
echo "3. Choose a name (e.g., 'WhaleTracker Alerts')"
echo "4. Choose a username (e.g., yourname_whalert_bot)"
echo "5. Copy the API token (starts with numbers, like 123456789:ABC...)"
echo ""

# Get token from user
read -p "Enter your bot token: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Validate token format
if [[ ! $TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
    echo "⚠️ Token format looks unusual. Make sure you copied it correctly."
    echo "It should look like: 123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📱 Step 2: Get Your Chat ID"
echo "---------------------------"
echo ""
echo "1. Send a message to your new bot"
echo "2. Visit: https://api.telegram.org/bot$TOKEN/getUpdates"
echo "3. Look for 'chat': {'id': 123456789}"
echo "4. Copy the ID number"
echo ""

read -p "Enter your chat ID: " CHAT_ID

if [ -z "$CHAT_ID" ]; then
    echo "⚠️ No chat ID provided. Using default (6610224534)"
    CHAT_ID="6610224534"
fi

echo ""
echo "🔧 Step 3: Save Configuration"
echo "-----------------------------"
echo ""

# Create environment file
cat > /home/skux/.openclaw/workspace/agents/wallet_whale/.env << EOF
# Whale Tracker Telegram Configuration
TELEGRAM_BOT_TOKEN=$TOKEN
TELEGRAM_CHAT_ID=$CHAT_ID
EOF

echo "✅ Configuration saved to .env file"

# Export for current session
export TELEGRAM_BOT_TOKEN=$TOKEN
export TELEGRAM_CHAT_ID=$CHAT_ID

# Add to bashrc for persistence
echo "" >> ~/.bashrc
echo "# Whale Tracker Telegram" >> ~/.bashrc
echo "export TELEGRAM_BOT_TOKEN=$TOKEN" >> ~/.bashrc
echo "export TELEGRAM_CHAT_ID=$CHAT_ID" >> ~/.bashrc

echo "✅ Added to ~/.bashrc for persistence"

echo ""
echo "🧪 Step 4: Test the Bot"
echo "-----------------------"
echo ""

# Test message
curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID" \
    -d "text=🐳 Whale Tracker is now configured! You'll receive alerts when whales are detected." \
    -d "parse_mode=HTML" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Test message sent! Check your Telegram."
else
    echo "⚠️ Could not send test message. Check your token and chat ID."
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Your bot will send alerts for:"
echo "  🐳 Whale activity detected"
echo "  🔥 Multi-whale signals"
echo "  ✅ Trades executed"
echo "  ❌ Trade failures"
echo "  📈 Daily summaries"
echo ""
echo "To start tracking:"
echo "  cd /home/skux/.openclaw/workspace/agents/wallet_whale"
echo "  python3 run_tracker_v2.py start"
echo ""
echo "To test alerts:"
echo "  python3 run_tracker_v2.py test-telegram"
echo ""
