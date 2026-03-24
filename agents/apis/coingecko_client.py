#!/usr/bin/env python3
"""
CoinGecko API Client
Backup price data for token screening
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime

class CoinGeckoClient:
    """
    CoinGecko API Client
    
    Features:
    - Get token prices
    - Market cap data
    - Volume information
    - Cross-reference with DexScreener
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key  # Optional, free tier works without
        self.rate_limit_remaining = 30  # Free tier = 10-30 calls/min
        
    def get_token_price(self, 
                       token_id: str,
                       vs_currency: str = "usd") -> Dict:
        """
        Get current price for a token
        
        Args:
            token_id: CoinGecko ID (e.g., "solana", "bonk")
            vs_currency: Quote currency
        
        Returns:
            Price data
        """
        url = f"{self.base_url}/simple/price"
        
        params = {
            "ids": token_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if token_id in data:
                return {
                    "success": True,
                    "price": data[token_id].get(vs_currency),
                    "market_cap": data[token_id].get(f"{vs_currency}_market_cap"),
                    "volume_24h": data[token_id].get(f"{vs_currency}_24h_vol"),
                    "change_24h": data[token_id].get(f"{vs_currency}_24h_change")
                }
            else:
                return {"success": False, "error": "Token not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_token(self, query: str) -> List[Dict]:
        """
        Search for token by name or symbol
        
        Args:
            query: Token name or symbol
        
        Returns:
            List of matching tokens
        """
        url = f"{self.base_url}/search"
        
        params = {"query": query}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("coins", [])
        except Exception as e:
            return []
    
    def get_market_data(self, 
                       token_addresses: List[str],
                       platform: str = "solana") -> Dict:
        """
        Get market data for multiple tokens by contract address
        
        Args:
            token_addresses: List of token contract addresses
            platform: Platform (solana, ethereum, etc.)
        
        Returns:
            Market data for all tokens
        """
        url = f"{self.base_url}/coins/markets"
        
        params = {
            "vs_currency": "usd",
            "ids": ",".join(token_addresses[:250]),  # Max 250
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_trending(self) -> List[Dict]:
        """
        Get trending tokens (last 24h)
        """
        url = f"{self.base_url}/search/trending"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("coins", [])
        except Exception as e:
            return []
    
    def check_rate_limit(self) -> bool:
        """
        Check if we can make more API calls
        """
        # Simple check - reset every minute
        # Full implementation would track actual rate limits
        return self.rate_limit_remaining > 0

class CoinGeckoScreening:
    """
    Use CoinGecko for enhanced token screening
    Cross-reference with DexScreener data
    """
    
    def __init__(self):
        self.client = CoinGeckoClient()
    
    def cross_validate_token(self, 
                             token_name: str,
                             token_address: str,
                             dex_price: float) -> Dict:
        """
        Cross-validate token data between DexScreener and CoinGecko
        
        Args:
            token_name: Token name
            token_address: Contract address
            dex_price: Price from DexScreener
        
        Returns:
            Validation result with discrepancies
        """
        # Search for token
        cg_tokens = self.client.search_token(token_name)
        
        if not cg_tokens:
            return {
                "validated": False,
                "reason": "Token not found on CoinGecko",
                "risk_score": 1.0  # High risk
            }
        
        # Get price data
        cg_id = cg_tokens[0].get("id")
        cg_data = self.client.get_token_price(cg_id)
        
        if not cg_data.get("success"):
            return {
                "validated": False,
                "reason": "Could not get CoinGecko price",
                "risk_score": 0.5
            }
        
        # Compare prices
        cg_price = cg_data.get("price", 0)
        price_diff = abs(cg_price - dex_price) / max(dex_price, 0.0001)
        
        validation = {
            "validated": True,
            "dex_price": dex_price,
            "cg_price": cg_price,
            "price_diff_pct": price_diff * 100,
            "market_cap": cg_data.get("market_cap"),
            "volume_24h": cg_data.get("volume_24h"),
            "risk_score": 0.0
        }
        
        # Price discrepancy check
        if price_diff > 0.5:  # 50% difference
            validation["risk_score"] += 0.3
            validation["warning"] = "Large price discrepancy between sources"
        
        # Volume check
        if cg_data.get("volume_24h", 0) < 1000:  # Less than $1K volume
            validation["risk_score"] += 0.4
            validation["warning"] = "Very low volume on CoinGecko"
        
        # Market cap check
        if cg_data.get("market_cap", 0) == 0:
            validation["risk_score"] += 0.2
        
        return validation

# Token ID mappings (popular Solana tokens)
SOLANA_TOKEN_IDS = {
    "SOL": "solana",
    "BONK": "bonk",
    "JUP": "jupiter-exchange-solana",
    "JTO": "jito",
    "WIF": "dogwifcoin",
    "BOME": "book-of-meme",
    "W": "wormhole",
    "SLERF": "slerf",
    "POPCAT": "popcat",
    "MYRO": "myro",
    "SILLY": "silly-dragon"
}

if __name__ == "__main__":
    print("=== CoinGecko API Client ===")
    print("\nFeatures:")
    print("- Get token prices and market data")
    print("- Cross-validate with DexScreener")
    print("- Trending tokens discovery")
    print("- Rate limit management")
    print("\nUsage:")
    print("  client = CoinGeckoClient()")
    print("  data = client.get_token_price('solana')")
    print("  validation = CoinGeckoScreening().cross_validate_token('BONK', address, price)")
    print("\n✅ CoinGecko client ready for cross-reference")
