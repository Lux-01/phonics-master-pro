#!/usr/bin/env python3
"""
🔧 JUPITER SWAP EXECUTOR
Handles actual blockchain transactions for LuxTrader and Holy Trinity
"""

import requests
import json
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime

JUPITER_API = "https://lite-api.jup.ag/swap/v1"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

class JupiterExecutor:
    """Execute swaps via Jupiter API"""
    
    def __init__(self, wallet_address: str, private_key: Optional[str] = None):
        self.wallet = wallet_address
        self.private_key = private_key
        self.session = requests.Session()
    
    def get_quote(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = 250) -> Optional[Dict]:
        """Get swap quote from Jupiter"""
        try:
            url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Quote failed: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Quote error: {e}")
            return None
    
    def get_swap_transaction(self, quote: Dict, user_public_key: str) -> Optional[Dict]:
        """Get swap transaction from Jupiter"""
        try:
            url = f"{JUPITER_API}/swap"
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSOL": True,
                "prioritizationFeeLamports": 10000  # 0.00001 SOL priority fee
            }
            
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Swap transaction failed: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Swap transaction error: {e}")
            return None
    
    def execute_swap(self, input_mint: str, output_mint: str, amount_sol: float, 
                     token_symbol: str = "UNKNOWN") -> Dict:
        """
        Execute a swap transaction
        Returns: Dict with transaction details
        """
        
        print(f"\n🚀 EXECUTING LIVE SWAP")
        print(f"   From: {amount_sol:.6f} SOL")
        print(f"   To: {token_symbol}")
        print(f"   Wallet: {self.wallet[:20]}...")
        
        # Convert SOL to lamports
        amount_lamports = int(amount_sol * 1e9)
        
        # Step 1: Get quote
        print("   Step 1: Getting quote...")
        quote = self.get_quote(input_mint, output_mint, amount_lamports)
        
        if not quote:
            return {
                "status": "failed",
                "error": "Could not get quote",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract expected output
        out_amount = int(quote.get('outAmount', 0))
        # Estimate decimals (most tokens are 6 or 9)
        decimals = 9 if out_amount > 1e12 else 6
        expected_out = out_amount / (10 ** decimals)
        price_impact = quote.get('priceImpactPct', '0')
        
        print(f"   ✅ Quote: ~{expected_out:.6f} tokens")
        print(f"   Price impact: {price_impact}%")
        
        # Step 2: Get swap transaction
        print("   Step 2: Building transaction...")
        swap_tx = self.get_swap_transaction(quote, self.wallet)
        
        if not swap_tx:
            return {
                "status": "failed",
                "error": "Could not build swap transaction",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 3: Sign and send (requires private key)
        if not self.private_key:
            print("   ⚠️ No private key configured - cannot sign transaction")
            print("   Transaction ready but needs manual signing")
            
            # Return transaction for manual signing
            return {
                "status": "ready_for_signing",
                "transaction": swap_tx.get('swapTransaction'),
                "quote": quote,
                "expected_output": expected_out,
                "price_impact": price_impact,
                "timestamp": datetime.now().isoformat(),
                "manual_url": f"https://jup.ag/swap/SOL-{output_mint}?amount={amount_sol}"
            }
        
        # If we have private key, sign and send
        print("   Step 3: Signing transaction...")
        # This would require solana-py library and proper key handling
        # For security, we'll skip auto-signing and require manual execution
        
        return {
            "status": "manual_required",
            "message": "Transaction prepared. Sign manually for security.",
            "manual_url": f"https://jup.ag/swap/SOL-{output_mint}?amount={amount_sol}",
            "expected_output": expected_out,
            "price_impact": price_impact,
            "timestamp": datetime.now().isoformat()
        }
    
    def sell_token(self, token_mint: str, token_symbol: str, amount_tokens: float) -> Dict:
        """Sell tokens back to SOL"""
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        
        print(f"\n🚀 EXECUTING LIVE SELL")
        print(f"   From: {amount_tokens:.6f} {token_symbol}")
        print(f"   To: SOL")
        
        # Note: Need token balance and decimals - this is simplified
        # In real implementation, need to:
        # 1. Get token account
        # 2. Check balance
        # 3. Get decimals
        # 4. Execute swap
        
        return {
            "status": "manual_required",
            "message": "Sell requires token balance check. Use Jupiter directly.",
            "manual_url": f"https://jup.ag/swap/{token_mint}-SOL",
            "timestamp": datetime.now().isoformat()
        }


# Convenience function for LuxTrader
def execute_buy(wallet: str, token_address: str, amount_sol: float, token_symbol: str = "UNKNOWN") -> Dict:
    """Execute a buy order"""
    SOL_MINT = "So11111111111111111111111111111111111111112"
    
    executor = JupiterExecutor(wallet)
    return executor.execute_swap(SOL_MINT, token_address, amount_sol, token_symbol)


def execute_sell(wallet: str, token_address: str, amount_tokens: float, token_symbol: str = "UNKNOWN") -> Dict:
    """Execute a sell order"""
    executor = JupiterExecutor(wallet)
    return executor.sell_token(token_address, token_symbol, amount_tokens)


if __name__ == "__main__":
    # Test
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    
    print("Testing Jupiter Executor...")
    result = execute_buy(wallet, test_token, 0.001, "USDC")
    print(f"\nResult: {json.dumps(result, indent=2)}")
