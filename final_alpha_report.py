#!/usr/bin/env python3
"""
Final Analysis of Tokens from First Scan
"""

import requests

# Top performers from first scan
tokens_to_analyze = [
    "D8kRu1fQ5MmSPLj5g1A3NK1C2TaMdUWFP7G4s8vPpump",  # MERTCODING
    "GmNFpyNvGk9GeLoapCFpFv7xgDrw3B7aDw1ytpa7pump",  # mertcoin
    "5ENqMfqjfW3npjZPAPdtCpSRR8bBNzX1oSASXP1apump",  # Peppen
    "7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump",  # Lumo
    "8Y4iGgprZwmH6vj4v7BfRcZaN89TCd6JxYrQ7tNkpump",  # DITTO
    "Dza3Bey5tvyYiPgcGRKoXKU6rNrdoNrWNVmjqePcpump",  # UNSYS
]

def check_rugcheck(token_address):
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"RugCheck API returned {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def get_dexscreener(token_address):
    url = f"https://api.dexscreener.com/tokens/v1/solana/{token_address}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None

def main():
    print("="*100)
    print("FINAL ALPHA REPORT - DETAILED ANALYSIS")
    print("="*100)
    
    for token in tokens_to_analyze:
        print("\n")
        print("="*100)
        print(f"CA: {token}")
        print("="*100)
        
        # Get data
        rc = check_rugcheck(token)
        dex = get_dexscreener(token)
        
        if dex and len(dex) > 0:
            pair = dex[0]
            name = pair.get('baseToken', {}).get('name', 'Unknown')
            symbol = pair.get('baseToken', {}).get('symbol', 'N/A')
            mc = pair.get('marketCap', 0) or 0
            liq = pair.get('liquidity', {}).get('usd', 0) or 0
            v5m = pair.get('volume', {}).get('m5', 0) or 0
            v1h = pair.get('volume', {}).get('h1', 0) or 0
            v24h = pair.get('volume', {}).get('h24', 0) or 0
            price = pair.get('priceUsd', 0)
            dex_name = pair.get('dexId', 'Unknown')
            
            print(f"\n🪙 TOKEN: {name} (${symbol})")
            print(f"🔗 DEX: {dex_name}")
            
            print(f"\n📊 FINANCIALS:")
            print(f"   Market Cap:    ${mc:,>12.2f}")
            print(f"   Liquidity:     ${liq:,>12.2f}")
            print(f"   Price:         ${price}")
            
            print(f"\n📈 VOLUME:")
            print(f"   5m:   ${v5m:,>14.2f}")
            print(f"   1h:   ${v1h:,>14.2f}")
            print(f"   24h:  ${v24h:,>14.2f}")
            
            # Rising wedge check
            if v1h > 0:
                avg_5m = v1h / 12
                ratio = v5m / avg_5m if avg_5m > 0 else 0
                print(f"\n📉 RISING WEDGE ANALYSIS:")
                print(f"   5m vs 1h Avg: {ratio:.2f}x")
                if ratio > 3:
                    print(f"   🔥 STRONG Rising Wedge Detected!")
                elif ratio > 1.5:
                    print(f"   ✅ Rising Volume Pattern")
                else:
                    print(f"   ⚠️  Volume declining")
            
            if rc:
                score = rc.get('score', 'N/A')
                holders = rc.get('holders', [])
                mint = rc.get('mintAuthority')
                freeze = rc.get('freezeAuthority')
                
                print(f"\n🔒 SECURITY (RugCheck):")
                print(f"   Risk Score:     {score}")
                print(f"   Mint Revoked:   {'✅ YES (Safe)' if mint is None else '❌ NO (Risk)'}")
                print(f"   Freeze Revoked: {'✅ YES (Safe)' if freeze is None else '❌ NO (Risk)'}")
                
                if holders:
                    top1 = holders[0].get('percentage', 0) if holders else 0
                    top10 = sum(h.get('percentage', 0) for h in holders[:10])
                    print(f"   Top Holder:     {top1:.2f}%")
                    print(f"   Top 10:         {top10:.2f}%")
                    print(f"   Total Holders:  {len(holders)}")
                    
                    # Bundle check
                    if top10 > 90:
                        print(f"\n   ⚠️  BUNDLE DETECTED: High concentration suggests bundled launch")
                    elif top10 > 50:
                        print(f"\n   ⚠️  HIGH CONCENTRATION: Top 10 owns {top10:.1f}%")
                    else:
                        print(f"\n   ✅ GOOD DISTRIBUTION: Top 10 owns {top10:.1f}%")
            
            # Criteria check
            print(f"\n🎯 CRITERIA CHECK:")
            criteria = []
            if liq >= 15000:
                criteria.append(f"✅ Liquidity ${liq:,.0f} ≥ $15k")
            else:
                criteria.append(f"❌ Liquidity ${liq:,.0f} < $15k")
                
            if v5m >= 5000:
                criteria.append(f"✅ 5m Vol ${v5m:,.0f} ≥ $5k")
            else:
                criteria.append(f"❌ 5m Vol ${v5m:,.0f} < $5k")
                
            if mc <= 250000:
                criteria.append(f"✅ MC ${mc:,.0f} ≤ $250k")
            else:
                criteria.append(f"❌ MC ${mc:,.0f} > $250k")
                
            if rc:
                holders = rc.get('holders', [])
                top10 = sum(h.get('percentage', 0) for h in holders[:10]) if holders else 100
                mint = rc.get('mintAuthority')
                
                if top10 < 25:
                    criteria.append(f"✅ Top10 {top10:.1f}% < 25%")
                else:
                    criteria.append(f"❌ Top10 {top10:.1f}% > 25%")
                    
                if mint is None:
                    criteria.append(f"✅ Mint Revoked")
                else:
                    criteria.append(f"❌ Mint NOT Revoked")
                    
            for c in criteria:
                print(f"   {c}")
            
            passed = sum(1 for c in criteria if c.startswith("✅"))
            total = len(criteria)
            print(f"\n📊 RESULT: {passed}/{total} Criteria Passed")
            
            if passed == total:
                print(f"\n🚀 FULL ALPHA - ALL CRITERIA MET!")
            elif passed >= total - 1:
                print(f"\n⚠️  CLOSE - Almost there")
        else:
            print(f"❌ No data available")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    main()
