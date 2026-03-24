#!/usr/bin/env python3
"""
🚀 FULL AUTO JUPITER EXECUTOR v2.0
Following exact procedure with validation and retry logic

Procedure:
1. Determine input amount
2. Fetch fresh quote
3. Validate quote (price impact, outAmount, route hops)
4. Build swap transaction
5. Sign and send
6. Retry up to 3 times on failure
7. Log everything
"""

import requests
import json
import base64
import time
from typing import Dict, Optional, Tuple
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

# Jupiter API (using NEW endpoint - lite-api)
JUPITER_QUOTE_API = "https://lite-api.jup.ag/swap/v1/quote"
JUPITER_SWAP_API = "https://lite-api.jup.ag/swap/v1/swap"
SOLANA_RPC = "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84"

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
MAX_RETRIES = 3
MAX_ROUTE_HOPS = 4
MAX_PRICE_IMPACT_PCT = 5.0  # 5%


class FullAutoExecutorV2:
    """Execute swaps with full validation and retry logic"""
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.key_manager = SecureKeyManager()
        self.keypair: Optional[Keypair] = None
        self.session = requests.Session()
        self.trade_log = []
        
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
    
    def _log_trade(self, log_entry: Dict):
        """Log trade details"""
        log_entry['timestamp'] = datetime.now().isoformat()
        self.trade_log.append(log_entry)
        print(f"\n📝 TRADE LOG:")
        for key, value in log_entry.items():
            print(f"   {key}: {value}")
    
    def fetch_quote(self, input_mint: str, output_mint: str, amount: int, 
                    slippage_bps: int = 250) -> Optional[Dict]:
        """
        Step 2: Fetch fresh quote from Jupiter
        """
        try:
            print(f"   Fetching quote...")
            print(f"      inputMint: {input_mint[:20]}...")
            print(f"      outputMint: {output_mint[:20]}...")
            print(f"      amount: {amount}")
            print(f"      slippageBps: {slippage_bps}")
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps
            }
            
            response = self.session.get(JUPITER_QUOTE_API, params=params, timeout=15)
            
            if response.status_code == 200:
                quote = response.json()
                print(f"   ✅ Quote received")
                return quote
            else:
                print(f"   ❌ Quote failed: {response.status_code}")
                print(f"      {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Quote error: {e}")
            return None
    
    def validate_quote(self, quote: Dict) -> Tuple[bool, str]:
        """
        Step 3: Validate the quote
        """
        print(f"\n   Validating quote...")
        
        # Check price impact
        price_impact = float(quote.get('priceImpactPct', 0))
        print(f"      Price impact: {price_impact}%")
        
        if price_impact > MAX_PRICE_IMPACT_PCT:
            return False, f"Price impact too high: {price_impact}% > {MAX_PRICE_IMPACT_PCT}%"
        
        # Check outAmount
        out_amount = int(quote.get('outAmount', 0))
        print(f"      Out amount: {out_amount}")
        
        if out_amount == 0:
            return False, "Out amount is zero"
        
        # Check route hops
        route_plan = quote.get('routePlan', [])
        num_hops = len(route_plan)
        print(f"      Route hops: {num_hops}")
        
        if num_hops > MAX_ROUTE_HOPS:
            return False, f"Too many hops: {num_hops} > {MAX_ROUTE_HOPS}"
        
        print(f"   ✅ Quote valid")
        return True, "OK"
    
    def build_swap_transaction(self, quote: Dict) -> Optional[Dict]:
        """
        Step 4: Build the swap transaction
        """
        try:
            print(f"\n   Building swap transaction...")
            
            payload = {
                "quoteResponse": quote,
                "userPublicKey": str(self.keypair.pubkey()),
                "wrapAndUnwrapSOL": True,
                "prioritizationFeeLamports": 50000  # 0.00005 SOL
            }
            
            response = self.session.post(JUPITER_SWAP_API, json=payload, timeout=15)
            
            if response.status_code == 200:
                swap_data = response.json()
                print(f"   ✅ Swap transaction built")
                return swap_data
            else:
                print(f"   ❌ Swap build failed: {response.status_code}")
                print(f"      {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Swap build error: {e}")
            return None
    
    def send_transaction(self, signed_tx_b64: str) -> Optional[str]:
        """
        Step 5: Send transaction to Solana
        """
        try:
            print(f"   Sending transaction...")
            
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
                        "skipPreflight": False,
                        "preflightCommitment": "confirmed"
                    }
                ]
            }
            
            response = requests.post(SOLANA_RPC, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print(f"   ✅ Transaction sent: {result['result'][:30]}...")
                    return result["result"]
                elif "error" in result:
                    print(f"   ❌ RPC error: {result['error']}")
                    return None
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Send error: {e}")
            return None
    
    def execute_sell(self, token_address: str, amount_tokens: float,
                     token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
        """
        Execute sell with full procedure and retry logic
        """
        print(f"\n{'='*60}")
        print("🚀 EXECUTING SELL (v2.0)")
        print(f"{'='*60}")
        print(f"Token: {token_symbol}")
        print(f"Amount: {amount_tokens:.6f} tokens")
        
        if not SOLANA_AVAILABLE or not self.keypair:
            return {"status": "failed", "error": "Not available"}
        
        # Step 1: Determine input amount
        input_mint = token_address
        output_mint = SOL_MINT  # Sell for SOL
        amount_raw = int(amount_tokens * (10 ** token_decimals))
        
        print(f"\n📍 Step 1: Input determined")
        print(f"   inputMint: {input_mint}")
        print(f"   outputMint: SOL")
        print(f"   amount: {amount_raw}")
        
        # Try up to MAX_RETRIES
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n{'='*60}")
            print(f"🔄 ATTEMPT {attempt}/{MAX_RETRIES}")
            print(f"{'='*60}")
            
            # Step 2: Fetch quote
            slippage_bps = 250 if attempt == 1 else 500 if attempt == 2 else 1000
            quote = self.fetch_quote(input_mint, output_mint, amount_raw, slippage_bps)
            
            if not quote:
                print(f"   ⚠️ Could not fetch quote, retrying...")
                continue
            
            # Step 3: Validate quote
            is_valid, validation_msg = self.validate_quote(quote)
            
            if not is_valid:
                print(f"   ⚠️ Quote invalid: {validation_msg}")
                if attempt < MAX_RETRIES:
                    print(f"   Retrying with higher slippage...")
                    continue
                else:
                    return {
                        "status": "failed",
                        "error": f"Quote validation failed: {validation_msg}"
                    }
            
            # Step 4: Build swap transaction
            swap_data = self.build_swap_transaction(quote)
            
            if not swap_data or 'swapTransaction' not in swap_data:
                print(f"   ⚠️ Could not build swap transaction")
                continue
            
            # Step 5: Sign and send
            print(f"\n   Signing transaction...")
            try:
                serialized_tx = swap_data['swapTransaction']
                tx_bytes = base64.b64decode(serialized_tx)
                transaction = VersionedTransaction.from_bytes(tx_bytes)
                
                signed_tx = VersionedTransaction(transaction.message, [self.keypair])
                signed_tx_bytes = bytes(signed_tx)
                signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
                
                signature = self.send_transaction(signed_tx_b64)
                
                if signature:
                    # Success!
                    expected_out = int(quote.get('outAmount', 0)) / 1e9
                    
                    print(f"\n🎉 SELL SUCCESS!")
                    print(f"   Transaction: {signature}")
                    print(f"   Explorer: https://solscan.io/tx/{signature}")
                    
                    # Step 7: Log trade
                    self._log_trade({
                        "type": "SELL",
                        "inputMint": input_mint,
                        "outputMint": output_mint,
                        "amountSold": amount_tokens,
                        "amountSoldRaw": amount_raw,
                        "expectedOutAmount": expected_out,
                        "slippageBps": slippage_bps,
                        "priceImpactPct": quote.get('priceImpactPct'),
                        "routeHops": len(quote.get('routePlan', [])),
                        "transactionSignature": signature,
                        "attempt": attempt
                    })
                    
                    return {
                        "status": "executed",
                        "transaction_signature": signature,
                        "expected_output_sol": expected_out,
                        "explorer_url": f"https://solscan.io/tx/{signature}",
                        "timestamp": datetime.now().isoformat(),
                        "attempt": attempt
                    }
                else:
                    # Step 6: Transaction failed, retry
                    print(f"   ⚠️ Transaction failed, will retry...")
                    
            except Exception as e:
                print(f"   ❌ Signing error: {e}")
                import traceback
                traceback.print_exc()
        
        # All retries failed
        print(f"\n{'='*60}")
        print("❌ ALL RETRIES FAILED")
        print(f"{'='*60}")
        
        self._log_trade({
            "type": "SELL_FAILED",
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amountSold": amount_tokens,
            "error": "Max retries exceeded"
        })
        
        return {
            "status": "failed",
            "error": "Max retries exceeded"
        }


# Convenience function
def execute_sell_v2(wallet: str, token_address: str, amount_tokens: float,
                    token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """Execute sell with v2.0 procedure"""
    executor = FullAutoExecutorV2(wallet)
    return executor.execute_sell(token_address, amount_tokens, token_symbol, token_decimals)


if __name__ == "__main__":
    print("Full Auto Executor v2.0 Test")
    print("="*60)
    
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    token = "32CdQdBUxbCsLy5AUHWmyidfwhgGUr9N573NBUrDpump"
    
    result = execute_sell_v2(wallet, token, 35.29, "TEST")
    
    print(f"\nResult: {json.dumps(result, indent=2)}")
