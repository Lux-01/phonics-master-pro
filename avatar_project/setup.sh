#!/bin/bash
# Setup script for DeskMate Replica

echo "🎭 Setting up DeskMate Replica..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18+. Current: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create directories
mkdir -p assets/avatars
mkdir -p assets/animations

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start:"
echo "  1. Terminal 1: npm start"
echo "  2. Terminal 2: node bridge/lux_bridge.js"
echo ""
echo "Then I can control the avatar! 🦞"