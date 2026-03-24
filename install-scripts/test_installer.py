#!/usr/bin/env python3
"""
OpenClaw Windows Installer Bug Report
Tests PowerShell and Batch files for common issues
"""

import sys

def analyze_powershell(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Check 1: WSL path issues
        if 'wsl -d Ubuntu-22.04 -u root cp' in line and '$env:TEMP' in line:
            if '"$temp' in line:
                pass  # Quoted
            else:
                issues.append({
                    'line': i,
                    'text': line.strip()[:50],
                    'issue': 'CRITICAL: $env:TEMP path passed to WSL needs Windows-to-Linux path conversion',
                    'severity': 'HIGH'
                })
        
        # Check 2: wsl --install is interactive
        if 'wsl --install -d Ubuntu-22.04' in line:
            issues.append({
                'line': i,
                'text': line.strip()[:50],
                'issue': 'CRITICAL: wsl --install is interactive (prompts for username/pass). Script will hang',
                'severity': 'HIGH'
            })
        
        # Check 3: Bash heredoc escaping
        if "cat > config.json << 'EOF'" in line or "cat \u003e config.json \u003c\u003c 'EOF'" in line:
            issues.append({
                'line': i,
                'text': line.strip()[:50],
                'issue': 'WARNING: Nested heredoc in bash inside PowerShell may have escaping issues',
                'severity': 'MEDIUM'
            })
        
        # Check 4: Error handling
        if 'errorlevel' in line.lower() and 'ne' in line.lower():
            if i + 1 < len(lines):
                next_line = lines[i].strip()
                if 'echo' in next_line.lower() or 'pause' in next_line.lower():
                    pass
                else:
                    issues.append({
                        'line': i,
                        'text': line.strip()[:50],
                        'issue': 'LOW: Error checking present but limited error handling in batch file',
                        'severity': 'LOW'
                    })
    
    return issues

def analyze_batch(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        lines = f.readlines()
    
    issues = []
    
    # Check for proper exit codes
    if 'exit /b 1' not in content:
        issues.append({
            'line': 0,
            'text': 'N/A',
            'issue': 'WARNING: No proper exit code on failure',
            'severity': 'LOW'
        })
    
    # Check for admin check
    if 'net session' in content:
        pass  # Good
    else:
        issues.append({
            'line': 0,
            'text': 'N/A',
            'issue': 'CRITICAL: No admin privilege check in batch file',
            'severity': 'HIGH'
        })
    
    # Check for proper error handling in PowerShell execution
    if '%~dp0' in content:
        pass  # Good - uses script directory
    else:
        issues.append({
            'line': 0,
            'text': 'N/A',
            'issue': 'WARNING: Not using script directory reference - may fail if run from different folder',
            'severity': 'MEDIUM'
        })
    
    return issues

print("=" * 70)
print("🐛 OPENCLAW WINDOWS INSTALLER BUG ANALYSIS")
print("=" * 70)

# Analyze PowerShell
print("\n📋 PowerShell Script Analysis:")
print("-" * 70)
ps_issues = analyze_powershell('openclaw-windows-installer.ps1')

if ps_issues:
    for issue in ps_issues:
        icon = '🔴' if issue['severity'] == 'HIGH' else '🟡' if issue['severity'] == 'MEDIUM' else '🟢'
        print(f"\n{icon} Line {issue['line']}: {issue['severity']}")
        print(f"   Issue: {issue['issue']}")
        print(f"   Code: {issue['text']}")
else:
    print("  ✓ No issues detected in PowerScript analysis")

# Analyze Batch
print("\n📋 Batch File Analysis:")
print("-" * 70)
batch_issues = analyze_batch('INSTALL-OPENCLAW.bat')

if batch_issues:
    for issue in batch_issues:
        icon = '🔴' if issue['severity'] == 'HIGH' else '🟡'
        print(f"\n{icon} {issue['severity']}: {issue['issue']}")
else:
    print("  ✓ Batch file looks good")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

high = sum(1 for i in ps_issues + batch_issues if i['severity'] == 'HIGH')
medium = sum(1 for i in ps_issues + batch_issues if i['severity'] == 'MEDIUM')
low = sum(1 for i in ps_issues + batch_issues if i['severity'] == 'LOW')

print(f"\nTotal Issues Found:")
print(f"  🔴 Critical/High: {high}")
print(f"  🟡 Medium: {medium}")
print(f"  🟢 Low/Info: {low}")

if high > 0:
    print("\n⚠️  CRITICAL BUGS MUST BE FIXED before sharing!")
else:
    print("\n✅ No critical bugs. Script should work with caveats.")
