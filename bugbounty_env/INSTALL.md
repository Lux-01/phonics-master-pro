#!/bin/bash
# Manual installation guide for Bug Bounty tools
# Run commands one by one as needed

echo "=========================================="
echo "🐛 Bug Bounty Tool Installation Guide"
echo "=========================================="
echo ""
echo "Run these commands manually:"
echo ""

echo "1. Install system packages:"
echo "   sudo apt update"
echo "   sudo apt install -y git curl wget python3 python3-pip python3-venv golang-go nmap masscan jq unzip tmux"
echo ""

echo "2. Install Go tools:"
echo "   # Set Go environment"
echo "   export GOPATH=\$HOME/go"
echo "   export PATH=\$PATH:\$GOPATH/bin"
echo "   mkdir -p \$GOPATH/bin"
echo ""
echo "   # Install tools"
echo "   go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
echo "   go install github.com/projectdiscovery/httpx/cmd/httpx@latest"
echo "   go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
echo "   go install github.com/projectdiscovery/katana/cmd/katana@latest"
echo "   go install github.com/projectdiscovery/notify/cmd/notify@latest"
echo "   go install github.com/owasp-amass/amass/v4/...@master"
echo "   go install github.com/tomnomnom/gf@latest"
echo "   go install github.com/tomnomnom/waybackurls@latest"
echo "   go install github.com/tomnomnom/unfurl@latest"
echo "   go install github.com/tomnomnom/assetfinder@latest"
echo "   go install github.com/tomnomnom/httprobe@latest"
echo ""

echo "3. Install Python tools:"
echo "   python3 -m venv tools/venv"
echo "   source tools/venv/bin/activate"
echo "   pip install sqlmap wfuzz requests beautifulsoup4 lxml pyjwt"
echo ""

echo "4. Download wordlists:"
echo "   git clone --depth 1 https://github.com/danielmiessler/SecLists.git wordlists/seclists"
echo ""

echo "5. Download Burp Suite:"
echo "   wget https://portswigger.net/burp/releases/download?product=community\&version=2024.1.1\&type=jar"
echo "   # Move to tools/burp/"
echo ""

echo "6. Activate environment:"
echo "   source activate_env.sh"
echo ""
