"""
AOE v2.0 - Birdeye Scanner
Birdeye API integration for token discovery and price history.
"""

import requests
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from scanner_base import ScannerBase, Token


class BirdeyeScanner(ScannerBase):
    """
    Birdeye scanner for Solana token data.
    
    Birdeye provides:
    - Real-time prices and market data
    - Token lists sorted by volume
    - Historical price data for analysis
    
    API: https://public-api.birdeye.so/
    Rate Limit: 100 req/min (free tier)
    """
    
    BASE_URL = "https://public-api.birdeye.so"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 15):
        super().__init__("birdeye", timeout)
        self.api_key = api_key or os.getenv('BIRDEYE_API_KEY')
        if not self.api_key:
            self.logger.warning("Birdeye API key not set - some features may fail")
        
        self.headers = {
            'x-api-key': self.api_key,
            'accept': 'application/json'
        }
    
    def fetch(self) -> List[Token]:
        """
        Fetch tokens from Birdeye tokenlist endpoint.
        
        Returns:
            List of Token objects sorted by volume
        """
        return self.fetch_tokenlist(limit=50)  # API max is 50
    
    def fetch_tokenlist(self, limit: int = 50, sort_by: str = "v24hUSD") -> List[Token]:
        """
        Fetch token list from Birdeye with retry logic.
        
        Args:
            limit: Max tokens to fetch (reduced to 50 to avoid rate limits)
            sort_by: Sort field (v24hUSD, mc, holders, etc.)
            
        Returns:
            List of Token objects
        """
        if not self.api_key:
            self.logger.error("Cannot fetch without API key")
            return []
        
        url = f"{self.BASE_URL}/defi/tokenlist"
        params = {
            'sort_by': sort_by,
            'sort_type': 'desc',
            'offset': 0,
            'limit': limit
        }
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching Birdeye tokenlist (limit={limit}, attempt {attempt + 1})")
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=self.timeout
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limited, waiting {wait_time}s...")
                    import time
                    time.sleep(wait_time)
                    continue
                
                # Handle other errors
                if response.status_code != 200:
                    self.logger.error(f"Birdeye API error {response.status_code}: {response.text[:200]}")
                    if attempt < max_retries - 1:
                        continue
                    return []
                
                data = response.json()
                if data.get('success') and data.get('data'):
                    tokens = data['data'].get('tokens', [])
                    parsed = self._parse_tokens(tokens)
                    self.logger.info(f"Parsed {len(parsed)} tokens from Birdeye")
                    return parsed
                else:
                    self.logger.warning(f"Birdeye returned success=false: {data}")
                    return []
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    return []
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return []
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return []
        
        return []
    
    def _parse_tokens(self, raw_tokens: List[Dict]) -> List[Token]:
        """Parse Birdeye token data into Token objects."""
        tokens = []
        
        for raw in raw_tokens:
            if not isinstance(raw, dict):
                continue
            
            address = raw.get('address', '')
            if not address:
                continue
            
            # Parse market data
            mc = self.safe_float(raw.get('mc') or raw.get('marketcap'))
            v24h = self.safe_float(raw.get('v24hUSD') or raw.get('v24h'))
            
            # Extract price changes if available
            price_change_24h = 0.0
            if 'priceChange24h' in raw:
                price_change_24h = self.safe_float(raw['priceChange24h'])
            elif 'price_change_24h' in raw:
                price_change_24h = self.safe_float(raw['price_change_24h'])
            
            token = Token(
                address=address,
                symbol=self.normalize_symbol(raw.get('symbol', '???')),
                name=raw.get('name', 'Unknown'),
                chain_id='solana',
                price=self.safe_float(raw.get('price')),
                market_cap=mc,
                fdv=mc,  # Birdeye uses MC = FDV for most tokens
                volume_24h=v24h,
                holders=self.safe_int(raw.get('holder') or raw.get('holders')),
                price_change_24h=price_change_24h,
                source='birdeye',
                sources=['birdeye']
            )
            tokens.append(token)
        
        return tokens
    
    def fetch_token_details(self, address: str) -> Optional[Dict]:
        """
        Fetch detailed token data via Birdeye.
        
        Args:
            address: Token contract address
            
        Returns:
            Token details dictionary or None
        """
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/defi/token_infor"
        params = {'address': address}
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('data', {})
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to fetch details for {address}: {e}")
            return None
    
    def fetch_price_history(self, address: str, time_from: int, time_to: int) -> Optional[List[Dict]]:
        """
        Fetch OHLCV price history for a token.
        
        Args:
            address: Token contract address
            time_from: Start timestamp
            time_to: End timestamp
            
        Returns:
            List of OHLCV data points
        """
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/defi/history_price"
        params = {
            'address': address,
            'address_type': 'token',
            'type': '1H',  # 1 hour candles
            'time_from': time_from,
            'time_to': time_to
        }
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('data', {}).get('items', [])
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to fetch history for {address}: {e}")
            return None
    
    def calculate_volume_spike(self, token: Token, hours_back: int = 24) -> float:
        """
        Calculate volume spike ratio vs historical average.
        
        Args:
            token: Token to analyze
            hours_back: Hours of history to compare
            
        Returns:
            Volume spike multiplier (e.g., 3.0 = 3x average)
        """
        if not self.api_key or not token.discovered_at:
            return 1.0
        
        time_to = int(token.discovered_at.timestamp())
        time_from = time_to - (hours_back * 3600)
        
        history = self.fetch_price_history(token.address, time_from, time_to)
        
        if history and len(history) > 0:
            avg_volume = sum(h.get('volume', 0) for h in history) / len(history)
            if avg_volume > 0:
                return token.volume_24h / (avg_volume * 24)  # Normalize to 24h
        
        return 1.0
    
    def fetch_new_tokens(self, hours_old: int = 24) -> List[Token]:
        """
        Fetch recently created tokens.
        
        Note: Birdeye doesn't provide creation time, so we filter
        by low holder count + low volume (typical of new tokens).
        
        Args:
            hours_old: Approximate age in hours to filter
            
        Returns:
            List of potentially new tokens
        """
        all_tokens = self.fetch_tokenlist(limit=200)
        
        # Heuristic: new tokens have low holders and price near 0
        new_tokens = []
        for token in all_tokens:
            is_new = (
                token.holders < 100 or  # Very few holders
                token.volume_24h < 1000  # Very low volume
            )
            if is_new and token.market_cap > 10000:  # Not completely dead
                new_tokens.append(token)
        
        return new_tokens


# Convenience function
def scan_birdeye(api_key: Optional[str] = None) -> List[Token]:
    """Standalone function to scan Birdeye."""
    scanner = BirdeyeScanner(api_key=api_key)
    return scanner.fetch_with_retry()


if __name__ == "__main__":
    # Test the scanner
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Birdeye Scanner v2.0...")
    print("=" * 60)
    
    scanner = BirdeyeScanner()
    
    if not scanner.api_key:
        print("❌ No API key found. Set BIRDEYE_API_KEY environment variable.")
    else:
        tokens = scanner.fetch_with_retry()
        print(f"\n📊 Found {len(tokens)} tokens")
        
        if tokens:
            print("\nTop 10 by volume:")
            top = sorted(tokens, key=lambda t: t.volume_24h, reverse=True)[:10]
            for t in top:
                print(f"  {t.symbol}: ${t.market_cap:,.0f} MC, {t.holders} holders")
