#!/usr/bin/env python3
"""
Check all positions via Solana RPC (like Phantom would)
Query token accounts and calculate real P&L
"""

import requests
import json
import base64
from datetime import datetime

# Config
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
HELIUS_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_KEY}"
SOL_MINT = "So11111111111111111111111111111111111111112"

# Load executed trades
with open('/home/skux/.openclaw/workspace/agents/skylar/skylar_live_executed.json', 'r') as f:
    data = json.load(f)

positions = [t for t in data['trades'] if t['status'] == 'SUCCESS']

print("=" * 70)
print("👻 PHANTOM-STYLE WALLET CHECK")
print("=" * 70)
print(f"Wallet: {WALLET}")
print(f"Checking {len(positions)} positions via Solana RPC...")
print("=" * 70)

# Get all token accounts for wallet
def get_token_accounts(wallet_address):
    """Get all SPL token accounts for wallet"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    
    try:
        resp = requests.post(RPC_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json().get('result', {}).get('value', [])
    except Exception as e:
        print(f"RPC Error: {e}")
    return []

# Get SOL balance
def get_sol_balance(wallet_address):
    """Get native SOL balance"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }
    
    try:
        resp = requests.post(RPC_URL, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            lamports = resp.json().get('result', {}).get('value', 0)
            return lamports / 1e9
    except Exception as e:
        print(f"Balance Error: {e}")
    return 0

# Get token prices from Jupiter
def get_jupiter_price(token_address):
    """Get token price in SOL from Jupiter"""
    try:
        url = f"https://quote-api.jup.ag/v6/quote"
        params = {
            "inputMint": token_address,
            "outputMint": SOL_MINT,
            "amount": "1000000",  # 1 token (assuming 6 decimals)
            "slippageBps": "100"
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Convert output to SOL value per token
            out_amount = float(data.get('outAmount', 0)) / 1e9  # SOL output
            in_amount = float(data.get('inAmount', 0)) / 1e6     # Tokens input
            price_per_token = out_amount / in_amount if in_amount > 0 else 0
            return price_per_token
    except Exception as e:
        print(f"  Price fetch error: {e}")
    return 0

# Main check
print("\n💰 FETCHING SOL BALANCE...")
sol_balance = get_sol_balance(WALLET)
print(f"   SOL Balance: {sol_balance:.6f} SOL\n")

print("🔍 FETCHING TOKEN ACCOUNTS...")
token_accounts = get_token_accounts(WALLET)
print(f"   Found {len(token_accounts)} token accounts\n")

# Match positions to token accounts
total_entry = 0
total_current = 0

for pos in positions:
    address = pos['tokenAddress']
    entry_sol = float(pos['inputSol'])
    trade_num = pos['tradeNum']
    
    print(f"🎯 Trade #{trade_num}: {pos['token']}")
    print(f"   Address: {address[:20]}...{address[-8:]}")
    print(f"   Entry: {entry_sol:.4f} SOL")
    total_entry += entry_sol
    
    # Find matching token account
    matching_account = None
    for account in token_accounts:
        parsed = account.get('account', {}).get('data', {}).get('parsed', {})
        info = parsed.get('info', {})
        mint = info.get('mint', '')
        if mint == address:
            matching_account = account
            break
    
    if matching_account:
        parsed = matching_account['account']['data']['parsed']
        info = parsed['info']
        token_balance = float(info.get('tokenAmount', {}).get('uiAmount', 0))
        decimals = info.get('tokenAmount', {}).get('decimals', 0)
        
        print(f"   Token Balance: {token_balance:,.4f}")
        
        # Get current price
        price_per_token_sol = get_jupiter_price(address)
        
        if price_per_token_sol > 0:
            current_value_sol = token_balance * price_per_token_sol
            pnl_sol = current_value_sol - entry_sol
            pnl_pct = (pnl_sol / entry_sol) * 100 if entry_sol > 0 else 0
            
            total_current += current_value_sol
            
            print(f"   Price: {price_per_token_sol:.10f} SOL/token")
            print(f"   Current Value: {current_value_sol:.6f} SOL")
            print(f"   P&L: {pnl_sol:+.6f} SOL ({pnl_pct:+.2f}%)")
            
            # Exit signals
            tp_target = entry_sol * 1.15
            sl_limit = entry_sol * 0.93
            
            if current_value_sol >= tp_target:
                print(f"   🟢🟢 TAKE PROFIT! Sell for +15%")
            elif current_value_sol <= sl_limit:
                print(f"   🔴🔴 STOP LOSS! Sell at -7%")
            else:
                progress = (current_value_sol - entry_sol) / (tp_target - entry_sol) * 100
                print(f"   🟡 HOLDING - {progress:.0f}% to TP")
        else:
            print(f"   ⚠️ Could not get price")
            total_current += entry_sol  # Assume no change
    else:
        print(f"   ⚠️ Token not found in wallet (may be merged or different mint)")
        total_current += entry_sol  # Assume no change
    
    print()

# Summary
print("=" * 70)
print("📊 PORTFOLIO SUMMARY (LIKE PHANTOM)")
print("=" * 70)
print(f"SOL Balance: {sol_balance:.6f} SOL")
print(f"Total Invested: {total_entry:.4f} SOL")
print(f"Current Value: {total_current:.4f} SOL")

total_pnl = total_current - total_entry
total_pnl_pct = (total_pnl / total_entry) * 100 if total_entry > 0 else 0

print(f"\nTotal P&L: {total_pnl:+.6f} SOL ({total_pnl_pct:+.2f}%)")

# Targets
tp_value = total_entry * 1.15
sl_value = total_entry * 0.93

print(f"\nPortfolio Targets:")
print(f"   Take Profit (+15%): {tp_value:.4f} SOL")
print(f"   Stop Loss (-7%): {sl_value:.4f} SOL")

if total_current >= tp_value:
    print("\n🟢🟢🟢 PORTFOLIO HIT TAKE PROFIT!")
elif total_current <= sl_value:
    print("\n🔴🔴🔴 PORTFOLIO HIT STOP LOSS!")
else:
    pct_to_tp = ((tp_value - total_current) / total_entry) * 100
    print(f"\n🟡 HOLDING - Need {pct_to_tp:.1f}% more to TP")

print("\n" + "=" * 70)
print("💡 NEXT ACTIONS:")
print("=" * 70)
print("1. Check wallet on: https://birdeye.so/profile/8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5")
print("2. Or open Phantom → check token balances")
print("3. Sell any position that hits +15% or drops -7%")
print("=" * 70)
