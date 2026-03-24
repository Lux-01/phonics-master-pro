#!/usr/bin/env python3
"""
Secret Scanner - Detect and protect sensitive information.
"""

import re
import logging
from typing import List, Dict, Optional


class SecretScanner:
    """
    Scan for secrets and sensitive data in content.
    """
    
    # Patterns to detect
    SECRET_PATTERNS = {
        "api_key": {
            "pattern": r'[a-zA-Z_][a-zA-Z0-9_]*_api_key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}',
            "description": "API key"
        },
        "secret_key": {
            "pattern": r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{32,}',
            "description": "Secret key"
        },
        "password": {
            "pattern": r'password\s*[:=]\s*["\'][^"\']{8,}',
            "description": "Hardcoded password"
        },
        "private_key": {
            "pattern": r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
            "description": "Private key"
        },
        "github_token": {
            "pattern": r'ghp_[a-zA-Z0-9]{36}',
            "description": "GitHub personal access token"
        },
        "aws_key": {
            "pattern": r'AKIA[0-9A-Z]{16}',
            "description": "AWS access key ID"
        },
        "slack_token": {
            "pattern": r'xox[baprs]-[a-zA-Z0-9]+',
            "description": "Slack token"
        },
        "jwt_token": {
            "pattern": r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            "description": "JWT token"
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger("Omnibot.SecretScanner")
    
    def scan(self, content: str) -> List[Dict]:
        """
        Scan content for secrets.
        
        Args:
            content: Content to scan
            
        Returns:
            List of found secrets with details
        """
        findings = []
        
        for secret_type, config in self.SECRET_PATTERNS.items():
            matches = re.finditer(config["pattern"], content, re.IGNORECASE)
            
            for match in matches:
                # Check if it's likely a placeholder
                if self._is_placeholder(match.group()):
                    continue
                
                findings.append({
                    "type": secret_type,
                    "description": config["description"],
                    "match": self._redact(match.group()),
                    "position": match.start()
                })
        
        return findings
    
    def _is_placeholder(self, match: str) -> bool:
        """Check if match is likely a placeholder."""
        placeholders = ["YOUR_API_KEY", "INSERT_KEY_HERE", "PLACEHOLDER", "XXX", "TEMP"]
        return any(p in match.upper() for p in placeholders)
    
    def _redact(self, secret: str) -> str:
        """Redact a secret for display."""
        if len(secret) <= 8:
            return "[REDACTED]"
        return secret[:4] + "..." + secret[-4:]
    
    def sanitize(self, content: str, redaction: str = "[REDACTED]") -> str:
        """
        Sanitize content by replacing secrets.
        
        Args:
            content: Original content
            redaction: Replacement string
            
        Returns:
            Sanitized content
        """
        sanitized = content
        
        for secret_type, config in self.SECRET_PATTERNS.items():
            sanitized = re.sub(config["pattern"], redaction, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_safe(self, content: str) -> bool:
        """
        Check if content is safe (no secrets).
        
        Args:
            content: Content to check
            
        Returns:
            True if safe
        """
        return len(self.scan(content)) == 0
    
    def get_scan_summary(self, content: str) -> str:
        """Get human-readable scan summary."""
        findings = self.scan(content)
        
        if not findings:
            return "✅ No secrets detected"
        
        summary = f"⚠️ Found {len(findings)} potential secret(s):\n"
        for finding in findings:
            summary += f"  - {finding['description']}: {finding['match']}\n"
        
        return summary