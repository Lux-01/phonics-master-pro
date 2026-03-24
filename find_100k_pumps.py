#!/usr/bin/env python3
"""
Find tokens that pumped to 100k+ and analyze coordinated buyers
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"

def get_token_info(token_address):
    """Get token info from Helius"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Try to get metadata
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAsset",
        "params": [token_address]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get('result', {})
            metadata = result.get('content', {}).get('metadata', {})
            return {
                'name': metadata.get('name', 'Unknown'),
                'symbol': metadata.get('symbol', '???')
            }
    except Exception as e:
        pass
    return {'name': 'Unknown', 'symbol': '???'}

def get_token_buyers(token_address, hours_back=2):
    """Get recent buyers of a token"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Get recent transactions
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [token_address, {"limit": 50}]
    }
    
    buyers = []
    cutoff = datetime.now() - timedelta(hours=hours_back)
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            sigs = data.get('result', [])
            
            for sig_info in sigs:
                sig = sig_info.get('signature')
                block_time = sig_info.get('blockTime')
                
                if block_time:
                    tx_time = datetime.fromtimestamp(block_time)
                    if tx_time > cutoff:
                        # Get transaction details
                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                        }
                        
                        tx_resp = requests.post(url, json=tx_payload, headers=headers, timeout=5)
                        if tx_resp.status_code == 200:
                            tx_data = tx_resp.json().get('result', {})
                            meta = tx_data.get('meta', {})
                            
                            # Check token balances
                            pre = meta.get('preTokenBalances', [])
                            post = meta.get('postTokenBalances', [])
                            
                            # Map pre balances
                            pre_map = {b['accountIndex']: b for b in pre}
                            
                            for p_bal in post:
                                if p_bal.get('mint') == token_address:
                                    owner = p_bal.get('owner')
                                    post_amt = p_bal.get('uiTokenAmount', {}).get('uiAmount', 0)
                                    
                                    # Get pre balance
                                    pre_bal = pre_map.get(p_bal['accountIndex'], {})
                                    pre_amt = pre_bal.get('uiTokenAmount', {}).get('uiAmount', 0) if pre_bal else 0
                                    
                                    bought = post_amt - pre_amt
                                    
                                    if bought > 0 and owner:
                                        buyers.append({
                                            'wallet': owner,
                                            'amount': bought,
                                            'time': tx_time,
                                            'signature': sig
                                        })
                        
                        time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")
    
    return buyers

def find_coordinated_wallets(buyers, min_wallets=2, time_window_minutes=30):
    """Find wallets that bought within time window of each other"""
    if not buyers:
        return {}
    
    # Group by wallet
    wallet_buys = defaultdict(list)
    for b in buyers:
        wallet_buys[b['wallet']].append(b)
    
    # Find wallets active in same time window
    coordinated = {}
    wallets = list(wallet_buys.keys())
    
    for i, wallet1 in enumerate(wallets):
        for wallet2 in wallets[i+1:]:
            # Check if any buys are within time window
            for b1 in wallet_buys[wallet1]:
                for b2 in wallet_buys[wallet2]:
                    time_diff = abs((b1['time'] - b2['time']).total_seconds()) / 60
                    
                    if time_diff <= time_window_minutes:
                        if wallet1 not in coordinated:
                            coordinated[wallet1] = []
                        if wallet2 not in coordinated:
                            coordinated[wallet2] = []
                        
                        coordinated[wallet1].append({
                            'paired_with': wallet2,
                            'time_diff': time_diff,
                            'amount': b1['amount'],
                            'time': b1['time']
                        })
                        coordinated[wallet2].append({
                            'paired_with': wallet1,
                            'time_diff': time_diff,
                            'amount': b2['amount'],
                            'time': b2['time']
                        })
                        break
    
    return coordinated

def scan_for_100k_pumps():
    """Scan trending tokens for 100k+ pumps"""
    print("=" * 70)
    print("🚀 FINDING 100K PUMP TOKENS")
    print("=" * 70)
    
    # These are tokens we found earlier that are trending
    trending_tokens = [
        "7Qb1ozj3JV72rRjFmFesZdrcswctQs3VrmwQMAbwpump",  # LIPPY - $61k
        "ERqjbaj1fS2vFEUhobSSPMJ3xkoMs3fSvJSBHZ4Gpump",  # RETARDISM - $26k
    ]
    
    for token in trending_tokens:
        print(f"\n📊 Analyzing token: {token[:20]}...")
        
        # Get token info
        info = get_token_info(token)
        print(f"   Name: {info['name']} ({info['symbol']})")
        
        # Get recent buyers
        print("   Fetching buyers...")
        buyers = get_token_buyers(token, hours_back=6)
        
        if buyers:
            print(f"   Found {len(buyers)} recent buyers")
            
            # Find coordinated wallets
            coordinated = find_coordinated_wallets(buyers)
            
            if coordinated:
                print(f"\n   🎯 COORDINATED WALLETS FOUND: {len(coordinated)}")
                
                # Sort by number of coordinated buys
                sorted_wallets = sorted(
                    coordinated.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )
                
                for wallet, coord_info in sorted_wallets[:5]:
                    print(f"\n   Wallet: {wallet[:20]}...")
                    print(f"   Coordinated with: {len(coord_info)} other wallets")
                    total_bought = sum(c['amount'] for c in coord_info)
                    print(f"   Total bought: {total_bought:,.2f} tokens")
                    
                    # Show first coordination
                    if coord_info:
                        c = coord_info[0]
                        print(f"   Example: Bought within {c['time_diff']:.1f} min of {c['paired_with'][:15]}...")
        else:
            print("   No recent buyers found")
        
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ Scan complete")

if __name__ == "__main__":
    scan_for_100k_pumps()
