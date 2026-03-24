#!/usr/bin/env python3
"""
🔍 TOKEN MIGRATION CHECKER
Checks if pump.fun tokens have migrated to Raydium
"""

import requests
from typing import Dict, Optional

BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BIRDEYE_API = "https://public-api.birdeye.so"


class MigrationChecker:
    """Check if token has migrated from pump.fun to Raydium"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": BIRDEYE_API_KEY,
            "accept": "application/json"
        })
    
    def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get token info from Birdeye"""
        try:
            url = f"{BIRDEYE_API}/public/token_info"
            params = {"address": token_address}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Birdeye error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   Birdeye exception: {e}")
            return None
    
    def check_migration_status(self, token_address: str) -> Dict:
        """
        Check if token is migrated and tradeable
        
        Returns:
            {
                "is_migrated": bool,
                "has_raydium_liquidity": bool,
                "platform": str,  # "pump.fun", "raydium", "mixed", "unknown"
                "liquidity_usd": float,
                "recommendation": str
            }
        """
        info = self.get_token_info(token_address)
        
        if not info or 'data' not in info:
            return {
                "is_migrated": False,
                "has_raydium_liquidity": False,
                "platform": "unknown",
                "liquidity_usd": 0,
                "recommendation": "Cannot verify - skip"
            }
        
        data = info.get('data', {})
        
        # Check liquidity
        liquidity = data.get('liquidity', 0)
        
        # Check if has Raydium pools
        # Birdeye shows this in the data
        platforms = data.get('platforms', [])
        
        has_raydium = any('raydium' in str(p).lower() for p in platforms)
        is_pumpfun = 'pump' in str(data.get('name', '')).lower() or \
                     'pump' in str(data.get('symbol', '')).lower()
        
        # Determine platform
        if has_raydium and liquidity > 10000:
            platform = "raydium"
            is_migrated = True
            recommendation = "✅ Ready for auto-trading"
        elif is_pumpfun and liquidity < 50000:
            platform = "pump.fun"
            is_migrated = False
            recommendation = "⚠️ Not migrated - manual sell only"
        else:
            platform = "mixed"
            is_migrated = has_raydium
            recommendation = "⚠️ Check liquidity before trading"
        
        return {
            "is_migrated": is_migrated,
            "has_raydium_liquidity": has_raydium and liquidity > 10000,
            "platform": platform,
            "liquidity_usd": liquidity,
            "recommendation": recommendation
        }


def check_token(token_address: str) -> Dict:
    """Quick check function"""
    checker = MigrationChecker()
    return checker.check_migration_status(token_address)


if __name__ == "__main__":
    import sys
    
    # Test with the PUMP token
    test_token = "6TyK5BiBRJPdU4o1naDaNb54kR9nF4wk7nwu6iUFpump"
    
    print("🔍 Token Migration Checker")
    print("="*60)
    print(f"Token: {test_token}")
    print()
    
    result = check_token(test_token)
    
    print(f"Is Migrated: {result['is_migrated']}")
    print(f"Has Raydium Liquidity: {result['has_raydium_liquidity']}")
    print(f"Platform: {result['platform']}")
    print(f"Liquidity: ${result['liquidity_usd']:,.2f}")
    print(f"Recommendation: {result['recommendation']}")
