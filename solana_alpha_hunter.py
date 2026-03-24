#!/usr/bin/env python3
"""
Solana On-Chain Alpha Hunter
Scans for new tokens meeting specific criteria
"""

import requests
import json
from datetime import datetime, timedelta

# Token addresses from Dex Screener profiles
# These are recently launched tokens we found
POTENTIAL_TOKENS = [
    "D8kRu1fQ5MmSPLj5g1A3NK1C2TaMdUWFP7G4s8vPpump",
    "GmNFpyNvGk9GeLoapCFpFv7xgDrw3B7aDw1ytpa7pump",
    "5ENqMfqjfW3npjZPAPdtCpSRR8bBNzX1oSASXP1apump",  # $PEPPEN
    "7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump",  # $Lumo
    "4H2P8UT5ajRiSAT82NKStG5eydMDonTEnU4GcPRApump",
    "8Y4iGgprZwmH6vj4v7BfRcZaN89TCd6JxYrQ7tNkpump",  # DefiTheOdds
    "Dza3Bey5tvyYiPgcGRKoXKU6rNrdoNrWNVmjqePcpump",  # uncertain.systems
    "GRr8GcrCAmRYRWTxzxGs7gH3En4Dr8iXVdtTkUbYpump",  # Sense AI
    "MwtYY8neNXU6U9FMZHSveeHx4bHXe1JHfGYyXuupump",  # Gekko
    "6RbzrC3JWyCPwAFLwiQJkvNjTj21SjTYaQ7WjXGMpump",  # Duck Dash
]

def check_rugcheck(token_address):
    """Check token on RugCheck.xyz"""
    # RugCheck API endpoint
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error checking RugCheck: {e}")
    return None

def get_token_info_dexscreener(token_address):
    """Get token info from Dex Screener"""
    url = f"https://api.dexscreener.com/tokens/v1/solana/{token_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching Dex Screener: {e}")
    return None

def analyze_token(token_address):
    """Analyze a single token against criteria"""
    results = {
        'token_address': token_address,
        'passes_criteria': False,
        'security_score': 0,
        'risks': []
    }
    
    # Get RugCheck data
    rugcheck_data = check_rugcheck(token_address)
    if rugcheck_data:
        score = rugcheck_data.get('score', 0)
        results['rugcheck_score'] = score
        
        # Check risks
        risks = rugcheck_data.get('risks', [])
        results['risks'] = [r.get('name', 'Unknown') for r in risks]
        
        # Check LP status
        lp_data = rugcheck_data.get('lpLock', {})
        lp_lock_pct = lp_data.get('usdc', 0) if isinstance(lp_data, dict) else 0
        results['lp_locked'] = lp_lock_pct
        
        # Check mint authority
        mint_auth = rugcheck_data.get('mintAuthority', None)
        freeze_auth = rugcheck_data.get('freezeAuthority', None)
        results['mint_revoked'] = mint_auth is None
        results['freeze_revoked'] = freeze_auth is None
        
        # Check holders
        holders = rugcheck_data.get('holders', [])
        if holders:
            top_holder_pct = holders[0].get('percentage', 0) if holders else 0
            top_10_pct = sum(h.get('percentage', 0) for h in holders[:10])
            results['top_holder_pct'] = top_holder_pct
            results['top_10_holders_pct'] = top_10_pct
        else:
            results['top_holder_pct'] = 100
            results['top_10_holders_pct'] = 100
            
        # Calculate security score (out of 10)
        security_score = 10
        if score > 0:
            security_score -= min(score / 100, 5)  # Risk score penalty
        if not results['mint_revoked']:
            security_score -= 2
        if results['top_10_holders_pct'] > 50:
            security_score -= 2
        elif results['top_10_holders_pct'] > 25:
            security_score -= 1
        results['security_score'] = max(0, round(security_score, 1))
    
    # Get Dex Screener data
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
        results['volume_24h'] = pair.get('volume', {}).get('h24', 0) or 0
        results['dex_id'] = pair.get('dexId', 'Unknown')
        
        # Check criteria
        passes = True
        if results['liquidity'] < 15000:
            passes = False
            results['fail_reason'] = f"Liquidity too low (${results['liquidity']:,.0f} < $15,000)"
        elif results['volume_5m'] < 5000:
            passes = False
            results['fail_reason'] = f"5m Volume too low (${results['volume_5m']:,.0f} < $5,000)"
        elif results['market_cap'] > 250000:
            passes = False
            results['fail_reason'] = f"Market cap too high (${results['market_cap']:,.0f} > $250,000)"
        elif results.get('top_10_holders_pct', 100) > 25:
            passes = False
            results['fail_reason'] = f"Top 10 holders too concentrated ({results['top_10_holders_pct']:.1f}% > 25%)"
        elif not results.get('mint_revoked', False):
            passes = False
            results['fail_reason'] = "Mint authority NOT revoked"
        
        results['passes_criteria'] = passes
    
    return results

def print_analysis(results):
    """Print analysis results"""
    print(f"\n{'='*80}")
    print(f"TOKEN: {results.get('token_name', 'Unknown')} (${results.get('symbol', 'N/A')})")
    print(f"CA: {results['token_address']}")
    print(f"{'='*80}")
    
    print(f"\n📊 MARKET DATA:")
    print(f"  Market Cap: ${results.get('market_cap', 0):,.0f}")
    print(f"  Liquidity: ${results.get('liquidity', 0):,.2f}")
    price = results.get('price', 0)
    try:
        price = float(price)
        print(f"  Price: ${price:,.10f}")
    except:
        print(f"  Price: ${price}")
    print(f"  DEX: {results.get('dex_id', 'Unknown')}")
    
    print(f"\n📈 VOLUME:")
    print(f"  5m Volume: ${results.get('volume_5m', 0):,.2f}")
    print(f"  1h Volume: ${results.get('volume_1h', 0):,.2f}")
    print(f"  24h Volume: ${results.get('volume_24h', 0):,.2f}")
    
    print(f"\n🔒 SECURITY:")
    print(f"  Security Score: {results.get('security_score', 0)}/10")
    print(f"  RugCheck Score: {results.get('rugcheck_score', 'N/A')}")
    print(f"  Mint Revoked: {'✅' if results.get('mint_revoked') else '❌'}")
    print(f"  Freeze Revoked: {'✅' if results.get('freeze_revoked') else '❌'}")
    print(f"  LP Locked: {results.get('lp_locked', 'N/A')}")
    print(f"  Top Holder: {results.get('top_holder_pct', 100):.1f}%")
    print(f"  Top 10 Holders: {results.get('top_10_holders_pct', 100):.1f}%")
    
    if results.get('risks'):
        print(f"\n⚠️  RISKS DETECTED:")
        for risk in results['risks'][:5]:
            print(f"  - {risk}")
    
    print(f"\n🎯 CRITERIA CHECK:")
    if results['passes_criteria']:
        print(f"  ✅ PASSES ALL CRITERIA")
    else:
        print(f"  ❌ FAILED: {results.get('fail_reason', 'Unknown')}")
    
    return results['passes_criteria']

def main():
    print("="*80)
    print("SOLANA ON-CHAIN ALPHA HUNTER - FINAL REPORT")
    print("Scanning for high-potential new tokens...")
    print("="*80)
    
    passed_tokens = []
    
    for token in POTENTIAL_TOKENS:
        results = analyze_token(token)
        passed = print_analysis(results)
        if passed:
            passed_tokens.append(results)
    
    print(f"\n{'='*80}")
    print("SUMMARY - TOKENS PASSING ALL CRITERIA")
    print(f"{'='*80}")
    if passed_tokens:
        for t in passed_tokens:
            print(f"✅ {t['token_name']} (${t['symbol']}) - CA: {t['token_address']}")
    else:
        print("❌ No tokens passed all criteria")
    
    return passed_tokens

if __name__ == "__main__":
    main()
