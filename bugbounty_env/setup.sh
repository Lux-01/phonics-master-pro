#!/bin/bash
# Bug Bounty Testing Environment Setup Script
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "=========================================="
echo "🐛 Bug Bounty Environment Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create directory structure
echo -e "${YELLOW}[*] Creating directory structure...${NC}"
mkdir -p {tools,wordlists,reports,targets,scripts,notes}
mkdir -p tools/{burp,recon,exploitation,utils}
mkdir -p wordlists/{subdomains,paths,parameters,passwords}
echo -e "${GREEN}[✓] Directories created${NC}"

# Update system
echo -e "${YELLOW}[*] Updating system packages...${NC}"
sudo apt-get update -qq
echo -e "${GREEN}[✓] System updated${NC}"

# Install essential packages
echo -e "${YELLOW}[*] Installing essential packages...${NC}"
sudo apt-get install -y -qq \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    golang-go \
    nmap \
    masscan \
    jq \
    unzip \
    tmux \
    vim \
    nano \
    firefox \
    chromium-browser \
    2>/dev/null || echo "Some packages may already be installed"
echo -e "${GREEN}[✓] Essential packages installed${NC}"

# Install Go tools
echo -e "${YELLOW}[*] Installing Go-based tools...${NC}"

# Set Go environment
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin:$HOME/.local/bin
mkdir -p $GOPATH/bin

# Subfinder - subdomain discovery
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || echo "subfinder already installed"

# HTTPX - fast HTTP prober
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || echo "httpx already installed"

# Nuclei - vulnerability scanner
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null || echo "nuclei already installed"

# Katana - web crawler
go install -v github.com/projectdiscovery/katana/cmd/katana@latest 2>/dev/null || echo "katana already installed"

# Notify - notification framework
go install -v github.com/projectdiscovery/notify/cmd/notify@latest 2>/dev/null || echo "notify already installed"

# Amass - in-depth subdomain enumeration
go install -v github.com/owasp-amass/amass/v4/...@master 2>/dev/null || echo "amass already installed"

# GF - grep on steroids
go install -v github.com/tomnomnom/gf@latest 2>/dev/null || echo "gf already installed"

# Waybackurls - fetch URLs from Wayback Machine
go install -v github.com/tomnomnom/waybackurls@latest 2>/dev/null || echo "waybackurls already installed"

# Unfurl - URL analysis
go install -v github.com/tomnomnom/unfurl@latest 2>/dev/null || echo "unfurl already installed"

# Assetfinder - subdomain discovery
go install -v github.com/tomnomnom/assetfinder@latest 2>/dev/null || echo "assetfinder already installed"

# Httprobe - HTTP prober
go install -v github.com/tomnomnom/httprobe@latest 2>/dev/null || echo "httprobe already installed"

echo -e "${GREEN}[✓] Go tools installed${NC}"

# Install Python tools
echo -e "${YELLOW}[*] Installing Python tools...${NC}"

# Create virtual environment
python3 -m venv tools/venv
source tools/venv/bin/activate

# Install Python packages
pip install -q --upgrade pip
pip install -q sqlmap
pip install -q wfuzz
pip install -q requests
pip install -q beautifulsoup4
pip install -q lxml
pip install -q pyjwt

echo -e "${GREEN}[✓] Python tools installed${NC}"

# Download wordlists
echo -e "${YELLOW}[*] Downloading wordlists...${NC}"

# SecLists
if [ ! -d "wordlists/seclists" ]; then
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git wordlists/seclists 2>/dev/null || echo "SecLists already exists"
fi

# Assetnote wordlists
if [ ! -d "wordlists/assetnote" ]; then
    mkdir -p wordlists/assetnote
    cd wordlists/assetnote
    wget -q https://wordlists-cdn.assetnote.io/data/automated/httparchive_subdomains_2024_04_28.txt -O subdomains.txt || echo "Assetnote download skipped"
    cd ../..
fi

echo -e "${GREEN}[✓] Wordlists downloaded${NC}"

# Install Burp Suite CA certificate for intercepting HTTPS
echo -e "${YELLOW}[*] Setting up Burp Suite CA...${NC}"
mkdir -p ~/.burp
echo "Burp CA will need to be exported manually after first run"
echo "See: https://portswigger.net/burp/documentation/desktop/tools/proxy/options/import-export-ca-cert"

# Create useful scripts
echo -e "${YELLOW}[*] Creating helper scripts...${NC}"

# Recon script
cat > scripts/recon.sh << 'EOF'
#!/bin/bash
# Quick reconnaissance script
# Usage: ./recon.sh target.com

TARGET=$1
OUTPUT_DIR="targets/$TARGET-$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

echo "[*] Starting recon for: $TARGET"
echo "[*] Output: $OUTPUT_DIR"

# Subdomain enumeration
echo "[*] Finding subdomains..."
subfinder -d $TARGET -o $OUTPUT_DIR/subdomains.txt 2>/dev/null
assetfinder --subs-only $TARGET >> $OUTPUT_DIR/subdomains.txt 2>/dev/null
sort -u $OUTPUT_DIR/subdomains.txt -o $OUTPUT_DIR/subdomains.txt

# Probe for live hosts
echo "[*] Probing for live hosts..."
cat $OUTPUT_DIR/subdomains.txt | httpx -o $OUTPUT_DIR/live_hosts.txt -silent

# Wayback URLs
echo "[*] Fetching URLs from Wayback Machine..."
cat $OUTPUT_DIR/live_hosts.txt | waybackurls > $OUTPUT_DIR/wayback_urls.txt 2>/dev/null

# Katana crawl
echo "[*] Crawling discovered hosts..."
cat $OUTPUT_DIR/live_hosts.txt | katana -o $OUTPUT_DIR/katana_urls.txt 2>/dev/null

# Combine and dedupe URLs
cat $OUTPUT_DIR/wayback_urls.txt $OUTPUT_DIR/katana_urls.txt 2>/dev/null | sort -u > $OUTPUT_DIR/all_urls.txt

echo "[*] Recon complete! Results in: $OUTPUT_DIR"
echo "    - Subdomains: $(wc -l < $OUTPUT_DIR/subdomains.txt)"
echo "    - Live hosts: $(wc -l < $OUTPUT_DIR/live_hosts.txt)"
echo "    - URLs found: $(wc -l < $OUTPUT_DIR/all_urls.txt)"
EOF
chmod +x scripts/recon.sh

# Quick XSS check script
cat > scripts/check_xss.sh << 'EOF'
#!/bin/bash
# Quick XSS parameter check
# Usage: ./check_xss.sh urls.txt

URLS=$1
PAYLOAD="<script>alert('XSS')</script>"

echo "[*] Testing for XSS in URL parameters..."
while read url; do
    # Check if URL has parameters
    if echo "$url" | grep -q '?'; then
        # Add payload to each parameter
        echo "$url" | gf xss 2>/dev/null | while read param_url; do
            test_url=$(echo "$param_url" | sed "s/=.*=/=$PAYLOAD\&/g")
            echo "Testing: $test_url"
        done
    fi
done < $URLS
EOF
chmod +x scripts/check_xss.sh

# Report template generator
cat > scripts/new_report.sh << 'EOF'
#!/bin/bash
# Create new vulnerability report template
# Usage: ./new_report.sh program-name vulnerability-type

PROGRAM=$1
VULN_TYPE=$2
DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/$PROGRAM-$DATE"
mkdir -p $REPORT_DIR

cat > $REPORT_DIR/report.md << EOL
# Vulnerability Report

## Program
$PROGRAM

## Date
$DATE

## Vulnerability Type
$VULN_TYPE

## Severity
[ ] Critical  [ ] High  [ ] Medium  [ ] Low  [ ] Informational

## Summary
Brief description of the vulnerability

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Proof of Concept
\`\`\`
[Insert PoC code or screenshots]
\`\`\`

## Impact
What could an attacker do with this?

## Affected URLs/Endpoints
- 

## Mitigation
How to fix this vulnerability

## References
- 

## Reporter
[Your HackerOne username]
EOL

echo "[*] Report template created: $REPORT_DIR/report.md"
EOF
chmod +x scripts/new_report.sh

echo -e "${GREEN}[✓] Scripts created${NC}"

# Create notes template
cat > notes/bug-types.md << 'EOF'
# Common Bug Types Checklist

## Information Gathering
- [ ] Subdomain enumeration
- [ ] Technology fingerprinting
- [ ] Directory brute-forcing
- [ ] Parameter discovery
- [ ] API endpoint mapping

## Authentication
- [ ] Brute force vulnerabilities
- [ ] Session management issues
- [ ] JWT weaknesses
- [ ] OAuth misconfigurations
- [ ] Password reset flaws
- [ ] 2FA bypass

## Injection
- [ ] SQL Injection
- [ ] NoSQL Injection
- [ ] Command Injection
- [ ] LDAP Injection
- [ ] XPath Injection
- [ ] Template Injection (SSTI)

## XSS
- [ ] Reflected XSS
- [ ] Stored XSS
- [ ] DOM XSS
- [ ] Blind XSS
- [ ] CSP bypass

## Access Control
- [ ] IDOR (Insecure Direct Object Reference)
- [ ] Missing function level access control
- [ ] Path traversal
- [ ] Local file inclusion (LFI)
- [ ] Remote file inclusion (RFI)

## Business Logic
- [ ] Price manipulation
- [ ] Quantity manipulation
- [ ] Workflow bypass
- [ ] Race conditions

## Client-Side
- [ ] CORS misconfiguration
- [ ] Clickjacking
- [ ] DOM manipulation
- [ ] Open redirects

## Server-Side
- [ ] SSRF (Server-Side Request Forgery)
- [ ] XXE (XML External Entity)
- [ ] Deserialization
- [ ] Host header injection
- [ ] HTTP request smuggling

## Mobile (if applicable)
- [ ] Insecure data storage
- [ ] Weak cryptography
- [ ] Root/jailbreak detection bypass
- [ ] Hardcoded credentials
- [ ] Insecure communication
EOF

cat > notes/methodology.md << 'EOF'
# Testing Methodology

## 1. Reconnaissance (40% of time)
- Passive: WHOIS, DNS, Google dorks, GitHub
- Active: Subdomain enumeration, port scanning
- Tools: subfinder, amass, httpx, waybackurls

## 2. Mapping (20% of time)
- Identify technologies (Wappalyzer, builtwith)
- Map application flow
- Identify entry points
- Find hidden parameters (arjun, x8)

## 3. Vulnerability Testing (30% of time)
- Test each entry point for common bugs
- Focus on high-impact areas first
- Use automation for coverage
- Manual testing for logic bugs

## 4. Reporting (10% of time)
- Document everything
- Clear reproduction steps
- Demonstrate impact
- Suggest fixes

## Daily Workflow
1. Check HackerOne for new programs
2. Pick target based on scope/bounty
3. Run recon automation
4. Manual testing on interesting targets
5. Document findings
6. Submit reports

## Tools by Phase
Recon: subfinder, amass, httpx, waybackurls
Discovery: katana, gau, hakrawler
Testing: burp, nuclei, sqlmap
Reporting: template scripts, screenshots
EOF

# Create environment activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Source this file: source activate_env.sh

echo "🐛 Bug Bounty Environment Activated"
echo ""

# Set paths
export BB_ROOT="$(pwd)"
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin:$BB_ROOT/tools/venv/bin"

# Activate Python venv
source $BB_ROOT/tools/venv/bin/activate

# Show status
echo "Directory: $BB_ROOT"
echo "Python venv: ACTIVE"
echo "Go tools: $GOPATH/bin"
echo ""
echo "Available commands:"
echo "  recon.sh <target>       - Run reconnaissance"
echo "  new_report.sh <prog> <type> - Create report template"
echo "  check_xss.sh <urls>     - Quick XSS check"
echo ""
echo "Quick start:"
echo "  1. source activate_env.sh"
echo "  2. ./scripts/recon.sh example.com"
echo "  3. ./scripts/new_report.sh hackerone xss"
EOF
chmod +x activate_env.sh

# Create README
cat > README.md << 'EOF'
# 🐛 Bug Bounty Testing Environment

Complete setup for bug bounty hunting on HackerOne and other platforms.

## Quick Start

```bash
# Activate environment
source activate_env.sh

# Run recon on target
./scripts/recon.sh target.com

# Create report template
./scripts/new_report.sh program-name vulnerability-type
```

## Directory Structure

```
.
├── tools/              # Installed tools
│   ├── burp/          # Burp Suite configs
│   ├── recon/         # Recon tools
│   ├── exploitation/  # Exploitation tools
│   └── utils/         # Utilities
├── wordlists/         # Wordlists
│   ├── seclists/      # SecLists collection
│   └── assetnote/     # Assetnote wordlists
├── scripts/           # Helper scripts
├── targets/           # Target recon data
├── reports/           # Vulnerability reports
└── notes/             # Methodology, checklists
```

## Installed Tools

### Go Tools
- subfinder - Subdomain discovery
- httpx - Fast HTTP prober
- nuclei - Vulnerability scanner
- katana - Web crawler
- amass - In-depth subdomain enumeration
- gf - Grep on steroids
- waybackurls - Wayback Machine URLs
- assetfinder - Subdomain discovery

### Python Tools
- sqlmap - SQL injection automation
- wfuzz - Web fuzzer
- requests - HTTP library
- beautifulsoup4 - HTML parsing

### System Tools
- nmap - Port scanner
- masscan - Fast port scanner
- jq - JSON processor
- git, curl, wget - Utilities

## Usage

### Reconnaissance
```bash
# Full recon on target
./scripts/recon.sh example.com

# Results saved to: targets/example.com-YYYYMMDD/
```

### Vulnerability Testing
```bash
# Quick XSS check on discovered URLs
./scripts/check_xss.sh targets/example.com-YYYYMMDD/all_urls.txt

# SQLMap on interesting parameter
cat targets/example.com-YYYYMMDD/all_urls.txt | grep "id=" | sqlmap --batch
```

### Reporting
```bash
# Create report template
./scripts/new_report.sh hackerone "stored-xss"

# Edit: reports/hackerone-YYYY-MM-DD/report.md
```

## Burp Suite Setup

1. Download Burp Suite Community from: https://portswigger.net/burp/communitydownload
2. Install in `tools/burp/`
3. Launch: `java -jar tools/burp/burpsuite_community.jar`
4. Set proxy: 127.0.0.1:8080
5. Install CA certificate in browser

## Learning Resources

- PortSwigger Web Security Academy: https://portswigger.net/web-security
- Hacker101: https://www.hacker101.com/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- HackerOne Hacktivity: https://hackerone.com/hacktivity

## Tips

1. Always read program scope before testing
2. Stay in scope - out of scope = no bounty
3. Document everything with screenshots
4. Be patient - first bounty takes time
5. Focus on one bug class at a time
6. Build automation for repetitive tasks

## Next Steps

1. Complete PortSwigger Academy labs
2. Practice on HackTheBox/VulnHub
3. Join bug bounty Discord communities
4. Start with VDPs (no payout, safe practice)
5. Submit first report (even if informational)

Good luck! 🎯
EOF

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. cd /home/skux/.openclaw/workspace/bugbounty_env"
echo "  2. source activate_env.sh"
echo "  3. Download Burp Suite Community"
echo "  4. Start with: ./scripts/recon.sh test.com"
echo ""
echo "Directory: $(pwd)"
echo "Tools installed: $(ls tools/venv/bin/ | wc -l) Python tools, $(ls ~/go/bin/ 2>/dev/null | wc -l) Go tools"
echo ""
echo "Read README.md for full documentation"
