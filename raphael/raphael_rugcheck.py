#!/usr/bin/env python3
"""
RAPHAEL Token Safety Check - Pre-trade rugcheck
Usage: python3 raphael_rugcheck.py <TOKEN_SYMBOL> <MINT_ADDRESS>
"""

import sys
import json
import requests
from typing import Dict, Any

def check_token_safety(symbol: str, mint: str) -> Dict[str, Any]:
    """
    Perform token safety checks for RAPHAEL trading system
    Returns dict with safety score and flags
    """
    result = {
        "token": symbol,
        "mint": mint,
        "passed": False,
        "grade": "C",
        "checks": {}
    }
    
    try:
        # Check Birdeye for token data
        headers = {"X-API-KEY": "6335463fca7340f9a2c73eacd5a37f64"}
        
        # Get token overview
        overview_url = f"https://public-api.birdeye.so/defi/token_overview?address={mint}"
        overview_resp = requests.get(overview_url, headers=headers, timeout=10)
        
        if overview_resp.status_code != 200:
            result["checks"]["api_access"] = "FAILED - API error"
            return result
            
        data = overview_resp.json()
        
        if data.get("success") and data.get("data"):
            token_data = data["data"]
            
            # Check 1: Market Cap >$20M
            mcap = token_data.get("realMc", token_data.get("marketCap", 0))
            result["checks"]["market_cap"] = "PASS" if mcap > 20_000_000 else f"FAIL - ${mcap:,.0f}"
            
            # Check 2: Liquidity/TVL >$50K
            liquidity = token_data.get("liquidity", 0)
            result["checks"]["tvl"] = "PASS" if liquidity > 50_000 else f"FAIL - ${liquidity:,.0f}"
            
            # Check 3: Volume check
            volume_24h = token_data.get("v24hUSD", token_data.get("volume24h", 0))
            result["checks"]["volume_24h"] = f"${volume_24h:,.2f}"
            
            # Check 4: Price change (volatility)
            price_change_24h = token_data.get("priceChange24h", 0)
            result["checks"]["volatility_24h"] = f"{price_change_24h:.2f}%"
            
            # Check 5: Number of holders
            unique_wallet = token_data.get("uniqueWallet24h", 0)
            result["checks"]["holders_24h"] = f"{unique_wallet}"
            
            # Determine grade (simplified for demo)
            score = 0
            if mcap > 20_000_000: score += 2
            elif mcap > 10_000_000: score += 1
                
            if liquidity > 50_000: score += 1
            if abs(price_change_24h) > 1.5: score += 1
            if unique_wallet > 1000: score += 1
            
            if score >= 4:
                result["grade"] = "A+"
            elif score >= 3:
                result["grade"] = "A"
            elif score >= 2:
                result["grade"] = "B"
            else:
                result["grade"] = "C"
            
            # Check if mint authority is revoked (simplified)
            result["checks"]["mint_authority"] = "UNKNOWN - Verify on Solscan"
            
            # Check holder concentration
            result["checks"]["holder_concentration"] = "UNKNOWN - Verify on Solscan"
            
            # Overall pass for A+/A only
            result["passed"] = result["grade"] in ["A+", "A"]
            
        else:
            result["checks"]["data_available"] = "FAILED - No data from Birdeye"
            
    except Exception as e:
        result["checks"]["error"] = str(e)
    
    return result

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 raphael_rugcheck.py <TOKEN_SYMBOL> <MINT_ADDRESS>")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    mint = sys.argv[2]
    
    print(f"\n🔍 RAPHAEL RUGCHECK: {symbol}")
    print("=" * 50)
    
    result = check_token_safety(symbol, mint)
    
    print(f"Token: {result['token']}")
    print(f"Mint: {result['mint']}")
    print(f"Grade: {result['grade']}")
    print(f"Passed: {'✅ YES' if result['passed'] else '❌ NO'}")
    print("\nChecks:")
    for check, status in result["checks"].items():
        print(f"  • {check}: {status}")
    
    print("=" * 50)
    
    # Exit code for shell scripts
    sys.exit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()
