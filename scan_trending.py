#!/usr/bin/env python3
import requests
import json
from datetime import datetime

class DexScanner:
    def get_trending(self):
        # Get trending tokens from Dex Screener Solana
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return [item for item in data if item.get('chainId') == 'solana']
        except Exception as e:
            print(f"Error fetching trending: {e}")
        return []

class RugChecker:
    def check(self, ca):
        try:
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=10)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return {}

class AlphaGrader:
    def __init__(self):
        self.dex = DexScanner()
        self.rug = RugChecker()
        
    def analyze(self, token):
        ca = token.get('tokenAddress')
        symbol = token.get('symbol', '?')
        name = token.get('name', symbol)
        
        print(f"\n{'='*80}")
        print(f"🎯 SCANNING: {name} (${symbol})")
        print(f"CA: {ca}")
        
        # Get token pairs data
        try:
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
            pairs = r.json() if r.status_code == 200 else []
        except:
            pairs = []
        
        if not pairs:
            print("❌ No Dex Screener data")
            return None
        
        pairs = pairs[:2]  # Top 2 pairs
        
        for dex in pairs:
            mcap = dex.get('marketCap', 0) or 0
            liq = dex.get('liquidity', {}).get('usd', 0) or 0
            vol24 = dex.get('volume', {}).get('h24', 0) or 0
            vol5m = dex.get('volume', {}).get('m5', 0) or 0
            
            # Filter MCAP range
            if mcap < 10000 or mcap > 250000:
                print(f"❌ MCAP ${mcap:,.0f} outside range")
                return None
            
            print(f"  📊 MCAP: ${mcap:,.0f} | Liquidity: ${liq:,.0f} | Vol 24h: ${vol24:,.0f}")
        
        # Security check
        rug = self.rug.check(ca)
        mint_revoked = rug.get('token', {}).get('mintAuthority') is None if rug else False
        markets = rug.get('markets', [{}]) if rug else [{}]
        lp_locked = markets[0].get('lp', {}).get('lpLockedPct', 0) if markets else 0
        holders = rug.get('totalHolders', 0) if rug else 0
        top_holders = rug.get('topHolders', []) if rug else []
        top10_pct = sum(h.get('pct', 0) for h in top_holders[:10])
        
        # Check for red flags
        net = rug.get('insiderNetworks', []) if rug else []
        cluster_risk = len(net) if isinstance(net, list) else 0
        
        # Scoring (12-point scale)
        score = 0
        checks = []
        
        for dex in pairs[:1]:
            mcap = dex.get('marketCap', 0) or 0
            liq = dex.get('liquidity', {}).get('usd', 0) or 0
            vol24 = dex.get('volume', {}).get('h24', 0) or 0
            vol5m = dex.get('volume', {}).get('m5', 0) or 0
            
            # MCAP range
            if 10000 < mcap < 250000:
                score += 1
                checks.append("MCAP range ✅")
            
            # Liquidity
            if liq >= 15000:
                score += 1
                checks.append("Liquidity ✅")
            
            # Slippage check
            slippage_2k = (2000 / (liq * 2 + 1)) * 100
            if slippage_2k < 20:
                score += 1
                checks.append("Low slippage ✅")
            
            # Volume
            if vol5m >= 5000:
                score += 1
                checks.append("Volume 5m ✅")
            if vol24 >= 20000:
                score += 1
                checks.append("Volume 24h ✅")
            
            # Info
            info = dex.get('info', {})
            socials = info.get('socials', [])
            websites = info.get('websites', [])
            
            has_tw = any(s.get('type') == 'twitter' for s in socials)
            has_tg = any(s.get('type') == 'telegram' for s in socials)
            has_web = len(websites) > 0
            
            # Security
            if mint_revoked:
                score += 1
                checks.append("Mint revoked ✅")
            if lp_locked >= 95:
                score += 1
                checks.append("LP locked 95%+ ✅")
            if top10_pct < 30:
                score += 1
                checks.append("Top10 <30% ✅")
            if cluster_risk <= 3:
                score += 1
                checks.append("Low cluster risk ✅")
            if holders > 300:
                score += 1
                checks.append("Holders >300 ✅")
            if has_web:
                score += 1
                checks.append("Website ✅")
            if has_tw:
                score += 1
                checks.append("Twitter ✅")
            
            # Security red flags
            red_flags = []
            if top10_pct > 60:
                red_flags.append("⚠️ HIGH TOP10 PCT")
            if cluster_risk > 5:
                red_flags.append("⚠️ CLUSTER RISK")
            if lp_locked < 50:
                red_flags.append("⚠️ LP NOT LOCKED")
            
            grade = "A+" if score >= 11 else "A" if score >= 9 else "B" if score >= 7 else "C" if score >= 6 else "D"
            
            print(f"\n🔒 SECURITY:")
            print(f"  Mint revoked: {'✅' if mint_revoked else '❌'}")
            print(f"  LP locked: {lp_locked:.0f}%")
            print(f"  Holders: {holders}")
            print(f"  Top10: {top10_pct:.1f}%")
            print(f"  Cluster risk: {cluster_risk}")
            
            print(f"\n🎓 GRADE: {grade} ({score}/12 points)")
            
            if red_flags:
                print(f"\n🚨 RED FLAGS: {' | '.join(red_flags)}")
            
            return {
                'name': name,
                'symbol': symbol,
                'ca': ca,
                'mcap': mcap,
                'liq': liq,
                'vol24': vol24,
                'vol5m': vol5m,
                'score': score,
                'grade': grade,
                'mint_revoked': mint_revoked,
                'lp_locked': lp_locked,
                'holders': holders,
                'top10_pct': top10_pct,
                'cluster_risk': cluster_risk,
                'red_flags': red_flags,
                'has_twitter': has_tw,
                'has_telegram': has_tg,
                'has_website': has_web,
                'checks': checks
            }
        
        return None

def scan_all():
    scanner = AlphaGrader()
    print("="*80)
    print("🚀 SOLANA ALPHA HUNTER - Daily Scan")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📊 Fetching trending Solana tokens...")
    
    trending = scanner.dex.get_trending()
    if not trending:
        print("❌ No trending data available")
        return []
    
    print(f"Found {len(trending)} tokens")
    
    results = []
    for token in trending[:15]:  # Check first 15 only
        result = scanner.analyze(token)
        if result:
            results.append(result)
    
    return results

if __name__ == "__main__":
    results = scan_all()
    
    # Print summary
    print("\n" + "="*80)
    print("🎯 SUMMARY")
    print("="*80)
    
    alpha_count = sum(1 for r in results if r['grade'] in ['A', 'A+'])
    beta_count = sum(1 for r in results if r['grade'] == 'B')
    red_flags = sum(1 for r in results if r['red_flags'])
    
    print(f"✅ Grade A/A+: {alpha_count}")
    print(f"🟡 Grade B: {beta_count}")
    print(f"⚠️ Red flags: {red_flags}")
    
    # Save results for telegram alerts
    with open('/home/skux/.openclaw/workspace/alpha_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Saved {len(results)} results to alpha_results.json")
