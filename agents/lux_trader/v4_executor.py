#!/usr/bin/env python3
"""
🚀 V4 API FALLBACK EXECUTOR
Uses Jupiter v4 API which may handle problematic tokens better
"""

import requests
import json
import base64
from typing import Dict, Optional
from datetime import datetime

try:
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

from secure_key_manager import SecureKeyManager

JUPITER_V4_API = "https://quote-api.jup.ag/v4"
SOLANA_RPC = "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84"


class V4Executor:
    """Execute using Jupiter v4 API"""
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.key_manager = SecureKeyManager()
        self.keypair: Optional[Keypair] = None
        
        if SOLANA_AVAILABLE:
            self._load_keypair()
    
    def _load_keypair(self) -> bool:
        """Load keypair from secure storage"""
        private_key = self.key_manager.get_key()
        if not private_key:
            return False
        
        try:
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            return True
        except Exception as e:
            print(f"❌ Error loading keypair: {e}")
            return False
    
    def get_quote_v4(self, input_mint: str, output_mint: str, amount: int) -> Optional[Dict]:
        """Get quote from v4 API"""
        try:
            url = f"{JUPITER_V4_API}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": 1000,  # 10%
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            response = requests.get(url, params=params, timeout=15)
            print(f"   V4 Quote status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   V4 Quote error: {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   V4 Quote exception: {e}")
            return None
    
    def get_swap_v4(self, routes: Dict) -> Optional[Dict]:
        """Get swap transaction from v4 API"""
        try:
            url = f"{JUPITER_V4_API}/swap"
            payload = {
                "route": routes,
                "userPublicKey": str(self.keypair.pubkey()),
                "wrapUnwrapSOL": True,
                "prioritizationFeeLamports": 50000
            }
            
            response = requests.post(url, json=payload, timeout=15)
            print(f"   V4 Swap status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   V4 Swap error: {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   V4 Swap exception: {e}")
            return None
    
    def send_transaction(self, signed_tx_b64: str) -> Optional[str]:
        """Send transaction"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    signed_tx_b64,
                    {
                        "encoding": "base64",
                        "maxRetries": 5,
                        "skipPreflight": True  # Skip preflight for problematic tokens
                    }
                ]
            }
            
            response = requests.post(SOLANA_RPC, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    print(f"   RPC error: {result['error']}")
                    return None
            return None
            
        except Exception as e:
            print(f"   Send error: {e}")
            return None
    
    def execute_sell_v4(self, token_address: str, amount_tokens: float,
                        token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
        """Execute sell using v4 API"""
        print(f"\n🚀 V4 API SELL")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_tokens:.6f}")
        
        if not SOLANA_AVAILABLE or not self.keypair:
            return {"status": "failed", "error": "Not available"}
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        amount_raw = int(amount_tokens * (10 ** token_decimals))
        
        # Get quote
        print("   Step 1: Getting V4 quote...")
        quote = self.get_quote_v4(token_address, SOL_MINT, amount_raw)
        
        if not quote:
            return {"status": "failed", "error": "V4 quote failed"}
        
        # Extract expected output
        out_amount = int(quote.get('outAmount', 0))
        expected_sol = out_amount / 1e9
        print(f"   ✅ Quote: ~{expected_sol:.6f} SOL")
        
        # Get swap transaction
        print("   Step 2: Getting V4 swap transaction...")
        swap_data = self.get_swap_v4(quote)
        
        if not swap_data or 'swapTransaction' not in swap_data:
            return {"status": "failed", "error": "V4 swap transaction failed"}
        
        # Sign and send
        print("   Step 3: Signing...")
        try:
            serialized_tx = swap_data['swapTransaction']
            tx_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            signed_tx = VersionedTransaction(transaction.message, [self.keypair])
            signed_tx_bytes = bytes(signed_tx)
            signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
            
            print("   Step 4: Sending...")
            signature = self.send_transaction(signed_tx_b64)
            
            if signature:
                print(f"\n🎉 V4 SELL SUCCESS!")
                print(f"   Tx: {signature}")
                print(f"   Explorer: https://solscan.io/tx/{signature}")
                
                return {
                    "status": "executed",
                    "transaction_signature": signature,
                    "expected_output_sol": expected_sol,
                    "explorer_url": f"https://solscan.io/tx/{signature}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"status": "failed", "error": "Transaction failed"}
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "error": str(e)}


def execute_sell_v4(wallet: str, token_address: str, amount_tokens: float,
                    token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """Execute sell with v4 API"""
    executor = V4Executor(wallet)
    return executor.execute_sell_v4(token_address, amount_tokens, token_symbol, token_decimals)


if __name__ == "__main__":
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    token = "6TyK5BiBRJPdU4o1naDaNb54kR9nF4wk7nwu6iUFpump"
    
    result = execute_sell_v4(wallet, token, 6366.490642, "PUMP")
    print(f"\nResult: {json.dumps(result, indent=2)}")
