# Solana Trader - Installation Script

cd ~/.openclaw/workspace/solana-trader

echo "═══════════════════════════════════════════"
echo "  Installing Solana Trading Bot"
echo "═══════════════════════════════════════════"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js 16+ first:"
    echo "   https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt "16" ]; then
    echo "❌ Node.js version too old. Need v16+. Current: $(node --version)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Create directories
mkdir -p .secrets
mkdir -p trading_logs

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Installation failed"
    exit 1
fi

# Setup wallet file
echo ""
echo "═══════════════════════════════════════════"
echo "  Wallet Setup"
echo "═══════════════════════════════════════════"
echo ""
echo "To complete setup, you need to:"
echo ""
echo "1. Open Phantom Wallet"
echo "2. Settings → Security & Privacy"
echo "3. Export private key (base58)"
echo "4. Save to .secrets/wallet.key"
echo ""
echo "   echo 'YOUR_PRIVATE_KEY' > .secrets/wallet.key"
echo "   chmod 600 .secrets/wallet.key"
echo ""
echo "⚠️  NEVER share or commit this key!"
echo ""
echo "═══════════════════════════════════════════"
echo ""
echo "After setting up wallet, run:"
echo "  node trader.js balance"
echo "  node trader.js state"
echo "  node trader.js monitor"
echo ""
