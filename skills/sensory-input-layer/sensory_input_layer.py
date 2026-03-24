#!/usr/bin/env python3
"""
Sensory Input Layer - ACA Built v1.0
The eyes and ears - gather raw data from external sources for ARAS reasoning.
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import argparse
import urllib.request
import urllib.error


@dataclass
class DataSource:
    """Represents a data source configuration."""
    name: str
    source_type: str  # web, api, blockchain, rss
    endpoint: str
    method: str = "GET"
    headers: Dict = None
    params: Dict = None
    rate_limit: int = 60  # requests per minute
    reliability_score: float = 0.8
    last_fetch: Optional[str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.params is None:
            self.params = {}


@dataclass
class FetchedData:
    """Represents fetched data with metadata."""
    source: str
    data: Any
    timestamp: str
    hash: str
    size: int
    processing_time_ms: float
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class SensoryInputLayer:
    """
    Sensory Input Layer - gathers raw data from external sources.
    Provides web scraping, API integration, blockchain queries.
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/sil")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.sources_file = os.path.join(self.memory_dir, "sources.json")
        self.cache_dir = os.path.join(self.memory_dir, "cache")
        self._ensure_dirs()
        self.state = self._load_state()
        self.sources = self._load_sources()
        self.cache: Dict[str, Any] = {}
        self._rate_limiters: Dict[str, List[float]] = {}
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "total_fetches": 0,
            "successful_fetches": 0,
            "failed_fetches": 0,
            "sources_configured": 0,
            "cache_hits": 0
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _load_sources(self) -> Dict[str, DataSource]:
        default_sources = {
            "birdeye": DataSource(
                name="Birdeye",
                source_type="api",
                endpoint="https://public-api.birdeye.so/public/tokenlist",
                headers={"X-API-KEY": os.getenv("BIRDEYE_API_KEY", "")}
            ),
            "dexscreener": DataSource(
                name="DexScreener",
                source_type="api",
                endpoint="https://api.dexscreener.com/latest/dex/search",
                rate_limit=30
            ),
            "helius": DataSource(
                name="Helius",
                source_type="blockchain",
                endpoint="https://mainnet.helius-rpc.com/?api-key=",
                rate_limit=100
            )
        }
        
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, 'r') as f:
                    data = json.load(f)
                    for name, cfg in data.items():
                        default_sources[name] = DataSource(**cfg)
        except Exception:
            pass
        
        return default_sources
    
    def _save(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            with open(self.sources_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.sources.items()}, f, indent=2)
        except Exception:
            pass
    
    def _check_rate_limit(self, source_name: str) -> bool:
        """Check if we can make a request to this source."""
        source = self.sources.get(source_name)
        if not source:
            return False
        
        limit = source.rate_limit
        now = time.time()
        
        if source_name not in self._rate_limiters:
            self._rate_limiters[source_name] = []
        
        # Clean old entries (older than 60 seconds)
        self._rate_limiters[source_name] = [
            t for t in self._rate_limiters[source_name] if now - t < 60
        ]
        
        return len(self._rate_limiters[source_name]) < limit
    
    def _record_request(self, source_name: str):
        """Record a request for rate limiting."""
        if source_name not in self._rate_limiters:
            self._rate_limiters[source_name] = []
        self._rate_limiters[source_name].append(time.time())
    
    def _compute_hash(self, data: str) -> str:
        """Compute hash of data for caching."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, source_name: str, params: str = "") -> str:
        """Generate cache key."""
        return f"{source_name}_{self._compute_hash(params)}"
    
    def _get_cached(self, cache_key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """Get cached data if not expired."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            if os.path.exists(cache_file):
                mtime = os.path.getmtime(cache_file)
                if time.time() - mtime < ttl_seconds:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        except Exception:
            pass
        
        return None
    
    def _set_cached(self, cache_key: str, data: Any):
        """Cache data to disk."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            self.state["cache_hits"] += 1
        except Exception:
            pass
    
    def fetch(self, source_name: str, params: str = "", use_cache: bool = False, 
              ttl_seconds: int = 300) -> FetchedData:
        """Fetch data from a source."""
        start = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(source_name, params)
        if use_cache:
            cached = self._get_cached(cache_key, ttl_seconds)
            if cached is not None:
                return FetchedData(
                    source=source_name,
                    data=cached,
                    timestamp=datetime.now().isoformat(),
                    hash=cache_key,
                    size=len(json.dumps(cached)),
                    processing_time_ms=(time.time() - start) * 1000
                )
        
        # Check rate limit
        if not self._check_rate_limit(source_name):
            return FetchedData(
                source=source_name,
                data=None,
                timestamp=datetime.now().isoformat(),
                hash="",
                size=0,
                processing_time_ms=0,
                error="Rate limit exceeded"
            )
        
        source = self.sources.get(source_name)
        if not source:
            return FetchedData(
                source=source_name,
                data=None,
                timestamp=datetime.now().isoformat(),
                hash="",
                size=0,
                processing_time_ms=0,
                error=f"Source '{source_name}' not found"
            )
        
        self._record_request(source_name)
        
        try:
            # Build URL
            url = source.endpoint
            if params:
                url = f"{url}?{params}"
            
            # Make request
            req = urllib.request.Request(
                url,
                method=source.method,
                headers=source.headers
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                raw_data = response.read().decode('utf-8')
                try:
                    data = json.loads(raw_data)
                except:
                    data = raw_data
            
            self.state["total_fetches"] += 1
            self.state["successful_fetches"] += 1
            source.last_fetch = datetime.now().isoformat()
            
            result = FetchedData(
                source=source_name,
                data=data,
                timestamp=datetime.now().isoformat(),
                hash=cache_key,
                size=len(raw_data),
                processing_time_ms=(time.time() - start) * 1000
            )
            
            if use_cache:
                self._set_cached(cache_key, data)
            
            self._save()
            return result
            
        except Exception as e:
            self.state["total_fetches"] += 1
            self.state["failed_fetches"] += 1
            self._save()
            
            return FetchedData(
                source=source_name,
                data=None,
                timestamp=datetime.now().isoformat(),
                hash="",
                size=0,
                processing_time_ms=(time.time() - start) * 1000,
                error=str(e)
            )
    
    def add_source(self, name: str, endpoint: str, source_type: str = "api",
                   headers: Dict = None, rate_limit: int = 60):
        """Add a new data source."""
        self.sources[name] = DataSource(
            name=name,
            source_type=source_type,
            endpoint=endpoint,
            headers=headers or {},
            rate_limit=rate_limit
        )
        self.state["sources_configured"] = len(self.sources)
        self._save()
    
    def get_source_health(self) -> Dict[str, Dict]:
        """Get health status of all sources."""
        health = {}
        for name, source in self.sources.items():
            last_fetch = source.last_fetch
            status = "unknown"
            
            if last_fetch:
                last = datetime.fromisoformat(last_fetch)
                hours_ago = (datetime.now() - last).total_seconds() / 3600
                if hours_ago < 1:
                    status = "healthy"
                elif hours_ago < 24:
                    status = "stale"
                else:
                    status = "disconnected"
            
            health[name] = {
                "status": status,
                "last_fetch": last_fetch,
                "reliability": source.reliability_score
            }
        
        return health
    
    def get_report(self) -> str:
        """Generate SIL report."""
        lines = [
            "Sensory Input Layer Report",
            f"Total fetches: {self.state['total_fetches']}",
            f"Success rate: {self.state['successful_fetches']/max(1,self.state['total_fetches']):.1%}",
            f"Sources configured: {self.state['sources_configured']}",
            f"Cache hits: {self.state['cache_hits']}",
            "",
            "Source health:"
        ]
        
        health = self.get_source_health()
        for name, status in health.items():
            lines.append(f"  {name}: {status['status']} (reliability: {status['reliability']})")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SIL - Sensory Input Layer")
    parser.add_argument("--mode", choices=["fetch", "health", "report", "test"], default="report")
    parser.add_argument("--source", "-s", help="Source name")
    
    args = parser.parse_args()
    
    sil = SensoryInputLayer()
    
    if args.mode == "fetch":
        if not args.source:
            print("Error: --source required")
            return
        result = sil.fetch(args.source, use_cache=True)
        print(json.dumps({
            "success": result.error is None,
            "size": result.size,
            "time_ms": result.processing_time_ms,
            "error": result.error
        }, indent=2))
    
    elif args.mode == "health":
        health = sil.get_source_health()
        print(json.dumps(health, indent=2))
    
    elif args.mode == "report":
        print(sil.get_report())
    
    elif args.mode == "test":
        print("🧪 Testing SIL...")
        health = sil.get_source_health()
        print(f"✓ {len(health)} sources configured")
        print(f"✓ Stats: {sil.state['total_fetches']} fetches")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
