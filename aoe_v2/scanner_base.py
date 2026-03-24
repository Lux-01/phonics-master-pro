"""
AOE v2.0 - Base Scanner Class
Abstract base for all token scanners.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import time


@dataclass
class Token:
    """Unified token data structure across all scanners."""
    # Identity
    address: str
    symbol: str
    name: str
    chain_id: str = "solana"
    
    # Market Data
    price: float = 0.0
    market_cap: float = 0.0
    fdv: float = 0.0
    liquidity: float = 0.0
    volume_24h: float = 0.0
    volume_1h: float = 0.0
    volume_5m: float = 0.0
    price_change_1h: float = 0.0
    price_change_24h: float = 0.0
    price_change_5m: float = 0.0
    price_change_30m: float = 0.0
    
    # Transaction Data
    txns_24h: int = 0
    txns_1h: int = 0
    txns_5m: int = 0
    buys_24h: int = 0
    sells_24h: int = 0
    
    # Metadata
    holders: int = 0
    creation_time: Optional[datetime] = None
    dex_id: str = ""
    pair_address: str = ""
    
    # Scoring
    opportunity_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None
    
    # Source tracking
    source: str = ""
    sources: List[str] = None  # All sources that found this token
    discovered_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = [self.source] if self.source else []
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary for serialization."""
        result = {
            'address': self.address,
            'symbol': self.symbol,
            'name': self.name,
            'chain_id': self.chain_id,
            'price': self.price,
            'market_cap': self.market_cap,
            'fdv': self.fdv,
            'liquidity': self.liquidity,
            'volume_24h': self.volume_24h,
            'volume_1h': self.volume_1h,
            'volume_5m': self.volume_5m,
            'price_change_1h': self.price_change_1h,
            'price_change_24h': self.price_change_24h,
            'price_change_5m': self.price_change_5m,
            'price_change_30m': self.price_change_30m,
            'txns_24h': self.txns_24h,
            'txns_1h': self.txns_1h,
            'txns_5m': self.txns_5m,
            'buys_24h': self.buys_24h,
            'sells_24h': self.sells_24h,
            'holders': self.holders,
            'dex_id': self.dex_id,
            'pair_address': self.pair_address,
            'source': self.source,
            'sources': self.sources,
            'opportunity_score': self.opportunity_score,
        }
        if self.creation_time:
            result['creation_time'] = self.creation_time.isoformat()
        if self.discovered_at:
            result['discovered_at'] = self.discovered_at.isoformat()
        return result
    
    @property
    def vol_mc_ratio(self) -> float:
        """Volume to market cap ratio."""
        return self.volume_24h / self.market_cap if self.market_cap > 0 else 0
    
    @property
    def liq_mc_ratio(self) -> float:
        """Liquidity to market cap ratio."""
        return self.liquidity / self.market_cap if self.market_cap > 0 else 0
    
    @property
    def buy_ratio(self) -> float:
        """Buy to total transaction ratio."""
        total = self.buys_24h + self.sells_24h
        return self.buys_24h / total if total > 0 else 0.5


class ScannerBase(ABC):
    """Abstract base class for all token scanners."""
    
    def __init__(self, name: str, timeout: int = 15):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"aoe.scanner.{name}")
        self._last_fetch_time: Optional[datetime] = None
        self._cache_duration = 300  # 5 minutes
    
    @abstractmethod
    def fetch(self) -> List[Token]:
        """
        Fetch tokens from this source.
        
        Returns:
            List of Token objects found by this scanner
        """
        pass
    
    def fetch_with_retry(self, max_retries: int = 3) -> List[Token]:
        """
        Fetch with exponential backoff retry.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of Token objects
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching from {self.name} (attempt {attempt + 1})")
                start_time = time.time()
                tokens = self.fetch()
                elapsed = time.time() - start_time
                self._last_fetch_time = datetime.now()
                self.logger.info(f"Fetched {len(tokens)} tokens from {self.name} in {elapsed:.1f}s")
                return tokens
            except Exception as e:
                self.logger.warning(f"Failed attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All {max_retries} attempts failed for {self.name}")
                    return []
        return []
    
    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if self._last_fetch_time is None:
            return False
        elapsed = (datetime.now() - self._last_fetch_time).total_seconds()
        return elapsed < self._cache_duration
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize token symbol."""
        if not symbol:
            return "???"
        # Remove special characters, keep alphanumeric
        return ''.join(c for c in symbol if c.isalnum()).upper()[:10]
    
    def safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    
    def safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int."""
        if value is None:
            return default
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default
