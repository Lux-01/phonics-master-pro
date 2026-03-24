#!/usr/bin/env python3
"""
Report Generator - Create professional vulnerability reports
Part of bug-bounty-hunter skill

Usage:
    python3 report_gen.py --program hackerone --type xss --severity high
    python3 report_gen.py --template idor --output my_report.md
"""

import argparse
import os
from datetime import datetime

# Report templates
TEMPLATES = {
    'xss': """# Stored XSS in {component}

## Executive Summary
The {component} functionality on {program} is vulnerable to stored XSS, allowing attackers to execute JavaScript in victims' browsers.

## Vulnerability Details
- **Type:** Cross-Site Scripting (XSS)
- **Severity:** {severity}
- **Affected URL(s):**
  - {affected_url}

## Description
The application fails to properly sanitize user input in the {component} functionality, allowing injection of malicious JavaScript code. This code is stored in the database and executed when other users view the affected content.

## Steps to Reproduce
1. Navigate to {affected_url}
2. Locate the {component} input field
3. Enter the following payload:
   ```
   <img src=x onerror=alert(document.cookie)>
   ```
4. Submit the form
5. View the content as another user (or in incognito mode)
6. Observe the JavaScript execution (alert popup)

## Proof of Concept
[Attach screenshot showing the XSS execution]

## Impact
An attacker can:
- Steal user session cookies
- Perform actions on behalf of authenticated users
- Deface the website
- Redirect users to malicious websites
- Keylog user input

## Affected Users
All users who view the infected content, including administrators.

## Mitigation
1. HTML encode all user input before rendering in the browser
2. Implement a Content Security Policy (CSP)
3. Use a library like DOMPurify to sanitize HTML
4. Validate input on the server side
5. Use HttpOnly flag on session cookies

## References
- OWASP XSS Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- CWE-79: https://cwe.mitre.org/data/definitions/79.html

## Reporter
**HackerOne Username:** {reporter}
**Date:** {date}
""",

    'sql': """# SQL Injection in {component}

## Executive Summary
The {component} functionality on {program} is vulnerable to SQL injection, allowing attackers to extract, modify, or delete database contents.

## Vulnerability Details
- **Type:** SQL Injection
- **Severity:** {severity}
- **Affected URL(s):**
  - {affected_url}

## Description
User-supplied input is directly concatenated into SQL queries without proper sanitization or parameterization, allowing attackers to inject malicious SQL code.

## Steps to Reproduce
1. Navigate to {affected_url}
2. Enter the following in the {component} field:
   ```
   ' UNION SELECT username,password,email FROM users--
   ```
3. Submit the request
4. Observe that user credentials are displayed in the response

## Proof of Concept

### HTTP Request
```http
GET {endpoint}?param=' UNION SELECT username,password,email FROM users-- HTTP/1.1
Host: {host}
```

### HTTP Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

[Response showing extracted data]
```

## Impact
An attacker can:
- Extract entire database contents
- Bypass authentication mechanisms
- Modify or delete data
- Potentially achieve remote code execution
- Access sensitive user information

## Mitigation
1. Use parameterized queries or prepared statements
2. Implement input validation and sanitization
3. Apply principle of least privilege to database accounts
4. Use Web Application Firewall (WAF) as additional layer
5. Disable detailed error messages in production

## References
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- CWE-89: https://cwe.mitre.org/data/definitions/89.html

## Reporter
**HackerOne Username:** {reporter}
**Date:** {date}
""",

    'idor': """# IDOR: Insecure Direct Object Reference in {component}

## Executive Summary
The {component} functionality on {program} lacks proper authorization checks, allowing authenticated users to access other users' data by manipulating object identifiers.

## Vulnerability Details
- **Type:** Insecure Direct Object Reference (IDOR)
- **Severity:** {severity}
- **Affected URL(s):**
  - {affected_url}

## Description
The application uses sequential or predictable identifiers for objects (orders, invoices, user profiles) and fails to verify that the requesting user has permission to access the requested resource.

## Steps to Reproduce
1. Login as User A
2. Navigate to your {component}: {affected_url}/12345
3. Note your {component} ID in the URL
4. Change the ID to access another user's {component}: {affected_url}/12346
5. Observe that you can view User B's {component} details

## Proof of Concept
[Attach screenshot showing access to another user's data]

## Impact
An attacker can:
- Access other users' sensitive information
- View private data (orders, invoices, personal details)
- Potentially modify other users' data
- Enumerate all objects in the system

## Affected Endpoints
- {affected_url}/{id}
- /api/v1/{component}/{id}

## Mitigation
1. Implement authorization checks on every endpoint
2. Verify the requesting user owns the resource before returning data
3. Use indirect object references (UUIDs instead of sequential IDs)
4. Implement rate limiting to prevent enumeration
5. Log access attempts for sensitive resources

## References
- OWASP IDOR: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References
- CWE-639: https://cwe.mitre.org/data/definitions/639.html

## Reporter
**HackerOne Username:** {reporter}
**Date:** {date}
""",

    'ssrf': """# Server-Side Request Forgery (SSRF) in {component}

## Executive Summary
The {component} functionality on {program} is vulnerable to SSRF, allowing attackers to make requests to internal services and cloud metadata endpoints.

## Vulnerability Details
- **Type:** Server-Side Request Forgery (SSRF)
- **Severity:** {severity}
- **Affected URL(s):**
  - {affected_url}

## Description
The application accepts user-supplied URLs and makes server-side requests to them without proper validation, allowing attackers to access internal resources and cloud metadata.

## Steps to Reproduce
1. Navigate to {affected_url}
2. Enter the following URL in the {component} field:
   ```
   http://169.254.169.254/latest/meta-data/
   ```
3. Submit the request
4. Observe that cloud metadata is returned in the response

## Proof of Concept

### HTTP Request
```http
POST {endpoint} HTTP/1.1
Host: {host}
Content-Type: application/x-www-form-urlencoded

url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### HTTP Response
```http
HTTP/1.1 200 OK

[Cloud metadata including temporary credentials]
```

## Impact
An attacker can:
- Access internal services and infrastructure
- Retrieve cloud metadata and credentials
- Scan internal network
- Access internal APIs and admin panels
- Potentially achieve remote code execution

## Mitigation
1. Validate and sanitize all user-supplied URLs
2. Use an allowlist of approved domains/IPs
3. Disable redirects or limit redirect hops
4. Run requests in isolated network segments
5. Disable access to internal IP ranges (169.254.x.x, 10.x.x.x, etc.)
6. Use DNS resolution validation

## References
- OWASP SSRF: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
- CWE-918: https://cwe.mitre.org/data/definitions/918.html
- SSRF Bible: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery

## Reporter
**HackerOne Username:** {reporter}
**Date:** {date}
""",

    'generic': """# {vuln_type} Vulnerability in {component}

## Executive Summary
[Brief summary of the vulnerability and its impact]

## Vulnerability Details
- **Type:** {vuln_type}
- **Severity:** {severity}
- **Affected URL(s):**
  - {affected_url}

## Description
[Detailed description of the vulnerability]

## Steps to Reproduce
1. [Step 1 - Be specific]
2. [Step 2]
3. [Step 3]
4. [Expected vs actual result]

## Proof of Concept
[Attach screenshot, HTTP request/response, or video]

## Impact
[Describe what an attacker could do with this vulnerability]

## Mitigation
[How to fix this vulnerability]

## References
- [Link to relevant documentation]
- [Similar CVE or writeup]

## Reporter
**HackerOne Username:** {reporter}
**Date:** {date}
"""
}

def generate_report(template_name, **kwargs):
    """Generate a report from template"""
    if template_name not in TEMPLATES:
        print(f"Error: Template '{template_name}' not found")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        return None
    
    template = TEMPLATES[template_name]
    return template.format(**kwargs)

def main():
    parser = argparse.ArgumentParser(description='Bug Bounty Report Generator')
    parser.add_argument('--template', '-t', required=True,
                       choices=['xss', 'sql', 'idor', 'ssrf', 'generic'],
                       help='Report template to use')
    parser.add_argument('--program', '-p', required=True,
                       help='Bug bounty program name')
    parser.add_argument('--component', '-c', required=True,
                       help='Affected component (e.g., "comment section", "search function")')
    parser.add_argument('--severity', '-s', required=True,
                       choices=['Critical', 'High', 'Medium', 'Low', 'Informational'],
                       help='Severity level')
    parser.add_argument('--url', '-u', required=True,
                       help='Affected URL')
    parser.add_argument('--reporter', '-r', default='[Your username]',
                       help='Your HackerOne username')
    parser.add_argument('--output', '-o', help='Output file (default: print to stdout)')
    parser.add_argument('--vuln-type', '-v', help='Vulnerability type (for generic template)')
    parser.add_argument('--endpoint', '-e', help='API endpoint (for detailed templates)')
    parser.add_argument('--host', help='Host header value (for detailed templates)')
    
    args = parser.parse_args()
    
    # Prepare template variables
    template_vars = {
        'program': args.program,
        'component': args.component,
        'severity': args.severity,
        'affected_url': args.url,
        'reporter': args.reporter,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'vuln_type': args.vuln_type or args.template.upper(),
        'endpoint': args.endpoint or '/api/v1/endpoint',
        'host': args.host or urlparse(args.url).netloc or 'target.com'
    }
    
    # Generate report
    report = generate_report(args.template, **template_vars)
    
    if report:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"[*] Report saved to: {args.output}")
        else:
            print(report)

if __name__ == '__main__':
    from urllib.parse import urlparse
    main()
