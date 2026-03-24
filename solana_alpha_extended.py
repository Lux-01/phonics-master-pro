#!/usr/bin/env python3
"""
Solana On-Chain Alpha Hunter - Extended Analysis
"""

import requests
import json

# Extended list of recently launched Solana tokens with better holder distribution potential
ADDITIONAL_TOKENS = [
    "FjZYphaiZKy6mChpmoEYchMbgJ1FQF2Z6z4FoWdspump",  # IKEA Orangutan
    "41uQipnraTB8n9BCngxiccykEC8NKUh62yvU1uMrpump",  # Dogpin
    "FtMiwJGNX7pk4S9J8C6vW7AeQ4fo6YsWa96PBZW5pump",  # TikTok viral
    "D9MA9Qh9zF5L7fYNbjihiWYBzUe5q24c18Sp3mn6pump",  # Community token
    "6p8JkUzDHGBzD3CcA1UqyJb6U7NUrQNYPFetbbnpump",  # DOMO
    "GjJkxWyJJpE5ihcs8G7ASQFmvTr1w8x6nF5U5Atpump",  # Valentin
    "Sv6JFjR5uGmnTfCPNhjqDQCPSseiM9pdKsCeTuvpump",  # Cupid
    "GdQu8UjXtgD3uKGesa9Tbyf45JaiuNcdmkVYgU4Xpump",  # Trending
    "HcMJPKYQGrk7umsg6Ea5XfxFprqPSPa9u1RA1xeUpump",  # Unknown new
]

def check_rugcheck(token_address):
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None

def get_token_info_dexscreener(token_address):
    url = f"https://api.dexscreener.com/tokens/v1/solana/{token_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None

def analyze_token(token_address):
    results = {
        'token_address': token_address,
        'passes_criteria': False,
        'security_score': 0,
        'risks': []
    }
    
    rugcheck_data = check_rugcheck(token_address)
    if rugcheck_data:
        score = rugcheck_data.get('score', 0)
        results['rugcheck_score'] = score
        results['risks'] = [r.get('name', 'Unknown') for r in rugcheck_data.get('risks', [])]
        
        lp_data = rugcheck_data.get('lpLock', {})
        results['lp_locked'] = lp_data.get('usdc', 0) if isinstance(lp_data, dict) else 0
        
        mint_auth = rugcheck_data.get('mintAuthority', None)
        freeze_auth = rugcheck_data.get('freezeAuthority', None)
        results['mint_revoked'] = mint_auth is None
        results['freeze_revoked'] = freeze_auth is None
        
        holders = rugcheck_data.get('holders', [])
        if holders:
            results['top_holder_pct'] = holders[0].get('percentage', 0) if holders else 0
            results['top_10_holders_pct'] = sum(h.get('percentage', 0) for h in holders[:10])
            results['holder_count'] = len(holders)
        else:
            results['top_holder_pct'] = 100
            results['top_10_holders_pct'] = 100
            results['holder_count'] = 0
            
        security_score = 10
        if score > 0:
            security_score -= min(score / 100, 5)
        if not results['mint_revoked']:
            security_score -= 2
        if results['top_10_holders_pct'] > 50:
            security_score -= 2
        elif results['top_10_holders_pct'] > 25:
            security_score -= 1
        results['security_score'] = max(0, round(security_score, 1))
    
    dex_data = get_token_info_dexscreener(token_address)
    if dex_data and len(dex_data) > 0:
        pair = dex_data[0]
        results['token_name'] = pair.get('baseToken', {}).get('name', 'Unknown')
        results['symbol'] = pair.get('baseToken', {}).get('symbol', 'Unknown')
        results['price'] = pair.get('priceUsd', 0)
        results['market_cap'] = pair.get('marketCap', 0) or 0
        results['liquidity'] = pair.get('liquidity', {}).get('usd', 0) or 0
        results['volume_5m'] = pair.get('volume', {}).get('m5', 0) or 0
        results['volume_1h'] = pair.get('volume', {}).get('h1', 0) or 0
        results['volume_6h'] = pair.get('volume', {}).get('h6', 0) or 0
        results['volume_24h'] = pair.get('volume', {}).get('h24', 0) or 0
        results['dex_id'] = pair.get('dexId', 'Unknown')
        results['pair_age'] = pair.get('pairCreatedAt', 0)
        
        # Check for rising wedge (5m volume > 1h average)
        if results['volume_1h'] > 0:
            m5_to_h1_ratio = results['volume_5m'] / (results['volume_1h'] / 12) if results['volume_1h'] > 0 else 0
            results['rising_wedge'] = m5_to_h1_ratio > 1.5
            results['volume_ratio'] = m5_to_h1_ratio
        else:
            results['rising_wedge'] = False
            results['volume_ratio'] = 0
        
        # Criteria checks
        passes = True
        reasons = []
        
        if results['liquidity'] < 15000:
            passes = False
            reasons.append(f"Liquidity ${results['liquidity']:,.0f} < $15,000")
        if results['volume_5m'] < 5000:
            passes = False
            reasons.append(f"5m Volume ${results['volume_5m']:,.0f} < $5,000")
        if results['market_cap'] > 250000:
            passes = False
            reasons.append(f"Market Cap ${results['market_cap']:,.0f} > $250,000")
        if results.get('top_10_holders_pct', 100) > 25:
            passes = False
            reasons.append(f"Top 10 Holders {results['top_10_holders_pct']:.1f}% > 25%")
        if not results.get('mint_revoked', False):
            passes = False
            reasons.append("Mint NOT revoked")
            
        results['passes_criteria'] = passes
        results['fail_reasons'] = reasons
    
    return results

def main():
    print("="*80)
    print("SOLANA ALPHA HUNTER - EXTENDED SCAN")
    print("Searching for tokens meeting ALL criteria...")
    print("="*80)
    
    all_results = []
    passed_tokens = []
    close_candidates = []
    
    for token in ADDITIONAL_TOKENS:
        results = analyze_token(token)
        all_results.append(results)
        
        if results.get('dex_id'):
            print(f"\n{'='*80}")
            print(f"TOKEN: {results.get('token_name', 'Unknown')} (${results.get('symbol', 'N/A')})")
            print(f"CA: {token}")
            print(f"{'='*80}")
            print(f"  Market Cap: ${results.get('market_cap', 0):,.0f}")
            print(f"  Liquidity: ${results.get('liquidity', 0):,.2f}")
            print(f"  5m Volume: ${results.get('volume_5m', 0):,.2f}")
            print(f"  1h Volume: ${results.get('volume_1h', 0):,.2f}")
            print(f"  Security Score: {results.get('security_score', 0)}/10")
            print(f"  Top 10 Holders: {results.get('top_10_holders_pct', 100):.1f}%")
            print(f"  Mint Revoked: {results.get('mint_revoked', False)}")
            print(f"  Rising Wedge: {'✅' if results.get('rising_wedge') else '❌'} ({results.get('volume_ratio', 0):.2f}x)")
            
            if results['passes_criteria']:
                print(f"  ✅ PASSES ALL CRITERIA")
                passed_tokens.append(results)
            else:
                print(f"  ❌ Failed: {', '.join(results.get('fail_reasons', ['Unknown']))}")
                # Check if close (3/5 criteria)
                if len(results.get('fail_reasons', [])) <= 2:
                    close_candidates.append(results)
    
    print(f"\n{'='*80}")
    print("PASSED ALL CRITERIA")
    print(f"{'='*80}")
    if passed_tokens:
        for t in passed_tokens:
            print(f"\n✅ {t['token_name']} (${t['symbol']})")
            print(f"   CA: {t['token_address']}")
            print(f"   MC: ${t['market_cap']:,.0f} | Liq: ${t['liquidity']:,.0f}")
            print(f"   Security: {t['security_score']}/10")
    else:
        print("No tokens passed all criteria")
    
    print(f"\n{'='*80}")
    print("CLOSE CANDIDATES (3-4/5 criteria)")
    print(f"{'='*80}")
    if close_candidates:
        for t in close_candidates:
            print(f"\n⚠️  {t['token_name']} (${t['symbol']})")
            print(f"   CA: {t['token_address']}")
            print(f"   MC: ${t['market_cap']:,.0f} | Liq: ${t['liquidity']:,.0f} | 5m Vol: ${t['volume_5m']:,.0f}")
            print(f"   Missing: {', '.join(t.get('fail_reasons', []))}")
    
    return passed_tokens

if __name__ == "__main__":
    main()
