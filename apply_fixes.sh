#!/bin/bash
# Apply Code Fixes Script
# Run this to fix common issues found in code audit

echo "=========================================="
echo "🔧 Applying Code Fixes"
echo "=========================================="
echo ""

# Fix 1: Add __init__.py files
echo "📦 Fix 1: Adding __init__.py files..."
find agents skills memory -type d -exec touch {}/__init__.py \; 2>/dev/null
echo "   ✅ Added __init__.py to package directories"
echo ""

# Fix 2: Create requirements.txt
echo "📦 Fix 2: Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Core
requests>=2.31.0
python-dotenv>=1.0.0

# Trading & Crypto
solana>=0.30.0

# Browser Automation
playwright>=1.40.0
playwright-stealth>=1.0.0
fake-useragent>=1.4.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0

# HTTP Client
httpx>=0.25.0
EOF
echo "   ✅ Created requirements.txt"
echo ""

# Fix 3: Create .env.example
echo "🔐 Fix 3: Creating .env.example..."
cat > .env.example << 'EOF'
# API Keys - Copy to .env and fill in real values
JUPITER_API_KEY=your_jupiter_key_here
BIRDEYE_API_KEY=your_birdeye_key_here
HELIUS_API_KEY=your_helius_key_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
AGENTMAIL_API_KEY=your_agentmail_key_here

# Optional APIs
TWITTER_BEARER_TOKEN=optional
COINGECKO_API_KEY=optional
JITO_API_KEY=optional
EOF
echo "   ✅ Created .env.example"
echo ""

# Fix 4: Update .gitignore
echo "🔒 Fix 4: Updating .gitignore..."
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

# Add entries if not present
if ! grep -q "\.env" .gitignore; then
    echo "" >> .gitignore
    echo "# Environment variables" >> .gitignore
    echo ".env" >> .gitignore
    echo ".env.local" >> .gitignore
fi

if ! grep -q "\.key" .gitignore; then
    echo "" >> .gitignore
    echo "# Keys" >> .gitignore
    echo "*.key" >> .gitignore
fi

if ! grep -q "secrets/" .gitignore; then
    echo "" >> .gitignore
    echo "# Secrets directory" >> .gitignore
    echo "secrets/" >> .gitignore
fi

echo "   ✅ Updated .gitignore"
echo ""

# Fix 5: Create agents/README.md
echo "📄 Fix 5: Creating README files..."
cat > agents/README.md << 'EOF'
# Agents Directory

Trading and automation agents.

## Structure
- `skylar/` - Trading strategy execution
- `wallet_tracker/` - Whale wallet monitoring
- `apis/` - API clients (Jupiter, Twitter, etc.)

## Usage
Each agent is self-contained with its own configuration.
EOF

cat > skills/README.md << 'EOF'
# Skills Directory

Reusable skill modules for OpenClaw.

## Structure
Each skill has its own directory with:
- `SKILL.md` - Documentation
- Scripts and utilities

## Adding Skills
Follow the pattern in existing skills.
EOF

cat > memory/README.md << 'EOF'
# Memory Directory

Persistent storage for:
- Daily logs
- Outcomes and learnings
- Configuration state

## Structure
- `YYYY-MM-DD.md` - Daily logs
- `*.json` - State files
- Subdirectories for specific systems
EOF

echo "   ✅ Created README files"
echo ""

echo "=========================================="
echo "✅ Fixes Applied!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review CODE_AUDIT_REPORT.md for details"
echo "2. Manually fix hardcoded API keys in test files"
echo "3. Fix bare except: clauses"
echo "4. Run: cp .env.example .env and fill in real keys"
echo ""
echo "⚠️  IMPORTANT: Rotate exposed API keys!"
echo "   - test_agentmail_text.py"
echo "   - test_agentmail2.py"
echo "   - send_installer.py"
echo "   - test_agentmail_explore.py"
echo ""
