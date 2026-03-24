# Tools Guide

Essential tools for bug bounty hunting and how to use them.

## Reconnaissance Tools

### Subfinder
**Purpose:** Fast subdomain discovery

**Installation:**
```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

**Basic Usage:**
```bash
# Single domain
subfinder -d example.com

# Output to file
subfinder -d example.com -o subdomains.txt

# Multiple domains
subfinder -d example.com -d another.com

# With all sources
subfinder -d example.com -all
```

**Pro Tips:**
- Use `-all` for comprehensive results (slower)
- Combine with `httpx` to find live hosts
- Run multiple times for new subdomains

---

### HTTPX
**Purpose:** Fast HTTP prober

**Installation:**
```bash
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
```

**Basic Usage:**
```bash
# Probe subdomains
cat subdomains.txt | httpx

# Output to file with status codes
cat subdomains.txt | httpx -o live.txt -status-code

# Get titles and tech
cat subdomains.txt | httpx -title -tech-detect

# Follow redirects
cat subdomains.txt | httpx -follow-redirects
```

**Pro Tips:**
- Use `-silent` for clean output
- Combine with `-title` to identify interesting targets
- Use `-tech-detect` for technology fingerprinting

---

### Amass
**Purpose:** In-depth subdomain enumeration

**Installation:**
```bash
go install github.com/owasp-amass/amass/v4/...@master
```

**Basic Usage:**
```bash
# Passive enumeration
amass enum -passive -d example.com

# Active enumeration (slower, more thorough)
amass enum -active -d example.com

# Output to file
amass enum -d example.com -o amass.txt

# Visualize results
amass viz -d3
```

**Pro Tips:**
- Passive is faster but less thorough
- Active includes DNS resolution and scraping
- Use for deep recon on high-value targets

---

### Waybackurls
**Purpose:** Fetch URLs from Wayback Machine

**Installation:**
```bash
go install github.com/tomnomnom/waybackurls@latest
```

**Basic Usage:**
```bash
# Single domain
echo "example.com" | waybackurls

# Multiple domains
cat domains.txt | waybackurls

# Output to file
echo "example.com" | waybackurls > wayback.txt

# With dates
echo "example.com" | waybackurls -dates
```

**Pro Tips:**
- Great for finding old endpoints
- Combine with `grep` to filter interesting URLs
- Use `-dates` to find recently added URLs

---

### Katana
**Purpose:** Web crawler

**Installation:**
```bash
go install github.com/projectdiscovery/katana/cmd/katana@latest
```

**Basic Usage:**
```bash
# Crawl single URL
katana -u https://example.com

# Crawl list of URLs
cat urls.txt | katana

# Headless crawling (JavaScript rendering)
katana -u https://example.com -headless

# Output to file
katana -u https://example.com -o crawled.txt
```

**Pro Tips:**
- Use `-headless` for SPAs (React, Vue, Angular)
- Combine with `waybackurls` for comprehensive coverage
- Use `-depth` to control crawl depth

---

## Scanning Tools

### Nuclei
**Purpose:** Vulnerability scanner

**Installation:**
```bash
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -update-templates
```

**Basic Usage:**
```bash
# Scan single target
nuclei -u https://example.com

# Scan list of targets
nuclei -l targets.txt

# Specific templates
nuclei -u https://example.com -t exposures/

# Rate limiting
nuclei -u https://example.com -rate-limit 100

# Output formats
nuclei -u https://example.com -o results.txt
nuclei -u https://example.com -json -o results.json
```

**Pro Tips:**
- Keep templates updated: `nuclei -update-templates`
- Use `-severity` to filter by severity
- Be careful with rate limits on production

---

### Nmap
**Purpose:** Port scanner

**Installation:**
```bash
sudo apt install nmap
```

**Basic Usage:**
```bash
# Quick scan
nmap -F example.com

# Full port scan
nmap -p- example.com

# Service detection
nmap -sV example.com

# OS detection
nmap -O example.com

# Script scan
nmap --script vuln example.com

# Output formats
nmap -oA scan_results example.com
```

**Pro Tips:**
- Use `-Pn` if host doesn't respond to ping
- `-sV` is slower but gives service versions
- Use `-T4` for faster scanning

---

## Exploitation Tools

### SQLMap
**Purpose:** SQL injection automation

**Installation:**
```bash
pip install sqlmap
```

**Basic Usage:**
```bash
# Basic scan
sqlmap -u "http://example.com/page.php?id=1"

# POST request
sqlmap -u "http://example.com/login" --data="user=admin&pass=test"

# Dump database
sqlmap -u "http://example.com/page.php?id=1" --dump

# Get tables
sqlmap -u "http://example.com/page.php?id=1" --tables

# Specific table
sqlmap -u "http://example.com/page.php?id=1" -T users --dump

# Batch mode (no prompts)
sqlmap -u "http://example.com/page.php?id=1" --batch
```

**Pro Tips:**
- Always get permission before using
- Use `--batch` for automation
- `--level` and `--risk` for more thorough testing

---

### Burp Suite
**Purpose:** Web proxy and testing platform

**Installation:**
Download from: https://portswigger.net/burp/communitydownload

**Basic Setup:**
1. Launch: `java -jar burpsuite_community.jar`
2. Set browser proxy to 127.0.0.1:8080
3. Install CA certificate in browser
4. Start intercepting traffic

**Key Features:**
- **Proxy:** Intercept and modify requests
- **Repeater:** Manual request modification
- **Intruder:** Automated attacks
- **Scanner:** Vulnerability detection (Pro only)
- **Decoder:** Encode/decode data
- **Comparer:** Compare requests/responses

**Pro Tips:**
- Use Repeater for manual testing
- Save interesting requests
- Use Intruder for fuzzing
- Learn keyboard shortcuts

---

## Utility Tools

### GF (Grep on Steroids)
**Purpose:** Pattern matching for URLs

**Installation:**
```bash
go install github.com/tomnomnom/gf@latest
```

**Basic Usage:**
```bash
# Load patterns
gf -list

# Find XSS candidates
cat urls.txt | gf xss

# Find SSRF candidates
cat urls.txt | gf ssrf

# Find interesting parameters
cat urls.txt | gf interestingparams
```

**Pro Tips:**
- Create custom patterns in ~/.gf/
- Combine with other tools for filtering
- Great for finding specific vulnerability patterns

---

### Unfurl
**Purpose:** URL analysis

**Installation:**
```bash
go install github.com/tomnomnom/unfurl@latest
```

**Basic Usage:**
```bash
# Extract domains
cat urls.txt | unfurl domains

# Extract paths
cat urls.txt | unfurl paths

# Extract keys
cat urls.txt | unfurl keys

# Extract values
cat urls.txt | unfurl values
```

**Pro Tips:**
- Great for analyzing URL patterns
- Use for parameter discovery
- Combine with other tools

---

## Workflow Examples

### Full Recon Workflow
```bash
# 1. Subdomain enumeration
subfinder -d example.com -o subs.txt

# 2. Find live hosts
cat subs.txt | httpx -o live.txt

# 3. Wayback URLs
cat live.txt | waybackurls > wayback.txt

# 4. Crawl
cat live.txt | katana > crawled.txt

# 5. Combine
cat wayback.txt crawled.txt | sort -u > all_urls.txt

# 6. Find interesting
cat all_urls.txt | gf interestingparams > interesting.txt
```

### Vulnerability Scanning Workflow
```bash
# 1. Nuclei scan
nuclei -l live.txt -o nuclei_results.txt

# 2. Manual testing with Burp
# - Import URLs
# - Test for XSS, SQLi, IDOR
# - Document findings

# 3. SQLMap on interesting params
cat urls_with_params.txt | grep "id=" | sqlmap --batch
```

### Report Generation Workflow
```bash
# 1. Document findings
# 2. Take screenshots
# 3. Write reproduction steps
# 4. Generate report with report_gen.py
python3 report_gen.py --template xss --program target --component "search" --severity High --url "https://target.com/search"
```

## Tool Comparison

| Task | Primary Tool | Alternative |
|------|--------------|-------------|
| Subdomain enum | subfinder | amass, assetfinder |
| HTTP probing | httpx | httprobe, meg |
| Web crawling | katana | gospider, hakrawler |
| Vuln scanning | nuclei | nikto, skipfish |
| SQL injection | sqlmap | manual testing |
| Proxy | Burp Suite | OWASP ZAP, Caido |
| Pattern matching | gf | grep, awk |

## Resources

- ProjectDiscovery Tools: https://github.com/projectdiscovery
- TomNomNom Tools: https://github.com/tomnomnom
- SecLists Wordlists: https://github.com/danielmiessler/SecLists
- PayloadsAllTheThings: https://github.com/swisskyrepo/PayloadsAllTheThings
