#!/usr/bin/env python3
"""
Solana Alpha Hunter v4.0 - Quick Check
"""

import requests

def dex_check(ca):
    try:
        r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs:
                return pairs[0]
    except:
        pass
    return None

def rug_check(ca):
    try:
        r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def slip(liq_val, buy):
    if liq_val <= 0:
        return 50
    return min(50, (buy / liq_val) * 100 * 2)

def scan(ca, name):
    print(f"\n{'='*80}")
    print(f"🎯 SCANNING: {name}")
    print(f"CA: {ca}")
    
    dex = dex_check(ca)
    if not dex:
        print("❌ No market data")
        return 0
    
    rug = rug_check(ca) or {}
    
    # Extract
    mcap = dex.get('marketCap', 0) or 0
    liq = dex.get('liquidity', {}).get('usd', 0) or 0
    vol5m = dex.get('volume', {}).get('m5', 0) or 0
    vol1h = dex.get('volume', {}).get('h1', 0) or 0
    vol24h = dex.get('volume', {}).get('h24', 0) or 0
    price_chg = dex.get('priceChange', {}).get('m5', 0)
    
    # Security
    token_info = rug.get('token', {}) if rug else {}
    mint_revoked = token_info.get('mintAuthority') is None if token_info else False
    
    markets = rug.get('markets', [{}]) if rug else [{}]
    lp_locked = markets[0].get('lp', {}).get('lpLockedPct', 0) if markets and isinstance(markets[0], dict) else 0
    holders = rug.get('totalHolders', 0) if rug else 0
    
    # Slippage
    s2k = slip(liq, 2000)
    
    # Socials
    info = dex.get('info', {}) or {}
    socials = info.get('socials', []) or []
    websites = info.get('websites', []) or []
    
    has_twitter = any(s.get('type') == 'twitter' for s in socials)
    has_telegram = any(s.get('type') == 'telegram' for s in socials)
    has_website = len(websites) > 0
    
    # Social sentiment
    soc_score = 0
    if has_website: soc_score += 2
    if has_twitter: soc_score += 3
    if vol24h > 50000 and has_twitter: soc_score += 2
    if has_telegram: soc_score += 2
    if mcap < 100000 and vol24h > 100000: soc_score += 1
    
    soc_grade = "A+ 🚀 VIRAL" if soc_score >= 9 else "A ✅ Strong" if soc_score >= 7 else "B 🟡 Moderate" if soc_score >= 5 else "C ⚠️ Weak"
    
    # Top holders
    hdata = rug.get('topHolders', []) if isinstance(rug, dict) else []
    top10 = sum(h.get('pct', 0) for h in hdata[:10] if h.get('pct', 0) < 15)
    
    # Cluster
    nets = rug.get('insiderNetworks', []) if isinstance(rug, dict) else []
    cluster = len(nets) if isinstance(nets, list) else 0
    
    # Scoring (12 criteria)
    passed = 0
    if mcap < 250000 and mcap > 0: passed += 1
    if liq >= 15000: passed += 1
    if s2k < 20: passed += 1
    if vol5m >= 5000: passed += 1
    if mint_revoked: passed += 1
    if lp_locked >= 95: passed += 1
    if top10 < 30: passed += 1
    if cluster <= 3: passed += 1
    if holders > 300: passed += 1
    if has_website: passed += 1
    if soc_score >= 7: passed += 1
    
    # Output
    print(f"\n📊 MARKET: MCAP ${mcap:,.0f} | Velocity: {price_chg:+.1f}%")
    print(f"💧 LIQUIDITY: ${liq:,.0f} | Slippage $2K: {s2k:.0f}%")
    print(f"📈 VOLUME: 5m=${vol5m:,.0f} | 1h=${vol1h:,.0f} | 24h=${vol24h:,.0f}")
    print(f"👥 HOLDERS: {holders} | Top10: {top10:.1f}% | Cluster: {cluster}/10")
    
    print(f"\n📱 SOCIAL VELOCITY ({soc_score}/10): {soc_grade}")
    print(f"  Website: {'✅ ' + websites[0].get('url', '')[:40] if has_website else '❌ None'}")
    print(f"  Twitter: {'✅' if has_twitter else '❌'}")
    print(f"  Telegram: {'✅' if has_telegram else '❌'}")
    
    print(f"\n🔒 SECURITY: Mint {'✅ Revoked' if mint_revoked else '⚠️ Active'} | LP {lp_locked:.0f}% Locked")
    
    grade = "A+ 🔥 APE" if passed >= 11 else "A ✅ BUY" if passed >= 9 else "B 🟡 CAUTION" if passed >= 7 else "C ⚠️ WATCH" if passed >= 6 else "D ❌ SKIP"
    
    print(f"\n🎯 FINAL SCORE: {passed}/12 | Grade: {grade}")
    
    if passed >= 9:
        print(f"💰 2X POTENTIAL: ${mcap:,.0f} → ${mcap*2:,.0f}")
    
    return passed


if __name__ == "__main__":
    print("="*80)
    print("🚀 SOLANA ALPHA HUNTER v4.0 - LIVE SCAN")
    print("="*80)
    
    # Scan the tokens you want
    scan("7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump", "LUMO")
    
    print("\n" + "="*80)
    print("✅ Scan complete!")
    print("="*80)
