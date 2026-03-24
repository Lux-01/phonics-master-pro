#!/usr/bin/env python3
"""
Proxy rotation with health checking
"""

import random
import asyncio
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Proxy:
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    fail_count: int = 0
    last_used: Optional[datetime] = None
    last_check: Optional[datetime] = None
    is_working: bool = True


class ProxyRotator:
    """
    Rotate through proxy list with health tracking.
    """
    
    def __init__(self, proxies: List[str], max_failures: int = 3, check_interval: int = 300):
        """
        Args:
            proxies: List of proxy URLs (http://host:port or http://user:pass@host:port)
            max_failures: Max failures before marking proxy dead
            check_interval: Seconds between health checks
        """
        self.proxies: List[Proxy] = []
        self.max_failures = max_failures
        self.check_interval = check_interval
        self._current_index = 0
        
        for proxy_url in proxies:
            self.proxies.append(self._parse_proxy(proxy_url))
    
    def _parse_proxy(self, url: str) -> Proxy:
        """Parse proxy URL into components."""
        # Simple parsing for user:pass@host:port format
        if "@" in url:
            auth_part, server_part = url.replace("http://", "").replace("https://", "").split("@")
            username, password = auth_part.split(":")
            return Proxy(url=url, username=username, password=password)
        return Proxy(url=url)
    
    def get_proxy(self, prefer_working: bool = True) -> str:
        """
        Get next proxy from rotation.
        
        Args:
            prefer_working: Skip proxies marked as not working
        
        Returns:
            Proxy URL string
        """
        if not self.proxies:
            raise ValueError("No proxies configured")
        
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self._current_index]
            self._current_index = (self._current_index + 1) % len(self.proxies)
            
            if not prefer_working or proxy.is_working:
                proxy.last_used = datetime.now()
                return proxy.url
            
            attempts += 1
        
        # All proxies marked as failed, reset and return first
        for p in self.proxies:
            p.is_working = True
            p.fail_count = 0
        
        return self.proxies[0].url
    
    def report_success(self, proxy_url: str):
        """Report successful use of proxy."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count = max(0, proxy.fail_count - 1)
                proxy.is_working = True
                break
    
    def report_failure(self, proxy_url: str):
        """Report failed use of proxy."""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count += 1
                if proxy.fail_count >= self.max_failures:
                    proxy.is_working = False
                break
    
    def get_stats(self) -> Dict:
        """Get proxy health statistics."""
        return {
            "total": len(self.proxies),
            "working": sum(1 for p in self.proxies if p.is_working),
            "failed": sum(1 for p in self.proxies if not p.is_working),
            "proxies": [
                {
                    "url": p.url.replace(p.password or "", "***") if p.password else p.url,
                    "working": p.is_working,
                    "fail_count": p.fail_count
                }
                for p in self.proxies
            ]
        }
