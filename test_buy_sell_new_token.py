#!/usr/bin/env python3
"""
🚀 Buy and Sell Test - New Token
Using OKX DEX API or Jupiter
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import FullAutoExecutor
import requests
import json

# Wallet
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# Token to trade (from scanner)
TOKEN = "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump"
TOKEN_SYMBOL = "pump"  # Short name
BUY_AMOUNT_SOL = 0.001  # Small test amount

def get_token_info():
    """Get token info from DexScreener"""
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{TOKEN}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                pair = data[0]
                return {
                    'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                    'price': pair.get('priceUsd', 'N/A'),
                    'liquidity': pair.get('liquidity', {}).get('usd', 0),
                    'volume': pair.get('volume', {}).get('h24', 0),
                    'dex': pair.get('dexId', 'Unknown')
                }
    except Exception as e:
        print(f"   Error: {e}")
    
    return None

def buy_token():
    """Buy token using FullAutoExecutor"""
    print("="*70)
    print(f"🛒 BUYING {TOKEN_SYMBOL}")
    print("="*70)
    print(f"   Token: {TOKEN}")
    print(f"   Amount: {BUY_AMOUNT_SOL} SOL")
    print(f"   Wallet: {WALLET}")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair loaded")
        return None
    
    try:
        result = executor.buy_token(TOKEN, BUY_AMOUNT_SOL)
        
        if result and result.get('success'):
            print(f"\n✅ BUY SUCCESS!")
            print(f"   TX: {result.get('tx_hash', 'N/A')}")
            print(f"   Amount: {result.get('amount', 'N/A')}")
            return result
        else:
            print(f"\n❌ BUY FAILED")
            print(f"   Error: {result.get('error', 'Unknown')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def sell_token(amount_tokens=None):
    """Sell token using FullAutoExecutor"""
    print("\n" + "="*70)
    print(f"💰 SELLING {TOKEN_SYMBOL}")
    print("="*70)
    print(f"   Token: {TOKEN}")
    
    executor = FullAutoExecutor(WALLET)
    
    if not executor.keypair:
        print("❌ No keypair loaded")
        return None
    
    try:
        # If amount not specified, sell all
        if amount_tokens is None:
            # Get balance first
            balance = executor.get_token_balance(TOKEN)
            if balance == 0:
                print("❌ No tokens to sell")
                return None
            amount_tokens = balance
        
        print(f"   Amount: {amount_tokens} tokens")
        
        result = executor.sell_token(TOKEN, amount_tokens)
        
        if result and result.get('success'):
            print(f"\n✅ SELL SUCCESS!")
            print(f"   TX: {result.get('tx_hash', 'N/A')}")
            print(f"   SOL received: {result.get('sol_received', 'N/A')}")
            return result
        else:
            print(f"\n❌ SELL FAILED")
            print(f"   Error: {result.get('error', 'Unknown')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("\n" + "="*70)
    print("🚀 BUY AND SELL TEST - NEW TOKEN")
    print("="*70)
    
    # Get token info first
    print("\n🔍 Getting token info...")
    info = get_token_info()
    if info:
        print(f"   Symbol: {info['symbol']}")
        print(f"   Price: ${info['price']}")
        print(f"   Liquidity: ${info['liquidity']:,.0f}")
        print(f"   Volume 24h: ${info['volume']:,.0f}")
        print(f"   DEX: {info['dex']}")
    
    # Step 1: Buy
    buy_result = buy_token()
    
    if not buy_result:
        print("\n❌ Buy failed, stopping")
        return
    
    tokens_bought = buy_result.get('amount', 0)
    
    # Step 2: Wait a moment
    print("\n⏳ Waiting 5 seconds before selling...")
    import time
    time.sleep(5)
    
    # Step 3: Sell
    sell_result = sell_token(tokens_bought)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TRADE SUMMARY")
    print("="*70)
    
    if buy_result and sell_result:
        print("✅ FULL CYCLE COMPLETE!")
        print(f"   Token: {TOKEN_SYMBOL}")
        print(f"   Buy TX: {buy_result.get('tx_hash', 'N/A')[:20]}...")
        print(f"   Sell TX: {sell_result.get('tx_hash', 'N/A')[:20]}...")
        print(f"   Amount: {tokens_bought} tokens")
        
        # Calculate P&L
        sol_spent = BUY_AMOUNT_SOL
        sol_received = sell_result.get('sol_received', 0)
        pnl = sol_received - sol_spent
        pnl_pct = (pnl / sol_spent) * 100 if sol_spent > 0 else 0
        
        print(f"   SOL spent: {sol_spent:.6f}")
        print(f"   SOL received: {sol_received:.6f}")
        print(f"   P&L: {pnl:.6f} SOL ({pnl_pct:+.2f}%)")
    elif buy_result:
        print("⚠️ Buy succeeded but sell failed")
        print(f"   You now hold {tokens_bought} {TOKEN_SYMBOL}")
        print(f"   Buy TX: {buy_result.get('tx_hash', 'N/A')}")
    else:
        print("❌ Both buy and sell failed")

if __name__ == "__main__":
    main()
