#!/usr/bin/env python3
"""
Vulnerability Scanner - Automated security testing
Part of bug-bounty-hunter skill

Usage:
    python3 vuln_scan.py --target example.com --output scan_results.json
    python3 vuln_scan.py --urls targets/urls.txt --check xss
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class VulnScanner:
    def __init__(self, target=None, urls_file=None):
        self.target = target
        self.urls_file = urls_file
        self.findings = []
        self.urls = []
        
    def load_urls(self):
        """Load URLs from file or generate from target"""
        if self.urls_file:
            with open(self.urls_file, 'r') as f:
                self.urls = [line.strip() for line in f if line.strip()]
        elif self.target:
            # Generate common URLs for target
            self.urls = [
                f"https://{self.target}/",
                f"https://{self.target}/login",
                f"https://{self.target}/admin",
                f"https://{self.target}/api/",
                f"https://www.{self.target}/",
            ]
        else:
            print("Error: No target or URLs file provided")
            sys.exit(1)
            
    def check_xss_candidates(self):
        """Identify URLs with parameters that could be XSS candidates"""
        candidates = []
        xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "'\"><script>alert(1)</script>",
        ]
        
        for url in self.urls:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if params:
                for param in params:
                    candidates.append({
                        'url': url,
                        'parameter': param,
                        'type': 'xss_candidate',
                        'payloads': xss_payloads
                    })
                    
        return candidates
    
    def check_idor_patterns(self):
        """Identify potential IDOR patterns in URLs"""
        idor_patterns = []
        patterns = [
            r'/user/\d+',
            r'/account/\d+',
            r'/order/\d+',
            r'/invoice/\d+',
            r'/profile/\d+',
            r'/api/v\d+/\w+/\d+',
        ]
        
        for url in self.urls:
            for pattern in patterns:
                if re.search(pattern, url):
                    idor_patterns.append({
                        'url': url,
                        'pattern': pattern,
                        'type': 'idor_candidate'
                    })
                    
        return idor_patterns
    
    def check_interesting_endpoints(self):
        """Identify interesting endpoints"""
        interesting = []
        keywords = [
            'admin', 'api', 'config', 'backup', 'debug', 'test',
            'dev', 'staging', 'internal', 'private', 'secret',
            'upload', 'download', 'export', 'import', 'graphql',
            'swagger', 'docs', 'api-docs', 'ws', 'websocket'
        ]
        
        for url in self.urls:
            for keyword in keywords:
                if keyword in url.lower():
                    interesting.append({
                        'url': url,
                        'keyword': keyword,
                        'type': 'interesting_endpoint'
                    })
                    
        return interesting
    
    def check_ssrf_candidates(self):
        """Identify potential SSRF entry points"""
        ssrf_params = ['url', 'path', 'redirect', 'next', 'return', 
                       'callback', 'proxy', 'host', 'ip', 'domain']
        candidates = []
        
        for url in self.urls:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            for param in params:
                if param.lower() in ssrf_params:
                    candidates.append({
                        'url': url,
                        'parameter': param,
                        'type': 'ssrf_candidate'
                    })
                    
        return candidates
    
    def scan(self, check_type='all'):
        """Run vulnerability scans"""
        print(f"[*] Starting scan of {len(self.urls)} URLs")
        print(f"[*] Check type: {check_type}")
        print()
        
        if check_type in ['all', 'xss']:
            print("[*] Checking for XSS candidates...")
            xss = self.check_xss_candidates()
            self.findings.extend(xss)
            print(f"    Found {len(xss)} XSS candidates")
            
        if check_type in ['all', 'idor']:
            print("[*] Checking for IDOR patterns...")
            idor = self.check_idor_patterns()
            self.findings.extend(idor)
            print(f"    Found {len(idor)} IDOR candidates")
            
        if check_type in ['all', 'interesting']:
            print("[*] Checking for interesting endpoints...")
            interesting = self.check_interesting_endpoints()
            self.findings.extend(interesting)
            print(f"    Found {len(interesting)} interesting endpoints")
            
        if check_type in ['all', 'ssrf']:
            print("[*] Checking for SSRF candidates...")
            ssrf = self.check_ssrf_candidates()
            self.findings.extend(ssrf)
            print(f"    Found {len(ssrf)} SSRF candidates")
            
        print()
        print(f"[*] Total findings: {len(self.findings)}")
        
    def generate_report(self, output_file):
        """Generate JSON report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'target': self.target,
            'urls_scanned': len(self.urls),
            'total_findings': len(self.findings),
            'findings': self.findings
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"[*] Report saved to: {output_file}")
        
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*50)
        print("SCAN SUMMARY")
        print("="*50)
        
        by_type = {}
        for finding in self.findings:
            ftype = finding.get('type', 'unknown')
            by_type[ftype] = by_type.get(ftype, 0) + 1
            
        for ftype, count in sorted(by_type.items()):
            print(f"  {ftype}: {count}")
            
        print("\n[*] Next steps:")
        print("  1. Review findings manually")
        print("  2. Test XSS candidates with Burp Suite")
        print("  3. Test IDOR patterns by changing IDs")
        print("  4. Investigate interesting endpoints")
        print("  5. Test SSRF candidates with internal URLs")

def main():
    parser = argparse.ArgumentParser(description='Bug Bounty Vulnerability Scanner')
    parser.add_argument('--target', '-t', help='Target domain (e.g., example.com)')
    parser.add_argument('--urls', '-u', help='File containing URLs to scan')
    parser.add_argument('--check', '-c', default='all', 
                       choices=['all', 'xss', 'idor', 'ssrf', 'interesting'],
                       help='Type of check to run')
    parser.add_argument('--output', '-o', default='scan_results.json',
                       help='Output file for results')
    
    args = parser.parse_args()
    
    if not args.target and not args.urls:
        parser.print_help()
        sys.exit(1)
        
    scanner = VulnScanner(target=args.target, urls_file=args.urls)
    scanner.load_urls()
    scanner.scan(check_type=args.check)
    scanner.generate_report(args.output)
    scanner.print_summary()

if __name__ == '__main__':
    main()
