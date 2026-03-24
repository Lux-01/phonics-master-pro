#!/usr/bin/env python3
"""
Find tokens that pumped to 100k MC within 30 min
Then identify coordinated wallets
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time

HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"

def get_recent_tokens():
    """Get recently launched tokens from Birdeye"""
    url = "https://public-api.birdeye.so/defi/tokenlist"
    headers = {"x-api-key": BIRDEYE_API_KEY}
    params = {
        "sort_by": "v24hUSD",
        "sort_type": "desc",
        "offset": 0,
        "limit": 100
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', {}).get('tokens', [])
    except Exception as e:
        print(f"Error fetching tokens: {e}")
    return []

def get_token_creation_time(token_address):
    """Get token creation time from first transaction"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Get first signatures for token
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [token_address, {"limit": 1}]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            sigs = data.get('result', [])
            if sigs:
                return datetime.fromtimestamp(sigs[0].get('blockTime', 0))
    except Exception as e:
        pass
    return None

def get_early_buyers(token_address, hours_back=2):
    """Get wallets that bought token early"""
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Get recent signatures
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [token_address, {"limit": 100}]
    }
    
    buyers = []
    cutoff = datetime.now() - timedelta(hours=hours_back)
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            sigs = data.get('result', [])
            
            for sig_info in sigs[:50]:  # First 50 transactions
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
                            post_balances = meta.get('postTokenBalances', [])
                            
                            # Find accounts that received token
                            for bal in post_balances:
                                if bal.get('mint') == token_address:
                                    owner = bal.get('owner')
                                    amount = bal.get('uiTokenAmount', {}).get('uiAmount', 0)
                                    if owner and amount > 0:
                                        buyers.append({
                                            'wallet': owner,
                                            'amount': amount,
                                            'time': tx_time,
                                            'signature': sig
                                        })
                        
                        time.sleep(0.05)  # Rate limit
    except Exception as e:
        print(f"Error fetching buyers: {e}")
    
    return buyers

def find_pump_tokens():
    """Find tokens that reached 100k MC quickly"""
    print("🔍 Scanning for 100k pump tokens...")
    print("="*70)
    
    tokens = get_recent_tokens()
    pump_candidates = []
    
    for token in tokens:
        mc = token.get('mc', 0) or 0
        v24h = token.get('v24hUSD', 0) or 0
        
        # Look for tokens 50k-500k MC with decent volume
        if 50000 < mc < 500000 and v24h > 10000:
            symbol = token.get('symbol', '???')
            address = token.get('address', '')
            name = token.get('name', 'Unknown')
            
            # Check how recently created
            creation = get_token_creation_time(address)
            if creation:
                age = datetime.now() - creation
                age_hours = age.total_seconds() / 3600
                
                if age_hours < 24:  # Less than 24h old
                    pump_candidates.append({
                        'name': name,
                        'symbol': symbol,
                        'address': address,
                        'mc': mc,
                        'volume': v24h,
                        'age_hours': age_hours,
                        'creation_time': creation
                    })
                    print(f"Found: {symbol} (${mc:,.0f} MC, {age_hours:.1f}h old)")
    
    return pump_candidates

def analyze_buyer_coordination(tokens):
    """Analyze buyer patterns across multiple tokens"""
    print("\n" + "="*70)
    print("📊 Analyzing buyer coordination...")
    print("="*70)
    
    all_buyers = defaultdict(lambda: defaultdict(list))
    
    for token in tokens[:5]:  # Analyze top 5
        print(f"\nChecking {token['symbol']} buyers...")
        buyers = get_early_buyers(token['address'])
        
        for buyer in buyers:
            wallet = buyer['wallet']
            all_buyers[wallet][token['symbol']].append({
                'amount': buyer['amount'],
                'time': buyer['time'],
                'token_address': token['address']
            })
        
        time.sleep(1)
    
    # Find wallets that bought multiple tokens
    coordinated = {}
    for wallet, tokens_bought in all_buyers.items():
        if len(tokens_bought) >= 2:
            coordinated[wallet] = tokens_bought
    
    return coordinated

def main():
    print("🚀 100K PUMP TOKEN SCANNER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Find pump tokens
    pump_tokens = find_pump_tokens()
    
    if not pump_tokens:
        print("\n❌ No 100k pump tokens found in last 24h")
        return
    
    print(f"\n✅ Found {len(pump_tokens)} pump tokens")
    
    # Sort by MC
    pump_tokens.sort(key=lambda x: x['mc'], reverse=True)
    
    print("\n" + "="*70)
    print("📈 TOP PUMP TOKENS:")
    print("="*70)
    
    for i, token in enumerate(pump_tokens[:10], 1):
        print(f"\n{i}. {token['name']} ({token['symbol']})")
        print(f"   CA: {token['address']}")
        print(f"   MC: ${token['mc']:,.0f}")
        print(f"   Volume 24h: ${token['volume']:,.0f}")
        print(f"   Age: {token['age_hours']:.1f} hours")
    
    # Analyze buyer coordination
    coordinated_wallets = analyze_buyer_coordination(pump_tokens)
    
    if coordinated_wallets:
        print("\n" + "="*70)
        print("🎯 COORDINATED WALLETS:")
        print("="*70)
        
        sorted_wallets = sorted(
            coordinated_wallets.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for wallet, tokens in sorted_wallets[:10]:
            print(f"\nWallet: {wallet}")
            print(f"   Tokens coordinated: {len(tokens)}")
            for symbol, purchases in tokens.items():
                total = sum(p['amount'] for p in purchases)
                print(f"   • {symbol}: {total:,.2f} tokens")
    else:
        print("\n❌ No coordinated wallets found")
    
    print(f"\n✅ Scan complete at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
