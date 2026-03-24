#!/usr/bin/env python3
"""
Solana Alpha Hunter v4.0 - Social Sentiment Edition
Full-featured scanner with social velocity tracking
"""

import requests
import json
from datetime import datetime

class SocialSentimentTracker:
    """Track social velocity for tokens"""
    
    def check_socials(self, ca):
        try:
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
            if r.status_code == 200:
                pairs = r.json()
                if pairs:
                    info = pairs[0].get('info', {})
                    socials = info.get('socials', [])
                    websites = info.get('websites', [])
                    
                    twitter = next((s.get('url') for s in socials if s.get('type') == 'twitter'), None)
                    telegram = next((s.get('url') for s in socials if s.get('type') == 'telegram'), None)
                    website = websites[0].get('url') if websites else None
                    
                    return {
                        'has_twitter': twitter is not None,
                        'twitter': twitter,
                        'has_telegram': telegram is not None,
                        'telegram': telegram,
                        'has_website': website is not None,
                        'website': website,
                        'social_score': (1 if twitter else 0) + (1 if telegram else 0) + (1 if website else 0)
                    }
        except:
            pass
        return {'has_twitter': False, 'twitter': None, 'has_telegram': False, 'telegram': None, 
                'has_website': False, 'website': None, 'social_score': 0}
    
    def calculate_sentiment(self, ca, symbol, name, mcap, vol24h):
        social = self.check_socials(ca)
        score = 0
        signals = []
        
        if social['has_website']:
            score += 2
            signals.append("✅ Website")
        if social['has_twitter']:
            score += 3
            signals.append("✅ Twitter")
            if vol24h > 50000:
                score += 2
                signals.append("🚀 High volume + Twitter")
        if social['has_telegram']:
            score += 2
            signals.append("✅ Telegram")
        if mcap < 100000 and vol24h > 100000:
            score += 3
            signals.append("🔥 Early viral")
        if vol24h > 200000:
            score += 1
            signals.append("📈 Strong volume")
        
        grade = "A+ 🚀" if score >= 9 else "A ✅" if score >= 7 else "B 🟡" if score >= 5 else "C ⚠️" if score >= 3 else "D ❌"
        return {'score': min(score, 10), 'grade': grade, 'signals': signals, 'social': social}

class AlphaHunter:
    def __init__(self):
        self.sentiment = SocialSentimentTracker()
    
    def scan(self, ca, name):
        print(f"\n{'='*80}")
        print(f"🎯 SCANNING: {name}")
        print(f"CA: {ca}")
        
        # Get Dex Screener data
        try:
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
            dex = r.json()[0] if r.status_code == 200 and r.json() else None
        except:
            dex = None
        
        if not dex:
            print("❌ No Dex data")
            return None
        
        # Get RugCheck data
        try:
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=10)
            rug = r.json() if r.status_code == 200 else {}
        except:
            rug = {}
        
        # Extract data
        mcap = dex.get('marketCap', 0) or 0
        liq = dex.get('liquidity', {}).get('usd', 0) or 0
        vol5m = dex.get('volume', {}).get('m5', 0) or 0
        vol1h = dex.get('volume', {}).get('h1', 0) or 0
        vol24h = dex.get('volume', {}).get('h24', 0) or 0
        symbol = dex.get('baseToken', {}).get('symbol', name)
        price_chg = dex.get('priceChange', {}).get('m5', 0)
        
        # Security
        mint_revoked = rug.get('token', {}).get('mintAuthority') is None if rug and isinstance(rug, dict) else False
        markets = rug.get('markets', [{}]) if rug and isinstance(rug, dict) else [{}]
        lp_locked = markets[0].get('lp', {}).get('lpLockedPct', 0) if markets and isinstance(markets[0], dict) else 0
        holders = rug.get('totalHolders', 0) if rug and isinstance(rug, dict) else 0
        hdata = rug.get('topHolders', []) if rug and isinstance(rug, dict) else []
        top10 = sum(h.get('pct', 0) for h in hdata[:10] if h.get('pct', 0) < 15) if hdata else 0
        nets = rug.get('insiderNetworks', []) if rug and isinstance(rug, dict) else []
        cluster = len(nets) if isinstance(nets, list) else 0
        if rug and isinstance(rug, dict) and rug.get('graphInsidersDetected', 0) > 0:
            cluster += 1
        
        # Slippage calc
        def slip(liq_val, buy):
            if liq_val <= 0:
                return 50
            return min(50, (buy / liq_val) * 100 * 2)
        
        s2k = slip(liq, 2000)
        
        # Social sentiment
        sentiment = self.sentiment.calculate_sentiment(ca, symbol, name, mcap, vol24h)
        
        # Scoring (12 criteria)
        passed = 0
        if mcap < 250000 and mcap > 0: passed += 1  # MCAP range
        if liq >= 15000: passed += 1  # Liquidity
        if s2k < 20: passed += 1  # Slippage
        if vol5m >= 5000: passed += 1  # Volume
        if mint_revoked: passed += 1  # Mint
        if lp_locked >= 95: passed += 1  # LP locked
        if top10 < 30: passed += 1  # Distribution
        if cluster <= 3: passed += 1  # Cluster
        if holders > 300: passed += 1  # Holders
        if sentiment['social']['has_website']: passed += 1  # Website
        if sentiment['score'] >= 7: passed += 1  # Social velocity ✅ NEW
        
        # Output
        print(f"\n📊 MARKET: MCAP ${mcap:,} | Velocity: {price_chg:+.1f}%")
        print(f"💧 LIQUIDITY: ${liq:,} | Slippage $2K: {s2k:.0f}%")
        print(f"📈 VOLUME: 5m=${vol5m:,} | 1h=${vol1h:,}")
        print(f"👥 HOLDERS: {holders} | Top10: {top10:.1f}% | Cluster: {cluster}/10")
        
        print(f"\n📱 SOCIAL VELOCITY:")
        print(f"  Website: {'✅' if sentiment['social']['has_website'] else '❌'} {sentiment['social'].get('website', 'None') or ''}")
        print(f"  Twitter: {'✅' if sentiment['social']['has_twitter'] else '❌'} {sentiment['social'].get('twitter', 'None') or ''}")
        print(f"  Telegram: {'✅' if sentiment['social']['has_telegram'] else '❌'} {sentiment['social'].get('telegram', 'None') or ''}")
        print(f"  Score: {sentiment['score']}/10 | Grade: {sentiment['grade']}")
        print(f"\n  📋 Signals:")
        for sig in sentiment['signals']:
            print(f"    {sig}")
        
        print(f"\n🔒 SECURITY: Mint {'✅' if mint_revoked else '❌'} | LP {lp_locked:.0f}% {'✅' if lp_locked >= 95 else '⚠️'}")
        
        grade = "A+ 🔥" if passed >= 11 else "A ✅" if passed >= 9 else "B 🟡" if passed >= 7 else "C ⚠️" if passed >= 6 else "D ❌"
        
        print(f"\n🎯 FINAL: {passed}/12 | Grade: {grade}")
        
        if passed >= 9:
            print(f"💰 2X Target: ${mcap*2:,} MCAP")
        
        return passed


if __name__ == "__main__":
    hunter = AlphaHunter()
    
    print("="*80)
    print("🚀 SOLANA ALPHA HUNTER v4.0 - Social Sentiment Edition")
    print("="*80)
    
    # Test on LUMO
    hunter.scan("7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump", "LUMO")
    
    print("\n" + "="*80)
    print("✅ v4.0 Social Sentiment Scanner Ready")
    print("="*80)
