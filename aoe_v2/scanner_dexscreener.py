#!/usr/bin/env python3
"""
AOE v2.0 - DexScreener Scanner (Enhanced Version)
Uses multiple search strategies to find microcap tokens.
"""

import requests
from typing import List, Dict, Optional, Any
from scanner_base import ScannerBase, Token


class DexScreenerScanner(ScannerBase):
    """
    Enhanced DexScreener scanner with multiple search strategies.
    API: https://api.dexscreener.com/latest/dex/search
    """
    
    BASE_URL = "https://api.dexscreener.com"
    
    def __init__(self, timeout: int = 15):
        super().__init__("dexscreener", timeout)
        # Multiple search queries to find different tokens
        self.search_queries = [
            'solana',
            'meme',
            'ai solana',
            'defi solana',
            'gaming solana',
            'new solana'
        ]
    
    def fetch(self) -> List[Token]:
        """
        Fetch Solana tokens from DexScreener using multiple searches.
        """
        all_tokens = []
        seen_addresses = set()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        for query in self.search_queries:
            try:
                url = f"{self.BASE_URL}/latest/dex/search"
                params = {'q': query}
                
                self.logger.info(f"Fetching DexScreener search: '{query}'")
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                tokens = self._parse_response(data, seen_addresses)
                all_tokens.extend(tokens)
                self.logger.info(f"  Found {len(tokens)} new tokens from '{query}'")
                
            except Exception as e:
                self.logger.warning(f"DexScreener search '{query}' failed: {e}")
                continue
        
        self.logger.info(f"Fetched {len(all_tokens)} unique tokens from DexScreener")
        return all_tokens
    
    def _parse_response(self, data: Dict, seen_addresses: set) -> List[Token]:
        """Parse DexScreener search response, filtering duplicates."""
        tokens = []
        
        if not isinstance(data, dict):
            return []
        
        pairs = data.get('pairs', [])
        if not pairs:
            return []
        
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            
            # Get base token
            base = pair.get('baseToken', {})
            address = base.get('address', '')
            
            if not address or address in seen_addresses:
                continue
            
            # Only include Solana tokens
            chain_id = pair.get('chainId', '').lower()
            if chain_id != 'solana':
                continue
            
            seen_addresses.add(address)
            
            # Extract market data
            mc = self.safe_float(pair.get('marketCap'))
            if mc == 0:
                mc = self.safe_float(pair.get('fdv'))
            
            volume = pair.get('volume', {})
            liquidity = pair.get('liquidity', {})
            price_change = pair.get('priceChange', {})
            txns = pair.get('txns', {})
            
            txns_24h = txns.get('h24', {})
            if isinstance(txns_24h, dict):
                buys_24h = txns_24h.get('buys', 0)
                sells_24h = txns_24h.get('sells', 0)
            else:
                buys_24h = sells_24h = 0
            
            token = Token(
                address=address,
                symbol=self.normalize_symbol(base.get('symbol', '???')),
                name=base.get('name', 'Unknown')[:50],
                chain_id=chain_id,
                price=self.safe_float(pair.get('priceUsd')),
                market_cap=mc,
                fdv=mc,
                liquidity=self.safe_float(liquidity.get('usd')),
                volume_24h=self.safe_float(volume.get('h24')),
                volume_1h=self.safe_float(volume.get('h1')),
                volume_5m=self.safe_float(volume.get('m5')),
                price_change_1h=self.safe_float(price_change.get('h1')),
                price_change_24h=self.safe_float(price_change.get('h24')),
                price_change_5m=self.safe_float(price_change.get('m5')),
                txns_24h=buys_24h + sells_24h,
                buys_24h=buys_24h,
                sells_24h=sells_24h,
                dex_id=pair.get('dexId', ''),
                pair_address=pair.get('pairAddress', ''),
                source='dexscreener',
                sources=['dexscreener']
            )
            tokens.append(token)
        
        return tokens


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')
    
    print("🧪 Testing DexScreener Scanner...")
    scanner = DexScreenerScanner()
    tokens = scanner.fetch()
    
    print(f"\n📊 Found {len(tokens)} tokens")
    
    if tokens:
        print("\nTop 10 by volume:")
        top = sorted(tokens, key=lambda t: t.volume_24h, reverse=True)[:10]
        for t in top:
            mc_str = f"${t.market_cap:,.0f}" if t.market_cap > 0 else "N/A"
            print(f"  {t.symbol}: {mc_str} MC, ${t.volume_24h:,.0f} vol")
        
        mcs = [t.market_cap for t in tokens if t.market_cap > 0]
        if mcs:
            print(f"\nMC range: ${min(mcs):,.0f} - ${max(mcs):,.0f}")
            print(f"Tokens with MC > 0: {len(mcs)}/{len(tokens)}")
