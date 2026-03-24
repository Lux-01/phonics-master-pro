# Report Templates

Professional vulnerability report templates for HackerOne submissions.

## Standard Report Template

```markdown
# Vulnerability Report

## Executive Summary
[Brief summary of the vulnerability and its impact - 2-3 sentences]

## Vulnerability Details

**Type:** [XSS/SQLi/IDOR/etc.]
**Severity:** [Critical/High/Medium/Low]
**Affected URL(s):**
- [URL 1]
- [URL 2]

## Description
[Detailed description of the vulnerability]

## Steps to Reproduce
1. [Step 1 - Be specific]
2. [Step 2]
3. [Step 3]
4. [Expected vs actual result]

## Proof of Concept

### HTTP Request
```http
GET /vulnerable-endpoint?param=payload HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0
```

### HTTP Response
```http
HTTP/1.1 200 OK
Content-Type: text/html

[Relevant response showing vulnerability]
```

### Screenshot/Video
[Attach screenshot or screen recording]

## Impact
[Describe what an attacker could do]

- [Impact point 1]
- [Impact point 2]
- [Impact point 3]

## Mitigation
[How to fix this vulnerability]

1. [Fix recommendation 1]
2. [Fix recommendation 2]

## References
- [Link to relevant documentation]
- [Similar CVE or writeup]

## Reporter Information
**HackerOne Username:** [username]
**Contact:** [email if desired]
```

---

## XSS Report Template

```markdown
# Stored XSS in Comment Functionality

## Summary
The comment functionality on [URL] is vulnerable to stored XSS, allowing attackers to execute JavaScript in victims' browsers when they view the comment.

## Severity
High

## Steps to Reproduce
1. Navigate to [URL]/post/123
2. Scroll to comment section
3. Enter the following payload in comment field:
   ```
   <img src=x onerror=alert(document.cookie)>
   ```
4. Submit comment
5. View comment as another user (or in incognito)
6. Observe JavaScript execution

## Proof of Concept
[Screenshot showing alert box]

## Impact
- Steal user session cookies
- Perform actions on behalf of users
- Deface website
- Redirect users to malicious sites

## Affected Users
All users who view the infected comment.

## Mitigation
1. HTML encode all user input before rendering
2. Implement Content Security Policy (CSP)
3. Use DOMPurify or similar library
4. Validate input on server side

## References
- OWASP XSS Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
```

---

## SQL Injection Report Template

```markdown
# SQL Injection in Search Function

## Summary
The search functionality at [URL]/search is vulnerable to SQL injection, allowing extraction of database contents.

## Severity
Critical

## Steps to Reproduce
1. Navigate to [URL]/search
2. Enter the following in search field:
   ```
   ' UNION SELECT username,password,email FROM users--
   ```
3. Submit search
4. Observe user credentials in results

## Proof of Concept

### Request
```http
GET /search?q=' UNION SELECT username,password,email FROM users-- HTTP/1.1
Host: target.com
```

### Response
```http
HTTP/1.1 200 OK

[Response showing extracted data]
```

## Impact
- Extract entire database contents
- Bypass authentication
- Modify/delete data
- Potential server compromise

## Mitigation
1. Use parameterized queries/prepared statements
2. Input validation and sanitization
3. Principle of least privilege for DB user
4. Web Application Firewall (WAF)

## References
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
```

---

## IDOR Report Template

```markdown
# IDOR: Access Other Users' Order Details

## Summary
The order details endpoint lacks proper authorization checks, allowing any authenticated user to view other users' orders by changing the order ID.

## Severity
High

## Steps to Reproduce
1. Login as User A
2. Navigate to order details: [URL]/orders/12345
3. Note your order ID in URL
4. Change order ID to another number: [URL]/orders/12346
5. Observe you can view User B's order details

## Proof of Concept
[Screenshot showing access to another user's order]

## Impact
- Access other users' personal information
- View order history and details
- Potential financial information exposure

## Affected Endpoints
- /orders/{id}
- /api/v1/orders/{id}

## Mitigation
1. Implement authorization checks on every endpoint
2. Verify user owns the resource before returning data
3. Use indirect object references (UUIDs instead of sequential IDs)
4. Log access attempts

## References
- OWASP IDOR: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References
```

---

## SSRF Report Template

```markdown
# SSRF in Image Upload via URL

## Summary
The image upload via URL feature is vulnerable to SSRF, allowing requests to internal services and cloud metadata endpoints.

## Severity
High

## Steps to Reproduce
1. Navigate to [URL]/upload
2. Select "Upload from URL" option
3. Enter internal URL:
   ```
   http://169.254.169.254/latest/meta-data/
   ```
4. Submit upload
5. Observe cloud metadata in response/error

## Proof of Concept

### Request
```http
POST /upload HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### Response
```http
HTTP/1.1 200 OK

[Cloud metadata including credentials]
```

## Impact
- Access internal services
- Cloud metadata exposure
- Potential credential theft
- Internal network reconnaissance

## Mitigation
1. Validate and sanitize URLs
2. Use allowlist of approved domains
3. Disable redirects
4. Run in isolated network segment
5. Disable access to internal IPs

## References
- OWASP SSRF: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
- SSRF Bible: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery
```

---

## Business Logic Report Template

```markdown
# Price Manipulation in Checkout Process

## Summary
The checkout process allows manipulation of item prices by modifying the price parameter in the POST request.

## Severity
High

## Steps to Reproduce
1. Add item to cart (Price: $100)
2. Proceed to checkout
3. Intercept checkout request with Burp Suite
4. Modify price parameter:
   ```
   From: price=100&item_id=123
   To: price=1&item_id=123
   ```
5. Forward request
6. Complete checkout for $1 instead of $100

## Proof of Concept
[Screenshot showing intercepted request and successful checkout]

## Impact
- Purchase items at arbitrary prices
- Financial loss to company
- Potential inventory manipulation

## Mitigation
1. Validate prices server-side against database
2. Don't trust client-submitted prices
3. Calculate totals server-side
4. Implement integrity checks

## References
- OWASP Business Logic: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/00-Introduction_to_Business_Logic
```

---

## Report Writing Tips

### Do's
- Be clear and concise
- Include step-by-step reproduction
- Provide proof of concept
- Demonstrate real impact
- Suggest fixes
- Be professional and respectful

### Don'ts
- Don't use automated scanner output without verification
- Don't submit theoretical vulnerabilities
- Don't exaggerate impact
- Don't submit duplicates (check first)
- Don't be rude or demanding
- Don't disclose before fix

### Severity Guidelines

**Critical ($5,000-$50,000+):**
- Remote Code Execution (RCE)
- SQL Injection with data exfiltration
- Authentication bypass to admin
- Mass account takeover

**High ($1,000-$10,000):**
- Stored XSS
- IDOR sensitive data
- SSRF with internal access
- Privilege escalation

**Medium ($500-$3,000):**
- Reflected XSS
- CSRF
- Information disclosure
- Weak cryptography

**Low ($100-$500):**
- Missing security headers
- Verbose error messages
- Best practice violations

### Response Templates

**When triage asks for more info:**
```
Hi [Name],

Thanks for the follow-up. Here are the additional details:

[Answer their specific questions]

Let me know if you need anything else.

Best regards,
[Your name]
```

**When bounty is lower than expected:**
```
Hi [Name],

Thank you for the bounty. I appreciate the team's time in triaging this.

I believe the severity could be [higher/lower] because [reasoning]. 
Would you be open to reconsidering based on [additional context]?

Regardless, I respect your decision and appreciate the program.

Best regards,
[Your name]
```

## Resources

- HackerOne Report Template: https://docs.hackerone.com/hackers/report-templates.html
- Bugcrowd Report Format: https://docs.bugcrowd.com/customers/reporting/report-formatting.html
- OWASP Writing Reports: https://owasp.org/www-project-web-security-testing-guide/latest/6-Appendix/A-Testing_Reporting_Format
