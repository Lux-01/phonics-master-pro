# OWASP Top 10 (2021)

The ten most critical web application security risks.

## A01:2021 - Broken Access Control

**Description:** Restrictions on authenticated users are not properly enforced.

**Common Issues:**
- IDOR (Insecure Direct Object Reference)
- Path traversal
- Missing function-level access control
- CORS misconfiguration
- JWT weaknesses

**Testing:**
- Change IDs in URLs (user_id=1 → user_id=2)
- Access admin functions as regular user
- Test CORS configurations
- Manipulate JWT tokens

**Impact:** Unauthorized data access, privilege escalation

**Real Example:**
```
GET /api/user/123/profile → returns user 123 data
GET /api/user/124/profile → returns user 124 data (IDOR)
```

---

## A02:2021 - Cryptographic Failures

**Description:** Sensitive data exposed due to weak cryptography.

**Common Issues:**
- Plaintext data transmission
- Weak encryption algorithms
- Hardcoded credentials
- Insufficient randomness

**Testing:**
- Check for HTTPS enforcement
- Look for hardcoded keys in source code
- Test password reset tokens for predictability

**Impact:** Data theft, session hijacking

---

## A03:2021 - Injection

**Description:** Untrusted data sent to interpreter as command.

**Types:**
- SQL Injection
- NoSQL Injection
- Command Injection
- LDAP Injection
- XPath Injection
- Template Injection (SSTI)

**SQL Injection Testing:**
```sql
' OR '1'='1
' UNION SELECT null,null--
' AND 1=1--
' AND 1=2--
```

**Command Injection Testing:**
```
; cat /etc/passwd
| whoami
`id`
$(ls -la)
```

**Impact:** Data loss, server takeover, RCE

---

## A04:2021 - Insecure Design

**Description:** Fundamental design flaws in application logic.

**Examples:**
- Business logic flaws
- Race conditions
- Insecure workflow
- Missing security controls

**Testing:**
- Understand business logic
- Test multi-step processes
- Look for race conditions
- Check for price/quantity manipulation

**Impact:** Financial loss, unauthorized actions

---

## A05:2021 - Security Misconfiguration

**Description:** Insecure default configurations, incomplete setups.

**Common Issues:**
- Default credentials
- Unnecessary features enabled
- Verbose error messages
- Missing security headers
- Directory listing enabled

**Testing:**
- Check /admin, /config, /.git, /.env
- Test default passwords
- Review security headers
- Check for stack traces in errors

**Impact:** Information disclosure, unauthorized access

---

## A06:2021 - Vulnerable and Outdated Components

**Description:** Using components with known vulnerabilities.

**Testing:**
- Identify technology stack (Wappalyzer)
- Check versions of frameworks/libraries
- Search CVE databases
- Look for known exploits

**Impact:** Depends on component vulnerability

---

## A07:2021 - Identification and Authentication Failures

**Description:** Authentication weaknesses allowing account compromise.

**Common Issues:**
- Brute force attacks possible
- Weak password policies
- Session fixation
- Missing MFA
- JWT vulnerabilities

**Testing:**
- Test password reset flows
- Check for brute force protection
- Test session management
- Manipulate JWT tokens

**Impact:** Account takeover, unauthorized access

---

## A08:2021 - Software and Data Integrity Failures

**Description:** Code and infrastructure without integrity verification.

**Examples:**
- Insecure deserialization
- Unsigned updates
- CI/CD pipeline vulnerabilities

**Testing:**
- Test deserialization endpoints
- Look for serialized objects in requests
- Check for RCE via deserialization

**Impact:** RCE, data tampering

---

## A09:2021 - Security Logging and Monitoring Failures

**Description:** Insufficient logging and monitoring.

**Note:** This is harder to test as a bug hunter, but important for defense.

---

## A10:2021 - Server-Side Request Forgery (SSRF)

**Description:** Server makes requests to attacker-controlled URLs.

**Testing:**
```
?url=http://localhost:22
?url=http://169.254.169.254/latest/meta-data/  # AWS metadata
?url=file:///etc/passwd
?url=dict://localhost:11211/stat  # Memcached
```

**Impact:** Internal network access, cloud metadata exposure

---

## Testing Priority

For bug bounty hunting, prioritize:

1. **Injection (A03)** - High impact, common
2. **Broken Access Control (A01)** - Easy to find, good payouts
3. **Authentication Failures (A07)** - Account takeover potential
4. **SSRF (A10)** - Often leads to RCE
5. **Security Misconfiguration (A05)** - Low hanging fruit

## Resources

- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
