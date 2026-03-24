#!/usr/bin/env python3
"""
🚀 ADVANCED SELL EXECUTOR
Multiple strategies to handle problematic tokens (pump.fun, restricted, etc.)

Error 0x1788 (6024) Solutions:
1. Skip preflight simulation
2. Use Helius RPC (private, less restrictive)
3. Increase slippage significantly
4. Use exactOut mode
5. Ensure ATA exists before swap
6. Use priority fees
7. Try multiple DEX aggregators
"""

import requests
import json
import base64
import time
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

# Multiple RPC endpoints to try
RPC_ENDPOINTS = [
    "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84",  # Helius
    "https://api.mainnet-beta.solana.com",  # Public
]

JUPITER_API = "https://lite-api.jup.ag/swap/v1"


class AdvancedSellExecutor:
    """Advanced executor with multiple fallback strategies"""
    
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
            return False
        
        try:
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            return True
        except Exception as e:
            print(f"❌ Error loading keypair: {e}")
            return False
    
    def get_quote(self, input_mint: str, output_mint: str, amount: int, 
                  slippage_bps: int = 500, exact_out: bool = False) -> Optional[Dict]:
        """Get quote with higher slippage tolerance"""
        try:
            url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            if exact_out:
                params["swapMode"] = "ExactOut"
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Quote failed: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   Quote error: {e}")
            return None
    
    def get_swap_transaction(self, quote: Dict, user_public_key: str, 
                             wrap_unwrap: bool = True) -> Optional[Dict]:
        """Get swap transaction"""
        try:
            url = f"{JUPITER_API}/swap"
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSOL": wrap_unwrap,
                "prioritizationFeeLamports": 50000,  # Higher priority fee
                "computeUnitPriceMicroLamports": 50000
            }
            
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Swap tx failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   Swap tx error: {e}")
            return None
    
    def send_transaction_rpc(self, signed_tx_b64: str, rpc_url: str,
                             skip_preflight: bool = False) -> Optional[str]:
        """Send transaction with optional preflight skip"""
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
                        "skipPreflight": skip_preflight,
                        "preflightCommitment": "confirmed"
                    }
                ]
            }
            
            response = requests.post(rpc_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    print(f"   RPC error: {result['error']}")
                    return None
            else:
                print(f"   HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   RPC request error: {e}")
            return None
    
    def execute_sell_advanced(self, token_address: str, amount_tokens: float,
                               token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
        """
        Execute sell with multiple fallback strategies
        """
        print(f"\n🚀 ADVANCED SELL EXECUTOR")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_tokens:.6f} tokens")
        
        if not SOLANA_AVAILABLE or not self.keypair:
            return {
                "status": "failed",
                "error": "Solana libraries not available"
            }
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        amount_raw = int(amount_tokens * (10 ** token_decimals))
        
        # Strategy 1: Standard with higher slippage (5%)
        print("\n📍 Strategy 1: High slippage (5%)")
        result = self._try_sell(token_address, SOL_MINT, amount_raw, 
                                slippage_bps=500, rpc_index=0)
        if result and result.get("status") == "executed":
            return result
        
        # Strategy 2: Skip preflight with Helius
        print("\n📍 Strategy 2: Skip preflight + Helius RPC")
        result = self._try_sell(token_address, SOL_MINT, amount_raw,
                                slippage_bps=500, rpc_index=0, skip_preflight=True)
        if result and result.get("status") == "executed":
            return result
        
        # Strategy 3: Very high slippage (10%)
        print("\n📍 Strategy 3: Very high slippage (10%)")
        result = self._try_sell(token_address, SOL_MINT, amount_raw,
                                slippage_bps=1000, rpc_index=0, skip_preflight=True)
        if result and result.get("status") == "executed":
            return result
        
        # Strategy 4: Public RPC with skip preflight
        print("\n📍 Strategy 4: Public RPC + skip preflight")
        result = self._try_sell(token_address, SOL_MINT, amount_raw,
                                slippage_bps=1000, rpc_index=1, skip_preflight=True)
        if result and result.get("status") == "executed":
            return result
        
        # All strategies failed
        return {
            "status": "failed",
            "error": "All advanced sell strategies failed"
        }
    
    def _try_sell(self, input_mint: str, output_mint: str, amount: int,
                  slippage_bps: int, rpc_index: int, skip_preflight: bool = False) -> Optional[Dict]:
        """Try a single sell strategy"""
        try:
            # Get quote
            print(f"   Getting quote (slippage: {slippage_bps/100}%)...")
            quote = self.get_quote(input_mint, output_mint, amount, slippage_bps)
            
            if not quote:
                print(f"   ❌ Quote failed")
                return None
            
            out_amount = int(quote.get('outAmount', 0))
            expected_sol = out_amount / 1e9
            print(f"   ✅ Quote: ~{expected_sol:.6f} SOL")
            
            # Get swap transaction
            print(f"   Building transaction...")
            swap_tx = self.get_swap_transaction(quote, str(self.keypair.pubkey()))
            
            if not swap_tx or 'swapTransaction' not in swap_tx:
                print(f"   ❌ No swap transaction")
                return None
            
            # Deserialize and sign
            serialized_tx = swap_tx['swapTransaction']
            tx_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            signed_tx = VersionedTransaction(transaction.message, [self.keypair])
            signed_tx_bytes = bytes(signed_tx)
            signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
            
            # Send with selected RPC
            rpc_url = RPC_ENDPOINTS[rpc_index % len(RPC_ENDPOINTS)]
            print(f"   Sending via RPC {rpc_index + 1} (skip_preflight={skip_preflight})...")
            
            signature = self.send_transaction_rpc(signed_tx_b64, rpc_url, skip_preflight)
            
            if signature:
                print(f"\n🎉 SELL SUCCESS!")
                print(f"   Transaction: {signature}")
                print(f"   Explorer: https://solscan.io/tx/{signature}")
                
                return {
                    "status": "executed",
                    "transaction_signature": signature,
                    "expected_output_sol": expected_sol,
                    "explorer_url": f"https://solscan.io/tx/{signature}",
                    "timestamp": datetime.now().isoformat(),
                    "strategy": f"slippage_{slippage_bps}_rpc_{rpc_index}_skip_{skip_preflight}"
                }
            else:
                print(f"   ❌ Transaction failed")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None


# Convenience function
def execute_sell_advanced(wallet: str, token_address: str, amount_tokens: float,
                          token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """Execute sell with advanced strategies"""
    executor = AdvancedSellExecutor(wallet)
    return executor.execute_sell_advanced(token_address, amount_tokens, token_symbol, token_decimals)


if __name__ == "__main__":
    print("Advanced Sell Executor Test")
    print("="*60)
    
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    test_token = "6TyK5BiBRJPdU4o1naDaNb54kR9nF4wk7nwu6iUFpump"
    
    result = execute_sell_advanced(wallet, test_token, 6366.490642, "PUMP")
    print(f"\nResult: {json.dumps(result, indent=2)}")
