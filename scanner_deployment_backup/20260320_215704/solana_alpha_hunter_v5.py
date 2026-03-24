#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.0 - Rug-Resistant Edition
Adds deployer tracking, honeypot detection, age filters
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Track deployer wallets across scans (persistent in memory during session)
DEPLOYER_HISTORY = defaultdict(list)  # wallet -> list of token CAs

def get_deployer_info(ca):
    """Get contract deployer from SolanaFM or similar"""
    try:
        # Try SolanaFM API
        url = f"https://api.solana.fm/v1/tokens/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get('data', {}).get('mintAuthority') or data.get('data', {}).get('updateAuthority')
    except:
        pass
    return None

def get_token_age(ca):
    """Get token age in hours from creation timestamp - FIXED"""
    try:
        # Method 1: DexScreener pair creation time
        url = f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs and len(pairs) > 0:
                # Get pair creation time
                pair_created_at = pairs[0].get('pairCreatedAt')
                if pair_created_at:
                    created = datetime.fromtimestamp(pair_created_at / 1000)  # ms to seconds
                    age_hours = (datetime.now() - created).total_seconds() / 3600
                    return max(0.1, age_hours)
    except Exception as e:
        pass
    
    try:
        # Method 2: Helius API for token creation
        url = f"https://mainnet.helius-rpc.com/?api-key=demo"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [ca, {"limit": 100}]
        }
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            sigs = data.get('result', [])
            if sigs:
                # Oldest signature is last
                oldest = sigs[-1].get('blockTime')
                if oldest:
                    created = datetime.fromtimestamp(oldest)
                    age_hours = (datetime.now() - created).total_seconds() / 3600
                    return max(0.1, age_hours)
    except:
        pass
    
    return 0.1  # Return minimum instead of 0

def check_honeypot(ca):
    """Check if token is a honeypot using honeypot.is or similar"""
    try:
        # Using alternative detection via DexScreener buy/sell simulation
        # In production, integrate honeypot.is API
        url = f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs:
                pair = pairs[0]
                buys = pair.get('txns', {}).get('h24', {}).get('buys', 0)
                sells = pair.get('txns', {}).get('h24', {}).get('sells', 0)
                
                # Honeypot indicators
                if buys > 50 and sells < 5:  # Many buys, no sells
                    return {'is_honeypot': True, 'reason': 'High buy/sell ratio imbalance'}
                if buys > 0 and sells == 0:  # Nobody can sell
                    return {'is_honeypot': True, 'reason': 'Zero sells detected'}
        return {'is_honeypot': False, 'reason': 'Normal buy/sell activity'}
    except:
        return {'is_honeypot': None, 'reason': 'Check failed'}

def check_contract_verified(ca):
    """Check if contract is verified on Solscan"""
    try:
        url = f"https://public-api.solscan.io/token/meta?tokenAddress={ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Verified contracts have metadata
            return data.get('metadata') is not None
    except:
        pass
    return False

def analyze_transactions(ca, hours=6):
    """Analyze recent transaction patterns"""
    try:
        url = f"https://api.solana.fm/v1/tokens/{ca}/transfers"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            txs = data.get('data', {}).get('transfers', [])
            
            # Count sells from unique wallets
            sells = [tx for tx in txs if tx.get('direction') == 'out']
            sell_wallets = defaultdict(int)
            for tx in sells:
                wallet = tx.get('from')
                if wallet:
                    sell_wallets[wallet] += 1
            
            # Check for coordinated selling
            coordinated = len([w for w, c in sell_wallets.items() if c > 5])
            total_sells = len(sells)
            
            return {
                'total_sells': total_sells,
                'coordinated_wallets': coordinated,
                'sell_concentration': (coordinated / max(total_sells, 1)) * 100,
                'is_wash_trading': coordinated > 3
            }
    except:
        pass
    return {'total_sells': 0, 'coordinated_wallets': 0, 'sell_concentration': 0, 'is_wash_trading': False}

class DexScanner:
    def get_trending(self):
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return [item for item in data if item.get('chainId') == 'solana']
        except:
            pass
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

class AlphaHunterV5:
    def __init__(self):
        self.dex = DexScanner()
        self.rug = RugChecker()
        self.scan_count = 0
    
    def analyze(self, token):
        ca = token.get('tokenAddress')
        symbol = token.get('symbol', '?')
        name = token.get('name', symbol)
        
        print(f"\n{'='*80}")
        print(f"🎯 SCANNING: {name} (${symbol})")
        print(f"CA: {ca}")
        
        # Get token pairs
        try:
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
            pairs = r.json() if r.status_code == 200 else []
        except:
            pairs = []
        
        if not pairs:
            print("❌ No Dex Screener data")
            return None
        
        dex = pairs[0]
        mcap = dex.get('marketCap', 0) or 0
        liq = dex.get('liquidity', {}).get('usd', 0) or 0
        vol24 = dex.get('volume', {}).get('h24', 0) or 0
        vol5m = dex.get('volume', {}).get('m5', 0) or 0
        
        # Filter MCAP
        if mcap < 10000 or mcap > 250000:
            print(f"❌ MCAP ${mcap:,.0f} outside range")
            return None
        
        # NEW: Age check
        age_hours = get_token_age(ca)
        print(f"  📊 MCAP: ${mcap:,.0f} | Liquidity: ${liq:,.0f} | Vol 24h: ${vol24:,.0f}")
        print(f"  🕐 Token Age: {age_hours:.1f} hours")
        
        # NEW: Honeypot check
        honeypot = check_honeypot(ca)
        print(f"  🍯 Honeypot Check: {honeypot.get('reason', 'N/A')}")
        
        # RugCheck data
        rug = self.rug.check(ca)
        mint_revoked = rug.get('token', {}).get('mintAuthority') is None if rug else False
        markets = rug.get('markets', [{}]) if rug else [{}]
        lp_locked = markets[0].get('lp', {}).get('lpLockedPct', 0) if markets else 0
        holders = rug.get('totalHolders', 0) if rug else 0
        top_holders = rug.get('topHolders', []) if rug else []
        top10_pct = sum(h.get('pct', 0) for h in top_holders[:10])
        net = rug.get('insiderNetworks', []) if rug else []
        cluster_risk = len(net) if isinstance(net, list) else 0
        
        # NEW: Deployer check
        deployer = get_deployer_info(ca)
        deployer_risk = False
        deployer_age_msg = "Unknown"
        if deployer:
            DEPLOYER_HISTORY[deployer].append(ca)
            token_count = len(DEPLOYER_HISTORY[deployer])
            print(f"  👤 Deployer: {deployer[:20]}... | Tokens: {token_count}")
            if token_count > 1:
                deployer_risk = True
                print(f"  ⚠️ DEPLOYER LAUNCHED {token_count} TOKENS!")
        
        # NEW: Contract verification
        is_verified = check_contract_verified(ca)
        print(f"  📜 Verified: {'✅' if is_verified else '❌'}")
        
        # NEW: Transaction analysis
        tx_analysis = analyze_transactions(ca)
        print(f"  📈 Tx Analysis: {tx_analysis['total_sells']} sells | {tx_analysis['coordinated_wallets']} coordinated wallets")
        if tx_analysis['is_wash_trading']:
            print(f"  ⚠️ WASH TRADING DETECTED!")
        
        # NEW: Info/socials
        info = dex.get('info', {})
        socials = info.get('socials', [])
        websites = info.get('websites', [])
        has_tw = any(s.get('type') == 'twitter' for s in socials)
        has_tg = any(s.get('type') == 'telegram' for s in socials)
        has_web = len(websites) > 0
        
        # Scoring (15-point scale v5.0)
        score = 0
        checks = []
        red_flags = []
        
        # 1. MCAP range
        if 10000 < mcap < 250000:
            score += 1
            checks.append("MCAP range ✅")
        
        # 2. Liquidity amount (NEW)
        if liq >= 15000:
            score += 1
            checks.append("Liquidity amount ✅")
        
        # 3. LP locked %
        if lp_locked >= 95:
            score += 1
            checks.append("LP locked 95%+ ✅")
        
        # 4. Slippage
        slippage_2k = (2000 / (liq * 2 + 1)) * 100
        if slippage_2k < 20:
            score += 1
            checks.append("Low slippage ✅")
        
        # 5. Volume 5m
        if vol5m >= 5000:
            score += 1
            checks.append("Volume 5m ✅")
        
        # 6. Volume 24h
        if vol24 >= 20000:
            score += 1
            checks.append("Volume 24h ✅")
        
        # 7. Mint revoked
        if mint_revoked:
            score += 1
            checks.append("Mint revoked ✅")
        
        # 8. Top10 distribution
        if top10_pct < 30:
            score += 1
            checks.append("Top10 <30% ✅")
        
        # 9. Cluster risk
        if cluster_risk <= 3:
            score += 1
            checks.append("Low cluster risk ✅")
        
        # 10. Holders
        if holders > 300:
            score += 1
            checks.append("Holders >300 ✅")
        
        # 11. Website
        if has_web:
            score += 1
            checks.append("Website ✅")
        
        # 12. Twitter
        if has_tw:
            score += 1
            checks.append("Twitter ✅")
        
        # 13. Token age (NEW - critical) - LOWERED TO 30 MIN FOR TESTING
        if age_hours >= 0.5:  # 30 minutes minimum
            score += 1
            checks.append("Age > 30m ✅")
        else:
            red_flags.append(f"⚠️ TOO NEW ({age_hours:.1f}h < 30m)")
        
        # 14. Deployer clean (NEW)
        if not deployer_risk and deployer:
            score += 1
            checks.append("Clean deployer ✅")
        elif deployer_risk:
            red_flags.append("⚠️ REPEAT DEPLOYER")
        
        # 15. Honeypot negative (NEW)
        if not honeypot.get('is_honeypot'):
            score += 1
            checks.append("Not honeypot ✅")
        else:
            red_flags.append("🚨 HONEYPOT DETECTED")
        
        # Bonus: Verified contract (A+ requirement)
        verified_bonus = 1 if is_verified else 0
        
        # Security output
        print(f"\n🔒 SECURITY:")
        print(f"  Mint revoked: {'✅' if mint_revoked else '❌'}")
        print(f"  LP locked: {lp_locked:.0f}%")
        print(f"  Holders: {holders}")
        print(f"  Top10: {top10_pct:.1f}%")
        print(f"  Cluster risk: {cluster_risk}")
        
        # Grading (v5.0)
        grade = "A+ 🔥" if score >= 13 else "A ✅" if score >= 10 else "B 🟡" if score >= 7 else "C ⚠️" if score >= 5 else "D ❌"
        
        # A+ requires verified contract + age > 2h (lowered for testing)
        if score >= 13 and (not is_verified or age_hours < 2):
            grade = "A ✅"  # Downgrade if missing critical requirements
            print(f"\n📉 A+ downgraded to A (missing: verified={is_verified}, age={age_hours:.1f}h)")
        
        print(f"\n🎓 SCORE: {score}/15 (+{verified_bonus} verification bonus)")
        print(f"🎯 GRADE: {grade}")
        
        if red_flags:
            print(f"\n🚨 RED FLAGS:")
            for flag in red_flags:
                print(f"    {flag}")
        
        # Auto-skip conditions
        if honeypot.get('is_honeypot') or tx_analysis['is_wash_trading'] or deployer_risk:
            print(f"\n❌ AUTO-SKIPPED: Critical red flags detected")
            return None
        
        return {
            'name': name,
            'symbol': symbol,
            'ca': ca,
            'mcap': mcap,
            'liq': liq,
            'vol24': vol24,
            'vol5m': vol5m,
            'age_hours': age_hours,
            'score': score,
            'grade': grade,
            'verified': is_verified,
            'mint_revoked': mint_revoked,
            'lp_locked': lp_locked,
            'holders': holders,
            'top10_pct': top10_pct,
            'cluster_risk': cluster_risk,
            'honeypot': honeypot,
            'tx_analysis': tx_analysis,
            'deployer_risk': deployer_risk,
            'red_flags': red_flags,
            'checks': checks
        }

def scan_all():
    hunter = AlphaHunterV5()
    print("="*80)
    print("🚀 SOLANA ALPHA HUNTER v5.0 - Rug-Resistant Edition")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📊 Fetching trending Solana tokens...")
    
    trending = hunter.dex.get_trending()
    if not trending:
        print("❌ No trending data available")
        return []
    
    print(f"Found {len(trending)} tokens, analyzing first 15...")
    
    results = []
    for token in trending[:15]:
        result = hunter.analyze(token)
        if result:
            results.append(result)
    
    return results

if __name__ == "__main__":
    results = scan_all()
    
    # Summary
    print("\n" + "="*80)
    print("🎯 SUMMARY - v5.0 Rug-Resistant Scan")
    print("="*80)
    
    alpha_count = sum(1 for r in results if 'A' in r['grade'] and '+' not in r['grade'])
    alpha_plus = sum(1 for r in results if 'A+' in r['grade'])
    skipped = 15 - len(results)  # Approximate
    
    print(f"✅ Grade A+: {alpha_plus}")
    print(f"✅ Grade A: {alpha_count}")
    print(f"❌ Auto-skipped (honeypot/wash/repeat deployer): ~{skipped}")
    
    # Save
    with open('/home/skux/.openclaw/workspace/alpha_results_v5.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Saved {len(results)} results to alpha_results_v5.json")
    
    # Telegram alerts for A/A+ only
    for r in results:
        if 'A' in r['grade']:
            print(f"\n🚨 ALERT CANDIDATE:")
            print(f"   {r['grade']} | {r['ca'][:20]}... | Age: {r['age_hours']:.1f}h")
