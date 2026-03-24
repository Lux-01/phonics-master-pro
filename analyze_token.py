#!/usr/bin/env python3
"""
Deep dive token analysis
"""

import json
import requests
import asyncio
from datetime import datetime
from pathlib import Path

# Token to analyze
TOKEN_ADDRESS = "AFd4NyGo5r6kqLRfarDecp96eh583B149X3GQJF5pump"
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"

class TokenAnalyzer:
    def __init__(self):
        self.token_address = TOKEN_ADDRESS
        
    def fetch_birdeye_data(self):
        """Get comprehensive Birdeye data"""
        try:
            # Price data
            url = f"https://public-api.birdeye.so/defi/price?address={self.token_address}"
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            response = requests.get(url, headers=headers, timeout=10)
            price_data = response.json()
            
            # Token metadata
            meta_url = f"https://public-api.birdeye.so/defi/token_meta?address={self.token_address}"
            meta_response = requests.get(meta_url, headers=headers, timeout=10)
            meta_data = meta_response.json()
            
            # Token creation info
            creation_url = f"https://public-api.birdeye.so/defi/history_price?address={self.token_address}&type=1D&time_from=1704067200&time_to=9999999999"
            creation_response = requests.get(creation_url, headers=headers, timeout=10)
            creation_data = creation_response.json()
            
            return {
                "price": price_data,
                "meta": meta_data,
                "history": creation_data
            }
        except Exception as e:
            print(f"Error fetching Birdeye: {e}")
            return None
    
    def analyze_dexscreener(self):
        """Get DexScreener data"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{self.token_address}"
            response = requests.get(url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error fetching DexScreener: {e}")
            return None
    
    def print_analysis(self):
        """Print comprehensive analysis"""
        print("=" * 70)
        print("🔍 DEEP DIVE TOKEN ANALYSIS")
        print("=" * 70)
        print(f"Token: {self.token_address}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Fetch all data
        birdeye = self.fetch_birdeye_data()
        dexscreen = self.analyze_dexscreener()
        
        # Birdeye Analysis
        if birdeye:
            print("\n📊 BIRDEYE DATA:")
            print("-" * 70)
            
            if birdeye.get("price") and birdeye["price"].get("data"):
                price = birdeye["price"]["data"]
                print(f"Price: ${price.get('value', 'N/A')}")
                print(f"Price Change 24h: {price.get('updateHumanTime', 'N/A')}")
            
            if birdeye.get("meta") and birdeye["meta"].get("data"):
                meta = birdeye["meta"]["data"]
                print(f"\nToken: {meta.get('name', 'Unknown')} (${meta.get('symbol', 'Unknown')})")
                print(f"Decimals: {meta.get('decimals', 'N/A')}")
                
        # DexScreener Analysis
        if dexscreen and dexscreen.get("pairs"):
            pairs = dexscreen["pairs"]
            print("\n📈 DEXSCREENER DATA:")
            print("-" * 70)
            
            for pair in pairs[:3]:  # Top 3 pairs
                print(f"\nPair: {pair.get('baseToken', {}).get('symbol', 'Unknown')}/{pair.get('quoteToken', {}).get('symbol', 'Unknown')}")
                print(f"DEX: {pair.get('dexId', 'Unknown')}")
                print(f"Price: ${pair.get('priceUsd', 'N/A')}")
                print(f"24h Volume: ${pair.get('volume', {}).get('h24', 'N/A')}")
                print(f"Liquidity: ${pair.get('liquidity', {}).get('usd', 'N/A')}")
                print(f"Market Cap: ${pair.get('marketCap', 'N/A')}")
                print(f"Price Change 24h: {pair.get('priceChange', {}).get('h24', 'N/A')}%")
                print(f"Boosted: {'Yes' if pair.get('boosted') else 'No'}")
                
                # Holder info if available
                if pair.get("txns"):
                    txns = pair["txns"]
                    print(f"Buys 24h: {txns.get('h24', {}).get('buys', 'N/A')}")
                    print(f"Sells 24h: {txns.get('h24', {}).get('sells', 'N/A')}")
        
        # Risk Assessment
        print("\n" + "=" * 70)
        print("⚠️  RISK ASSESSMENT:")
        print("-" * 70)
        
        risks = []
        
        if dexscreen and dexscreen.get("pairs"):
            pair = dexscreen["pairs"][0]
            
            # Check liquidity
            liq = pair.get("liquidity", {}).get("usd", 0)
            if isinstance(liq, str):
                liq = float(liq.replace(",", "")) if liq else 0
            if liq < 8000:
                risks.append(f"❌ Low liquidity: ${liq:,.0f} (min $8K)")
            elif liq < 20000:
                risks.append(f"⚠️ Medium liquidity: ${liq:,.0f}")
            else:
                risks.append(f"✅ Good liquidity: ${liq:,.0f}")
            
            # Check volume
            vol = pair.get("volume", {}).get("h24", 0)
            if isinstance(vol, str):
                vol = float(vol.replace(",", "")) if vol else 0
            if vol < 5000:
                risks.append(f"❌ Low volume: ${vol:,.0f} (min $5K)")
            else:
                risks.append(f"✅ Volume OK: ${vol:,.0f}")
            
            # Check market cap
            mcap = pair.get("marketCap", 0)
            if isinstance(mcap, str):
                mcap = float(mcap.replace(",", "")) if mcap else 0
            if mcap < 15000:
                risks.append(f"❌ Low market cap: ${mcap:,.0f}")
            elif mcap > 100000:
                risks.append(f"ℹ️ High market cap: ${mcap:,.0f} (might be less volatile)")
            else:
                risks.append(f"✅ Market cap OK: ${mcap:,.0f}")
            
            # Check price change
            change = pair.get("priceChange", {}).get("h24", 0)
            if isinstance(change, str):
                change = float(change) if change else 0
            if change > 100:
                risks.append(f"⚠️ Extreme pump: +{change:.1f}% (risky entry)")
            elif change < -50:
                risks.append(f"⚠️ Heavy dump: {change:.1f}% (potential knife catch)")
            else:
                risks.append(f"✅ Price change: {change:+.1f}%")
        
        for risk in risks:
            print(f"  {risk}")
        
        # Overall Grade
        print("\n" + "=" * 70)
        print("📊 OVERALL ASSESSMENT:")
        print("-" * 70)
        
        grade = self.calculate_grade(risks)
        print(f"Grade: {grade}")
        
        if "A" in grade:
            print("✅ Tradeable with proper risk management")
        elif "B" in grade:
            print("⚠️ Caution - higher risk")
        else:
            print("❌ Avoid - too risky")
        
        print("=" * 70)
    
    def calculate_grade(self, risks):
        """Calculate overall grade"""
        score = 100
        
        for risk in risks:
            if "❌" in risk:
                score -= 20
            elif "⚠️" in risk:
                score -= 10
        
        if score >= 85:
            return "A+"
        elif score >= 75:
            return "A"
        elif score >= 65:
            return "A-"
        elif score >= 55:
            return "B+"
        elif score >= 45:
            return "B"
        else:
            return "C"

if __name__ == "__main__":
    analyzer = TokenAnalyzer()
    analyzer.print_analysis()
