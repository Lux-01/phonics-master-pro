# HackerOne Platform Guide

Complete guide to using HackerOne for bug bounty hunting.

## Getting Started

### Creating an Account

1. Go to https://hackerone.com
2. Click "Sign Up"
3. Choose "Hacker" account type
4. Verify email
5. Complete profile
6. Set up 2FA (strongly recommended)

### Profile Setup

**Important fields:**
- **Username:** Professional, memorable
- **Bio:** Your skills, experience, focus areas
- **Location:** Timezone for communications
- **Website/Portfolio:** Link to your blog, GitHub, etc.
- **Skills:** Web, Mobile, API, etc.

**Profile Tips:**
- Use real name (builds trust)
- Link to disclosed reports
- Mention any certifications
- Keep it professional

---

## Finding Programs

### Program Types

**Public Programs:**
- Open to all hackers
- Listed on HackerOne directory
- Various bounty ranges

**Private Programs:**
- Invite-only
- Often higher bounties
- Less competition
- Build reputation to get invited

**Vulnerability Disclosure Programs (VDPs):**
- No monetary rewards
- Safe practice environment
- Build reputation
- Good for beginners

### Searching Programs

**Filters:**
- Bounty range
- Scope (wide vs narrow)
- Response time
- Triage rating
- Program type

**Good Beginner Programs:**
- Wide scope (more surface area)
- Fast response times
- Clear scope definitions
- Active triage team

### Evaluating Programs

**Check Before Hacking:**
- [ ] Read scope carefully
- [ ] Check bounty ranges
- [ ] Review response time stats
- [ ] Read program policy
- [ ] Check for exclusions
- [ ] Look at disclosed reports

**Red Flags:**
- Extremely narrow scope
- Slow response times
- Low bounties for critical bugs
- Unclear policies
- Poor communication

---

## Submitting Reports

### Report Structure

**Required Sections:**
1. **Title:** Clear, specific vulnerability name
2. **Description:** What the bug is
3. **Steps to Reproduce:** Numbered, detailed
4. **Proof of Concept:** Screenshots, videos, code
5. **Impact:** What attacker could do
6. **Mitigation:** How to fix

### Severity Selection

**Critical (CVSS 9.0-10.0):**
- Remote Code Execution
- SQL Injection with data exfiltration
- Mass account takeover
- Authentication bypass to admin

**High (CVSS 7.0-8.9):**
- Stored XSS
- IDOR sensitive data
- SSRF with internal access
- Privilege escalation

**Medium (CVSS 4.0-6.9):**
- Reflected XSS
- CSRF
- Information disclosure

**Low (CVSS 0.1-3.9):**
- Missing headers
- Verbose errors

### Submission Process

1. **Draft Report:**
   - Write clear description
   - Include reproduction steps
   - Attach proof of concept
   - Select severity

2. **Submit:**
   - Double-check scope
   - Verify it's not a duplicate
   - Submit report

3. **Triage:**
   - Program reviews report
   - May ask questions
   - Validates vulnerability

4. **Resolution:**
   - Bug is fixed
   - Bounty is awarded
   - Optional public disclosure

---

## Report States

**New:**
- Just submitted
- Awaiting triage

**Triaged:**
- Validated by program
- Severity assigned
- Bounty determined

**Resolved:**
- Bug is fixed
- Bounty paid
- May be disclosed

**Duplicate:**
- Already reported
- No bounty (usually)
- Check disclosed reports first

**Informative:**
- Not a security issue
- Or out of scope
- No bounty

**Not Applicable:**
- Doesn't meet criteria
- Not reproducible
- Expected behavior

---

## Communication

### With Triage Team

**Do:**
- Be professional and polite
- Respond promptly to questions
- Provide additional info when asked
- Ask for clarification if needed

**Don't:**
- Be rude or demanding
- Spam with messages
- Disclose before fix
- Argue excessively about severity

### Report Updates

**When to Update:**
- Additional findings
- Better proof of concept
- Related vulnerabilities
- Fix verification

**How to Update:**
- Comment on report
- Provide clear information
- Reference original finding

---

## Bounties

### Payment Process

1. **Report Triaged:**
   - Severity assigned
   - Bounty amount determined

2. **Bug Fixed:**
   - Program confirms fix
   - Bounty awarded

3. **Payment:**
   - Sent to HackerOne account
   - Available for withdrawal

4. **Withdrawal:**
   - PayPal
   - Bank transfer
   - Bitcoin

### Tax Considerations

**Important:**
- Bounties are taxable income
- Report on tax returns
- Keep records of payments
- Consult tax professional

**Forms:**
- W-9 (US persons)
- W-8BEN (Non-US persons)
- May be required for large payments

---

## Reputation System

### Signal

**What It Is:**
- Reputation metric
- Based on report quality
- Affects private invites

**How It's Calculated:**
- Valid reports increase signal
- Invalid reports decrease signal
- Duplicate ratio matters

**Good Signal:**
- More private program invites
- Higher trust from programs
- Better standing

### Leaderboard

**Types:**
- All-time earnings
- Yearly earnings
- Quarterly earnings
- By country
- By program

**Benefits:**
- Recognition
- Job opportunities
- Speaking invitations
- Credibility

---

## Best Practices

### Before Submitting

- [ ] Read scope carefully
- [ ] Check for duplicates
- [ ] Verify vulnerability
- [ ] Document everything
- [ ] Write clear report

### During Triage

- [ ] Respond promptly
- [ ] Be professional
- [ ] Provide additional info
- [ ] Ask questions if unclear

### After Resolution

- [ ] Thank the program
- [ ] Request disclosure if desired
- [ ] Write blog post (if disclosed)
- [ ] Add to portfolio

---

## Common Mistakes

### Submission Mistakes

**Out of Scope:**
- Always check scope first
- Don't test excluded assets
- Respect program boundaries

**Duplicates:**
- Search disclosed reports
- Check recent submissions
- Ask in program chat if unsure

**Poor Reports:**
- Unclear descriptions
- Missing reproduction steps
- No proof of concept
- Wrong severity

### Communication Mistakes

**Being Impatient:**
- Triage takes time
- Don't spam messages
- Wait for responses

**Being Rude:**
- Stay professional
- Don't argue excessively
- Accept decisions gracefully

**Premature Disclosure:**
- Never disclose before fix
- Wait for program approval
- Follow responsible disclosure

---

## Advanced Tips

### Getting Private Invites

1. **Build Reputation:**
   - Submit quality reports
   - Maintain good signal
   - Be professional

2. **Network:**
   - Join HackerOne Discord
   - Attend conferences
   - Engage on Twitter

3. **Specialize:**
   - Focus on specific bug classes
   - Build expertise
   - Become known for quality

### Maximizing Bounties

1. **Demonstrate Impact:**
   - Show real exploitation
   - Chain vulnerabilities
   - Document business impact

2. **Write Great Reports:**
   - Clear and professional
   - Easy to reproduce
   - Include mitigation

3. **Build Relationships:**
   - Be reliable
   - Communicate well
   - Become trusted researcher

### Staying Updated

**Follow:**
- HackerOne blog
- @Hacker0x01 on Twitter
- HackerOne Discord
- Security researchers

**Read:**
- Disclosed reports
- Security blogs
- CVE announcements
- Research papers

---

## Resources

### Official
- HackerOne Docs: https://docs.hackerone.com/
- HackerOne Blog: https://www.hackerone.com/blog
- Hacktivity: https://hackerone.com/hacktivity

### Community
- Discord: https://discord.gg/hackerone
- Twitter: #bugbounty, #infosec
- Reddit: r/bugbounty

### Learning
- Hacker101: https://www.hacker101.com/
- PortSwigger: https://portswigger.net/web-security
- Web Security Academy: https://portswigger.net/web-security

---

## Support

**Need Help?**
- HackerOne Support: support@hackerone.com
- Community Discord
- Twitter: @Hacker0x01

**Report Issues:**
- Platform bugs
- Payment issues
- Account problems
