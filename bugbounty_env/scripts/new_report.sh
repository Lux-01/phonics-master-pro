#!/bin/bash
# Create new vulnerability report template
# Usage: ./new_report.sh program-name vulnerability-type

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./new_report.sh <program-name> <vulnerability-type>"
    echo "Example: ./new_report.sh hackerone stored-xss"
    exit 1
fi

PROGRAM=$1
VULN_TYPE=$2
DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/$PROGRAM-$DATE-$VULN_TYPE"
mkdir -p $REPORT_DIR

cat > $REPORT_DIR/report.md << EOL
# Vulnerability Report

## Program
**Program:** $PROGRAM  
**Date:** $DATE  
**Reporter:** [Your HackerOne Username]

## Vulnerability Information

**Type:** $VULN_TYPE  
**Severity:** [ ] Critical  [ ] High  [ ] Medium  [ ] Low  [ ] Informational  
**CVSS Score:** [If applicable]

## Summary

[Brief description of the vulnerability - 2-3 sentences]

## Steps to Reproduce

1. [First step - be specific]
2. [Second step]
3. [Third step]
4. [Expected result vs actual result]

## Proof of Concept

### Screenshot/Video
[Attach screenshots or screen recording showing the vulnerability]

### HTTP Request
\`\`\`http
[Include the raw HTTP request if applicable]
\`\`\`

### HTTP Response
\`\`\`http
[Include relevant parts of the response]
\`\`\`

### Code/Script
\`\`\`[language]
[If you used a script or specific payload, include it here]
\`\`\`

## Impact

[Describe what an attacker could do with this vulnerability]

- [Impact point 1]
- [Impact point 2]
- [Impact point 3]

## Affected URLs/Endpoints

- [URL 1]
- [URL 2]
- [URL 3]

## Mitigation / Fix

[Suggest how to fix this vulnerability]

1. [Fix recommendation 1]
2. [Fix recommendation 2]

## References

- [Link to relevant documentation]
- [Link to similar CVE or writeup]
- [OWASP reference]

## Additional Notes

[Any other information that might be helpful]

---

**Disclaimer:** This vulnerability was discovered in accordance with the program's security policy and scope. No data was accessed, modified, or deleted beyond what was necessary to demonstrate the vulnerability.
EOL

cat > $REPORT_DIR/notes.txt << EOL
# Research Notes for $VULN_TYPE on $PROGRAM

## Discovery Method
[How did you find this? Manual testing, automation, etc.]

## Testing Environment
- Browser: 
- Tools used: 
- Time spent: 

## Attempts That Didn't Work
[Document failed attempts - helps avoid duplicates]

## Related Findings
[Any other similar issues found]

## Follow-up Questions
[Questions for the program during triage]

## Timeline
- Discovered: $DATE
- Reported: [Date]
- Triaged: [Date]
- Resolved: [Date]
- Bounty: [Amount]
EOL

echo "=========================================="
echo "✅ Report template created!"
echo "=========================================="
echo ""
echo "Location: $REPORT_DIR/"
echo ""
echo "Files created:"
echo "  - report.md      # Main vulnerability report"
echo "  - notes.txt      # Your research notes"
echo ""
echo "Next steps:"
echo "  1. Edit: nano $REPORT_DIR/report.md"
echo "  2. Add screenshots to $REPORT_DIR/"
echo "  3. Submit to HackerOne"
echo ""
