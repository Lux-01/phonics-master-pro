#!/usr/bin/env python3
"""
🚀 Proactive Trading Monitor
Checks positions and alerts on opportunities
"""

import requests
import json
from datetime import datetime

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# Current holdings (from memory)
HOLDINGS = {
    "INCOME": {
        "address": "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump",
        "amount": 490.916016,
        "buy_price_sol": 0.001,
        "status": "needs_sell"
    }
}

def check_token_price(token_address):
    """Check current token price via DexScreener"""
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{token_address}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                pair = data[0]
                return {
                    "price_usd": float(pair.get('priceUsd', 0)),
                    "liquidity": pair.get('liquidity', {}).get('usd', 0),
                    "volume_24h": pair.get('volume', {}).get('h24', 0),
                    "price_change_24h": pair.get('priceChange', {}).get('h24', 0),
                    "dex": pair.get('dexId', 'Unknown')
                }
    except Exception as e:
        print(f"   Error checking price: {e}")
    
    return None

def monitor_positions():
    """Monitor all holdings"""
    print("="*70)
    print("📊 PROACTIVE TRADING MONITOR")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Wallet: {WALLET[:10]}...{WALLET[-6:]}")
    print("="*70)
    
    alerts = []
    
    for token_name, data in HOLDINGS.items():
        print(f"\n🔍 Checking {token_name}...")
        
        price_data = check_token_price(data['address'])
        
        if price_data:
            current_price = price_data['price_usd']
            amount = data['amount']
            value_usd = current_price * amount
            
            print(f"   Price: ${current_price:.8f}")
            print(f"   Holdings: {amount:.2f} tokens")
            print(f"   Value: ${value_usd:.2f}")
            print(f"   24h Change: {price_data['price_change_24h']:.2f}%")
            print(f"   Liquidity: ${price_data['liquidity']:,.0f}")
            print(f"   DEX: {price_data['dex']}")
            
            # Check for alerts
            if data.get('status') == 'needs_sell':
                alerts.append({
                    'token': token_name,
                    'message': f"🚨 {token_name} needs to be sold manually",
                    'value': value_usd,
                    'action': f"https://jup.ag/swap/{data['address']}-SOL"
                })
            
            if price_data['price_change_24h'] > 50:
                alerts.append({
                    'token': token_name,
                    'message': f"🚀 {token_name} up {price_data['price_change_24h']:.1f}%! Consider taking profits",
                    'value': value_usd
                })
                
        else:
            print(f"   ❌ Could not fetch price data")
    
    # Display alerts
    if alerts:
        print("\n" + "="*70)
        print("🚨 ALERTS")
        print("="*70)
        for alert in alerts:
            print(f"\n{alert['message']}")
            if 'action' in alert:
                print(f"   Action: {alert['action']}")
    else:
        print("\n✅ No alerts - all positions normal")
    
    print("\n" + "="*70)
    print("💡 Proactive Actions:")
    print("   • Sell INCOME when convenient (manual via Jupiter)")
    print("   • Monitor for new trading opportunities")
    print("   • Check LuxTrader for new signals")
    print("="*70)

def find_new_opportunities():
    """Scan for new trading opportunities"""
    print("\n🔍 Scanning for new opportunities...")
    
    # This would connect to your scanner
    # For now, just a placeholder
    
    print("   💡 Tip: Run quick_meme_scan_v3.py for live opportunities")

if __name__ == "__main__":
    monitor_positions()
    find_new_opportunities()
