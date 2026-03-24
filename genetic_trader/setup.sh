#!/bin/bash
# Genetic Trading System Setup

echo "🧬 Genetic Trading System - Setup"
echo "=================================="
echo ""

# Create directories
mkdir -p /home/skux/.openclaw/workspace/genetic_trader
cd /home/skux/.openclaw/workspace/genetic_trader

# Check Python dependencies
echo "📦 Checking dependencies..."

python3 -c "import aiohttp" 2>/dev/null || echo "⚠️  aiohttp not installed: pip3 install aiohttp"
python3 -c "import asyncio" 2>/dev/null || echo "✅ asyncio available"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "   1. Test run:     python3 runner.py demo"
echo "   2. Run cycle:    python3 runner.py run"
echo "   3. Check status: python3 runner.py status"
echo "   4. View dashboard: Open dashboard.html in browser"
echo ""
echo "🕐 Automated execution:"
echo "   python3 runner.py setup-cron"
echo ""
