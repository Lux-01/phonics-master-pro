#!/usr/bin/env python3
"""
AOE v2.1 - PumpFun Scanner (Upgraded)
PumpFun tracking with exponential backoff retry.
"""

import requests
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from scanner_base import ScannerBase, Token


class PumpFunScanner(ScannerBase):
    """
    PumpFun scanner for Solana memecoin launches.
    Falls back gracefully if API is rate limited.
    """
    
    BASE_URL = "https://frontend-api.pump.fun"
    
    def __init__(self, timeout: int = 10):
        super().__init__("pumpfun", timeout)
    
    def fetch(self) -> List[Token]:
        """Fetch tokens from PumpFun with exponential backoff retry."""
        tokens = []
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                tokens = self._fetch_recent()
                if tokens:
                    break  # Success
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 or e.response.status_code == 530:
                    delay = min(base_delay * (2 ** attempt), 60)  # 2s, 4s, 8s, max 60s
                    self.logger.warning(f"PumpFun rate limited (attempt {attempt + 1}/{max_retries}), waiting {delay}s...")
                    time.sleep(delay)
                else:
                    self.logger.warning(f"PumpFun HTTP error: {e}")
                    break
            except Exception as e:
                self.logger.warning(f"PumpFun fetch error (attempt {attempt + 1}): {e}")
                break
        
        if not tokens:
            self.logger.warning("PumpFun: No tokens fetched after retries")
        
        return tokens
    
    def _fetch_recent(self, limit: int = 30) -> List[Token]:
        """Fetch recent tokens from PumpFun."""
        url = f"{self.BASE_URL}/coins"
        params = {
            'offset': 0,
            'limit': limit,
            'sort': 'created_timestamp',
            'order': 'DESC'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        
        # Handle rate limiting
        if response.status_code == 429 or response.status_code == 530:
            self.logger.warning("PumpFun rate limited - skipping this source")
            return []
        
        response.raise_for_status()
        data = response.json()
        
        tokens = []
        coins = data if isinstance(data, list) else data.get('coins', [])
        
        for coin in coins:
            token = self._parse_coin(coin)
            if token:
                tokens.append(token)
        
        return tokens
    
    def _parse_coin(self, coin: Dict) -> Optional[Token]:
        """Parse a single PumpFun coin."""
        if not isinstance(coin, dict):
            return None
        
        address = coin.get('mint') or coin.get('address') or coin.get('id', '')
        if not address:
            return None
        
        # Calculate market cap (PumpFun bonding curve math)
        sol_reserves = self.safe_float(coin.get('virtual_sol_reserves', 0)) / 1e9
        sol_price = 130  # Approx SOL price
        mc = sol_reserves * sol_price * 2
        
        symbol = self.normalize_symbol(coin.get('symbol', '???'))
        name = coin.get('name', 'Unknown')
        
        # Parse creation time
        created = None
        ts = coin.get('created_timestamp')
        if ts:
            try:
                ts = ts / 1000 if ts > 1000000000000 else ts  # ms to s
                created = datetime.fromtimestamp(ts)
            except:
                pass
        
        return Token(
            address=address,
            symbol=symbol,
            name=name,
            chain_id='solana',
            market_cap=mc,
            fdv=mc,
            volume_24h=self.safe_float(coin.get('volume_24h', 0)),
            txns_24h=self.safe_int(coin.get('trades_24h', 0)),
            creation_time=created,
            source='pumpfun',
            sources=['pumpfun']
        )


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing PumpFun Scanner v2.0...")
    scanner = PumpFunScanner()
    tokens = scanner.fetch_with_retry()
    
    print(f"\n📊 Found {len(tokens)} tokens")
    
    if tokens:
        print("\nTop 5 by market cap:")
        for t in sorted(tokens, key=lambda x: x.market_cap, reverse=True)[:5]:
            print(f"  {t.symbol}: ${t.market_cap:,.0f} MC")
