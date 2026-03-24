# 🐛 Bug Bounty Testing Environment

Complete setup for bug bounty hunting on HackerOne and other platforms.

## Quick Start

```bash
# Navigate to environment
cd /home/skux/.openclaw/workspace/bugbounty_env

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
│   ├── subdomains/    # Subdomain lists
│   ├── paths/         # Directory lists
│   └── passwords/     # Password lists
├── scripts/           # Helper scripts
│   ├── recon.sh       # Full reconnaissance
│   ├── new_report.sh  # Create report template
│   └── check_xss.sh   # Quick XSS check
├── targets/           # Target recon data
├── reports/           # Vulnerability reports
└── notes/             # Methodology, checklists
    ├── bug-types.md   # Bug checklist
    └── methodology.md # Testing methodology
```

## Installation

### Step 1: System Dependencies

```bash
sudo apt update
sudo apt install -y git curl wget python3 python3-pip python3-venv golang-go nmap masscan jq unzip tmux vim firefox
```

### Step 2: Go Tools

```bash
# Set Go environment
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
mkdir -p $GOPATH/bin

# Install recon tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/projectdiscovery/notify/cmd/notify@latest
go install github.com/owasp-amass/amass/v4/...@master

# Install utility tools
go install github.com/tomnomnom/gf@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/tomnomnom/unfurl@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/tomnomnom/httprobe@latest
```

### Step 3: Python Tools

```bash
python3 -m venv tools/venv
source tools/venv/bin/activate
pip install sqlmap wfuzz requests beautifulsoup4 lxml pyjwt
```

### Step 4: Wordlists

```bash
# SecLists
git clone --depth 1 https://github.com/danielmiessler/SecLists.git wordlists/seclists

# Assetnote wordlists
mkdir -p wordlists/assetnote
cd wordlists/assetnote
wget https://wordlists-cdn.assetnote.io/data/automated/httparchive_subdomains_2024_04_28.txt -O subdomains.txt
cd ../..
```

### Step 5: Burp Suite

1. Download from: https://portswigger.net/burp/communitydownload
2. Move to: `tools/burp/burpsuite_community.jar`
3. Launch: `java -jar tools/burp/burpsuite_community.jar`
4. Set proxy: 127.0.0.1:8080
5. Install CA certificate in browser

## Usage

### Reconnaissance

```bash
# Full recon on target
./scripts/recon.sh example.com

# Results saved to: targets/example.com-YYYYMMDD/
#   - subdomains.txt      # Discovered subdomains
#   - live_hosts.txt      # Live web servers
#   - all_urls.txt        # All discovered URLs
#   - interesting_urls.txt # Potentially interesting endpoints
#   - urls_with_params.txt # URLs with parameters (test these!)
```

### Vulnerability Testing

```bash
# Quick XSS check on discovered URLs
./scripts/check_xss.sh targets/example.com-YYYYMMDD/urls_with_params.txt

# Manual testing with Burp Suite
# 1. Set browser proxy to 127.0.0.1:8080
# 2. Browse target and capture requests
# 3. Send to Repeater/Intruder for testing

# SQLMap on interesting parameter
cat targets/example.com-YYYYMMDD/urls_with_params.txt | grep "id=" | sqlmap --batch
```

### Reporting

```bash
# Create report template
./scripts/new_report.sh hackerone "stored-xss"

# Edit the report
nano reports/hackerone-YYYY-MM-DD-stored-xss/report.md

# Add screenshots
# Copy screenshots to reports/hackerone-YYYY-MM-DD-stored-xss/
```

## Installed Tools

### Reconnaissance
- **subfinder** - Fast subdomain discovery
- **assetfinder** - Find domains and subdomains
- **amass** - In-depth subdomain enumeration
- **httpx** - Fast HTTP prober
- **waybackurls** - Fetch URLs from Wayback Machine
- **katana** - Web crawler

### Scanning
- **nuclei** - Vulnerability scanner
- **nmap** - Port scanner
- **masscan** - Fast port scanner

### Exploitation
- **sqlmap** - SQL injection automation
- **wfuzz** - Web fuzzer
- **Burp Suite** - Web proxy and testing platform

### Utilities
- **gf** - Grep on steroids (pattern matching)
- **unfurl** - URL analysis
- **jq** - JSON processor
- **git, curl, wget** - Standard utilities

## Methodology

### 1. Reconnaissance (40% of time)
- Passive: WHOIS, DNS, Google dorks, GitHub
- Active: Subdomain enumeration, port scanning
- Tools: subfinder, amass, httpx, waybackurls

### 2. Mapping (20% of time)
- Identify technologies (Wappalyzer, builtwith)
- Map application flow
- Identify entry points
- Find hidden parameters

### 3. Vulnerability Testing (30% of time)
- Test each entry point for common bugs
- Focus on high-impact areas first
- Use automation for coverage
- Manual testing for logic bugs

### 4. Reporting (10% of time)
- Document everything
- Clear reproduction steps
- Demonstrate impact
- Suggest fixes

## Common Bug Types

See `notes/bug-types.md` for full checklist.

Quick reference:
- **XSS** - Cross-site scripting
- **SQLi** - SQL injection
- **IDOR** - Insecure direct object reference
- **CSRF** - Cross-site request forgery
- **SSRF** - Server-side request forgery
- **Auth Bypass** - Authentication bypass
- **Info Disclosure** - Information disclosure

## Tips for Success

### Getting Started
1. **Learn first** - Complete PortSwigger Academy before hunting
2. **Start small** - Begin with VDPs (no payout) for practice
3. **Focus** - Pick one bug class and master it
4. **Read reports** - Study disclosed HackerOne reports
5. **Be patient** - First bounty takes time (3-6 months typical)

### During Testing
- Always read program scope carefully
- Stay in scope - out of scope = no bounty
- Document everything with screenshots
- Test on staging when available
- Don't test on production accounts you don't own

### Report Writing
- Clear, concise title
- Step-by-step reproduction
- Proof of concept (PoC)
- Demonstrate real impact
- Suggest fixes

## Resources

### Free Learning
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Hacker101](https://www.hacker101.com/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [HackerOne Hacktivity](https://hackerone.com/hacktivity)

### Communities
- **Twitter** - Follow @Hacker0x01, @NahamSec, @TomNomNom
- **Discord** - Bug Bounty Hunter, The Cyber Mentor
- **Reddit** - r/bugbounty

### Practice Platforms
- [HackTheBox](https://www.hackthebox.com/) - Realistic labs
- [TryHackMe](https://tryhackme.com/) - Guided learning
- [VulnHub](https://www.vulnhub.com/) - Vulnerable VMs
- [PentesterLab](https://pentesterlab.com/) - Web exercises

## Expected Timeline

| Phase | Duration | Focus | Expected Earnings |
|-------|----------|-------|-------------------|
| Learning | Months 1-3 | PortSwigger, HTB | $0 |
| First Attempts | Months 3-6 | VDPs, low bounties | $0-1,000 |
| First Bounties | Months 6-12 | Consistent hunting | $1,000-10,000 |
| Intermediate | Year 2 | Specialization | $10,000-50,000 |
| Advanced | Year 3+ | Full-time potential | $50,000-200,000 |

## Troubleshooting

### Tool not found?
```bash
# Check if in PATH
which subfinder

# If not found, add to PATH
export PATH=$PATH:$HOME/go/bin:$HOME/.local/bin
```

### Permission denied?
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Burp Suite won't start?
```bash
# Check Java version
java -version

# Should be Java 11 or higher
# Download from: https://portswigger.net/burp/communitydownload
```

## Next Steps

1. ✅ Environment set up
2. ⬜ Complete PortSwigger Academy (40+ hours)
3. ⬜ Do 10 HackTheBox machines
4. ⬜ Read 50 disclosed HackerOne reports
5. ⬜ Pick first target program
6. ⬜ Submit first report (even if informational)

Good luck! 🎯

---

**Disclaimer:** Only test systems you have permission to test. Unauthorized access to computer systems is illegal. Always follow responsible disclosure practices.
