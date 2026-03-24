#!/usr/bin/env python3
"""
Quick LP Check - Single run
"""

import requests
import json

try:
    with open('/home/skux/.openclaw/workspace/solana-trader/.secrets/helius.key', 'r') as f:
        helius_key = f.read().strip()
except:
    print("❌ Helius key not found")
    exit(1)

helius_url = f'https://mainnet.helius-rpc.com/?api-key={helius_key}'

WALLETS = [
    '39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg',
    'LfEcaUf77iEhnz6gFpLqYgDb5Uk6Ekc5n69wu7Qa9Uw'
]

print("🔍 Quick LP Check")
print("="*60)

for wallet in WALLETS:
    print(f"\n👤 Wallet: {wallet[:25]}...")
    
    # Get signatures
    payload = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getSignaturesForAddress',
        'params': [wallet, {'limit': 10}]
    }
    
    try:
        r = requests.post(helius_url, json=payload, timeout=10)
        data = r.json()
        
        if 'result' in data:
            sigs = data['result']
            print(f"   Found {len(sigs)} transactions")
            
            for sig in sigs[:3]:  # Check first 3
                sig_str = sig['signature']
                print(f"\n   Checking tx: {sig_str[:20]}...")
                
                # Get tx details
                tx_payload = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'getTransaction',
                    'params': [sig_str, {'encoding': 'jsonParsed', 'maxSupportedTransactionVersion': 0}]
                }
                
                try:
                    tx_r = requests.post(helius_url, json=tx_payload, timeout=10)
                    tx_data = tx_r.json()
                    
                    if 'result' in tx_data and tx_data['result']:
                        tx = tx_data['result']
                        meta = tx.get('meta', {})
                        
                        # Check for token transfers
                        pre_tokens = meta.get('preTokenBalances', [])
                        post_tokens = meta.get('postTokenBalances', [])
                        
                        print(f"   Pre-token balances: {len(pre_tokens)}")
                        print(f"   Post-token balances: {len(post_tokens)}")
                        
                        # Check instructions
                        instructions = tx.get('transaction', {}).get('message', {}).get('instructions', [])
                        print(f"   Instructions: {len(instructions)}")
                        for inst in instructions[:3]:
                            if isinstance(inst, dict):
                                prog = inst.get('program')
                                parsed = inst.get('parsed', {})
                                if parsed:
                                    print(f"   - {parsed.get('type', 'unknown')}")
                        
                except Exception as e:
                    print(f"   Error fetching tx: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")
