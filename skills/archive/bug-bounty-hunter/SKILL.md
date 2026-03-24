---
name: bug-bounty-hunter
description: Expert bug bounty hunter for HackerOne and other platforms. Automates reconnaissance, vulnerability discovery, report generation, and submission workflows. Use when hunting for security vulnerabilities, performing penetration testing on authorized targets, generating professional bug reports, or analyzing web applications for security flaws. Integrates with bugbounty_env testing environment.
---

# Bug Bounty Hunter

Expert bug bounty hunter skill for finding and reporting security vulnerabilities on HackerOne and other platforms.

## Overview

This skill transforms OpenClaw into an expert bug bounty hunter capable of:
- Automated reconnaissance and target mapping
- Vulnerability discovery and exploitation
- Professional report generation
- Workflow automation for efficient hunting

## When to Use This Skill

- Hunting for security vulnerabilities on HackerOne programs
- Performing authorized penetration testing
- Generating professional vulnerability reports
- Analyzing web applications for security flaws
- Automating repetitive reconnaissance tasks
- Researching and documenting new attack vectors

## Prerequisites

1. **Bug Bounty Environment** set up at `/home/skux/.openclaw/workspace/bugbounty_env/`
2. **HackerOne account** created and verified
3. **Tools installed** per INSTALL.md in bugbounty_env
4. **Legal authorization** - Only test systems you have permission to test

## Quick Start

```bash
# Activate environment
cd /home/skux/.openclaw/workspace/bugbounty_env
source activate_env.sh

# Run full recon on target
./scripts/recon.sh target.com

# Analyze results and identify vulnerabilities
# Generate report
./scripts/new_report.sh program-name vulnerability-type
```

## Core Workflows

### 1. Target Reconnaissance

**Purpose:** Map the attack surface of a target

**Steps:**
1. Run `recon.sh <target.com>`
2. Review `targets/target.com-*/` output
3. Identify interesting endpoints from `interesting_urls.txt`
4. Prioritize URLs with parameters for testing

**Key Files:**
- `subdomains.txt` - Discovered subdomains
- `live_hosts.txt` - Live web servers
- `all_urls.txt` - All discovered URLs
- `interesting_urls.txt` - High-value endpoints
- `urls_with_params.txt` - XSS/Injection candidates

### 2. Vulnerability Discovery

**Purpose:** Find security vulnerabilities

**Approach:**
- Start with OWASP Top 10
- Focus on one bug class at a time
- Use automation for coverage, manual for logic bugs
- Document everything with screenshots

**Common Targets:**
- Login/registration forms (Auth bypass, XSS)
- Search functionality (SQLi, XSS)
- File uploads (RCE, path traversal)
- API endpoints (IDOR, auth issues)
- Admin panels (Access control)

### 3. Report Generation

**Purpose:** Create professional vulnerability reports

**Command:**
```bash
./scripts/new_report.sh <program> <vulnerability-type>
```

**Report Structure:**
- Clear title and severity
- Step-by-step reproduction
- Proof of concept (PoC)
- Impact demonstration
- Mitigation suggestions

### 4. Submission Workflow

**Purpose:** Submit reports to HackerOne

**Steps:**
1. Review program scope carefully
2. Ensure vulnerability is in scope
3. Write clear, professional report
4. Submit via HackerOne platform
5. Respond to triage questions promptly

## Reference Materials

For detailed information, see:

- **[references/owasp-top10.md](references/owasp-top10.md)** - OWASP Top 10 vulnerabilities
- **[references/bug-classes.md](references/bug-classes.md)** - Detailed bug class explanations
- **[references/report-templates.md](references/report-templates.md)** - Report templates by bug type
- **[references/tools-guide.md](references/tools-guide.md)** - Tool usage and commands
- **[references/methodology.md](references/methodology.md)** - Testing methodology
- **[references/hackerone-guide.md](references/hackerone-guide.md)** - HackerOne platform guide

## Automation Scripts

### recon.sh
Full reconnaissance automation. See `scripts/recon.sh`

### check_xss.sh
Quick XSS parameter testing. See `scripts/check_xss.sh`

### new_report.sh
Generate report templates. See `scripts/new_report.sh`

### vuln_scan.py
Automated vulnerability scanning. See `scripts/vuln_scan.py`

## Integration with Bug Bounty Environment

This skill works with the bugbounty_env at:
`/home/skux/.openclaw/workspace/bugbounty_env/`

**Key Integration Points:**
- Uses `scripts/` from bugbounty_env
- Reads `targets/` for recon data
- Writes `reports/` for submissions
- References `notes/` for methodology

## Safety & Ethics

**CRITICAL RULES:**
1. Only test systems you have explicit permission to test
2. Always read program scope before testing
3. Never access data beyond what's necessary to demonstrate vulnerability
4. Do not damage systems or delete data
5. Follow responsible disclosure practices
6. Unauthorized access is illegal

## Learning Path

**Beginner (Months 1-3):**
- Complete PortSwigger Web Security Academy
- Practice on HackTheBox
- Read 50+ disclosed HackerOne reports
- Submit first VDP (no payout) report

**Intermediate (Months 3-6):**
- Find first valid bounty
- Specialize in 2-3 bug classes
- Build automation scripts
- Join bug bounty communities

**Advanced (Months 6-12):**
- Consistent bounty earnings
- Target high-paying programs
- Develop unique techniques
- Mentor others

## Expected Results

| Phase | Timeline | Earnings |
|-------|----------|----------|
| Learning | Months 1-3 | $0 |
| First Bounty | Months 3-6 | $0-1,000 |
| Consistent | Months 6-12 | $1,000-10,000 |
| Intermediate | Year 2 | $10,000-50,000 |
| Advanced | Year 3+ | $50,000-200,000 |

## Tips for Success

1. **Start with learning** - Don't hunt before you understand the basics
2. **Focus** - Master one bug class before moving to next
3. **Document** - Screenshots and notes are crucial
4. **Be patient** - First bounty takes 3-6 months typically
5. **Read reports** - Study disclosed reports on HackerOne
6. **Automate** - Build scripts for repetitive tasks
7. **Network** - Join communities, share knowledge

## Resources

- **PortSwigger Academy:** https://portswigger.net/web-security
- **HackerOne:** https://hackerone.com
- **HackTheBox:** https://www.hackthebox.com
- **Hacker101:** https://www.hacker101.com

## Troubleshooting

**Tool not found?**
```bash
# Check INSTALL.md in bugbounty_env
cat /home/skux/.openclaw/workspace/bugbounty_env/INSTALL.md
```

**Need wordlists?**
```bash
cd /home/skux/.openclaw/workspace/bugbounty_env
git clone --depth 1 https://github.com/danielmiessler/SecLists.git wordlists/seclists
```

**Report format questions?**
```bash
cat references/report-templates.md
```
