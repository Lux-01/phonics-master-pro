#!/usr/bin/env python3
"""
🚀 ULTRA API EXECUTOR
Uses Jupiter Ultra API for more reliable execution

Ultra API Flow:
1. GET /ultra/v1/order - Returns quote + transaction together
2. Sign and send transaction

Benefits:
- Simpler 2-step process
- Better transaction landing
- MEV protection
"""

import requests
import json
import base64
import time
from typing import Dict, Optional
from datetime import datetime

# Try to import Solana libraries
try:
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    import base58
    SOLANA_AVAILABLE = True
except ImportError as e:
    SOLANA_AVAILABLE = False
    print(f"⚠️  Solana libraries not available: {e}")

from secure_key_manager import SecureKeyManager

# Jupiter Ultra API
ULTRA_API = "https://lite-api.jup.ag/ultra/v1"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"


class UltraExecutor:
    """Execute swaps using Jupiter Ultra API"""
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.key_manager = SecureKeyManager()
        self.keypair: Optional[Keypair] = None
        self.session = requests.Session()
        
        if SOLANA_AVAILABLE:
            self._load_keypair()
    
    def _load_keypair(self) -> bool:
        """Load keypair from secure storage"""
        private_key = self.key_manager.get_key()
        if not private_key:
            print("❌ No private key found")
            return False
        
        try:
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            print(f"✅ Keypair loaded: {self.keypair.pubkey()}")
            return True
        except Exception as e:
            print(f"❌ Error loading keypair: {e}")
            return False
    
    def get_order(self, input_mint: str, output_mint: str, amount: str, 
                  slippage_bps: int = 250) -> Optional[Dict]:
        """
        Get order from Ultra API
        Returns quote + transaction in one call
        """
        try:
            url = f"{ULTRA_API}/order"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": slippage_bps,
                "taker": self.wallet
            }
            
            print(f"   Calling Ultra API: {url}")
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Ultra order received")
                print(f"      Input: {data.get('inAmount')} | Output: {data.get('outAmount')}")
                print(f"      Price Impact: {data.get('priceImpactPct', 'N/A')}%")
                return data
            else:
                print(f"   ❌ Ultra order failed: {response.status_code}")
                print(f"      {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Ultra order error: {e}")
            return None
    
    def send_transaction_rpc(self, signed_tx_b64: str) -> Optional[str]:
        """Send signed transaction via Solana RPC"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    signed_tx_b64,
                    {"encoding": "base64", "maxRetries": 3, "skipPreflight": False}
                ]
            }
            
            response = requests.post(SOLANA_RPC, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    print(f"   ❌ RPC error: {result['error']}")
                    return None
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ RPC request error: {e}")
            return None
    
    def execute_buy_ultra(self, token_address: str, amount_sol: float, 
                          token_symbol: str = "UNKNOWN") -> Dict:
        """
        Execute buy using Ultra API
        """
        print(f"\n🚀 ULTRA API BUY")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_sol:.6f} SOL")
        
        if not SOLANA_AVAILABLE:
            return {
                "status": "manual_required",
                "message": "Solana libraries not installed",
                "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}"
            }
        
        if not self.keypair:
            return {
                "status": "manual_required",
                "message": "No private key available",
                "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}"
            }
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        amount_lamports = int(amount_sol * 1e9)
        
        # Step 1: Get Ultra order (quote + transaction)
        print("   Step 1: Getting Ultra order...")
        order = self.get_order(SOL_MINT, token_address, str(amount_lamports))
        
        if not order:
            return {
                "status": "failed",
                "error": "Could not get Ultra order"
            }
        
        # Extract transaction
        serialized_tx = order.get('transaction')
        if not serialized_tx:
            print(f"   ⚠️ No transaction field in order response")
            print(f"   Response keys: {list(order.keys())}")
            return {
                "status": "manual_required",
                "message": "Ultra API did not return transaction, use manual execution",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL",
                "order": order
            }
        
        # Extract expected output
        out_amount = int(order.get('outAmount', 0))
        decimals = 9 if out_amount > 1e12 else 6
        expected_out = out_amount / (10 ** decimals)
        
        print(f"   Step 2: Signing transaction...")
        
        try:
            # Deserialize transaction
            tx_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            # Sign transaction
            signed_tx = VersionedTransaction(transaction.message, [self.keypair])
            signed_tx_bytes = bytes(signed_tx)
            signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
            
            print(f"   Step 3: Sending to Solana...")
            signature = self.send_transaction_rpc(signed_tx_b64)
            
            if signature:
                print(f"\n🎉 ULTRA BUY SUCCESS!")
                print(f"   Transaction: {signature}")
                print(f"   Explorer: https://solscan.io/tx/{signature}")
                
                return {
                    "status": "executed",
                    "transaction_signature": signature,
                    "expected_output": expected_out,
                    "price_impact": order.get('priceImpactPct', '0'),
                    "explorer_url": f"https://solscan.io/tx/{signature}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"\n❌ Transaction failed")
                return {
                    "status": "manual_required",
                    "message": "Transaction failed, use manual execution",
                    "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}"
                }
                
        except Exception as e:
            print(f"   ❌ Signing error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def execute_sell_ultra(self, token_address: str, amount_tokens: float,
                            token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
        """
        Execute sell using Ultra API
        """
        print(f"\n🚀 ULTRA API SELL")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_tokens:.6f} tokens")
        
        if not SOLANA_AVAILABLE or not self.keypair:
            return {
                "status": "manual_required",
                "message": "Cannot execute sell",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL"
            }
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        amount_raw = int(amount_tokens * (10 ** token_decimals))
        
        # Get Ultra order
        print("   Step 1: Getting Ultra order...")
        order = self.get_order(token_address, SOL_MINT, str(amount_raw))
        
        if not order:
            return {
                "status": "failed",
                "error": "Could not get Ultra order"
            }
        
        serialized_tx = order.get('transaction')
        if not serialized_tx:
            return {
                "status": "failed",
                "error": "No transaction in order"
            }
        
        # Extract expected SOL output
        out_amount = int(order.get('outAmount', 0))
        expected_out_sol = out_amount / 1e9
        
        print(f"   Step 2: Signing transaction...")
        
        try:
            # Sign and send
            tx_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            signed_tx = VersionedTransaction(transaction.message, [self.keypair])
            signed_tx_bytes = bytes(signed_tx)
            signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
            
            print(f"   Step 3: Sending to Solana...")
            signature = self.send_transaction_rpc(signed_tx_b64)
            
            if signature:
                print(f"\n🎉 ULTRA SELL SUCCESS!")
                print(f"   Transaction: {signature}")
                print(f"   Explorer: https://solscan.io/tx/{signature}")
                
                return {
                    "status": "executed",
                    "transaction_signature": signature,
                    "expected_output_sol": expected_out_sol,
                    "explorer_url": f"https://solscan.io/tx/{signature}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "manual_required",
                    "message": "Transaction failed",
                    "manual_url": f"https://jup.ag/swap/{token_address}-SOL"
                }
                
        except Exception as e:
            print(f"   ❌ Signing error: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


# Convenience functions
def execute_buy_ultra(wallet: str, token_address: str, amount_sol: float, 
                      token_symbol: str = "UNKNOWN") -> Dict:
    """Execute buy with Ultra API"""
    executor = UltraExecutor(wallet)
    return executor.execute_buy_ultra(token_address, amount_sol, token_symbol)


def execute_sell_ultra(wallet: str, token_address: str, amount_tokens: float,
                       token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """Execute sell with Ultra API"""
    executor = UltraExecutor(wallet)
    return executor.execute_sell_ultra(token_address, amount_tokens, token_symbol, token_decimals)


if __name__ == "__main__":
    print("Ultra API Executor Test")
    print("="*60)
    
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    
    result = execute_buy_ultra(wallet, test_token, 0.001, "USDC")
    print(f"\nResult: {json.dumps(result, indent=2)}")
