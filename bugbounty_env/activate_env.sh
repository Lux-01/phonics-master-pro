#!/bin/bash
# Source this file: source activate_env.sh

echo ""
echo "=========================================="
echo "🐛 Bug Bounty Environment Activated"
echo "=========================================="
echo ""

# Set paths
export BB_ROOT="$(pwd)"
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin:$HOME/.local/bin:$BB_ROOT/scripts"

# Show status
echo "📁 Directory: $BB_ROOT"
echo ""
echo "📂 Structure:"
echo "  tools/      - Security tools"
echo "  wordlists/  - Wordlists (SecLists, etc.)"
echo "  targets/    - Recon data"
echo "  reports/    - Vulnerability reports"
echo "  scripts/    - Helper scripts"
echo "  notes/      - Methodology & checklists"
echo ""

# Check installed tools
echo "🔧 Available Tools:"
echo ""

check_tool() {
    if command -v $1 &> /dev/null; then
        echo "  ✓ $1"
        return 0
    else
        echo "  ✗ $1 (install from INSTALL.md)"
        return 1
    fi
}

echo "Recon:"
check_tool subfinder
check_tool assetfinder
check_tool httpx
check_tool amass
check_tool waybackurls
check_tool katana

echo ""
echo "Testing:"
check_tool nuclei
check_tool nmap
check_tool sqlmap

echo ""
echo "Utils:"
check_tool gf
check_tool unfurl
check_tool git
check_tool jq

echo ""
echo "=========================================="
echo "🚀 Quick Start Commands:"
echo "=========================================="
echo ""
echo "  recon.sh <target.com>              - Run full reconnaissance"
echo "  new_report.sh <prog> <type>      - Create report template"
echo "  check_xss.sh <urls.txt>          - Quick XSS check"
echo ""
echo "Example workflow:"
echo "  1. recon.sh example.com"
echo "  2. cat targets/example.com-*/interesting_urls.txt"
echo "  3. check_xss.sh targets/example.com-*/urls_with_params.txt"
echo "  4. new_report.sh example-com xss"
echo "  5. # Edit report and submit to HackerOne"
echo ""
echo "📚 Documentation:"
echo "  cat README.md       - Full documentation"
echo "  cat INSTALL.md      - Installation guide"
echo "  cat notes/methodology.md - Testing methodology"
echo "  cat notes/bug-types.md   - Bug checklist"
echo ""
echo "💡 Tips:"
echo "  - Always read program scope before testing"
echo "  - Document everything with screenshots"
echo "  - Start with VDPs (no payout) for practice"
echo "  - Join HackerOne Discord for community support"
echo ""
