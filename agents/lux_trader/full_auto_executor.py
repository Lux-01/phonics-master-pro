#!/usr/bin/env python3
"""
🚀 FULL AUTO JUPITER EXECUTOR
Signs and sends transactions automatically for full auto-execution

⚠️  WARNING: This requires private key storage
⚠️  Only use after extensive testing
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
    print("   Install with: pip install solders base58")

from secure_key_manager import SecureKeyManager

JUPITER_API = "https://lite-api.jup.ag/swap/v1"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

class FullAutoExecutor:
    """Execute swaps automatically with private key signing"""
    
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
            print("❌ No private key found. Key should be in:")
            print(f"   {self.key_manager.key_file}")
            return False
        
        try:
            # Convert base58 private key to keypair
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            print(f"✅ Keypair loaded successfully")
            print(f"   Public key: {self.keypair.pubkey()}")
            return True
        except Exception as e:
            print(f"❌ Error loading keypair: {e}")
            return False
    
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
                    {"encoding": "base64", "maxRetries": 3}
                ]
            }
            
            response = requests.post(SOLANA_RPC, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    print(f"❌ RPC error: {result['error']}")
                    return None
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ RPC request error: {e}")
            return None
    
    def sign_and_send_transaction(self, swap_response: Dict) -> Optional[str]:
        """
        Sign and send transaction to Solana
        Returns transaction signature or None
        """
        if not SOLANA_AVAILABLE:
            print("❌ Cannot sign: Solana libraries not available")
            return None
        
        if not self.keypair:
            print("❌ Cannot sign: No keypair loaded")
            return None
        
        try:
            # Get serialized transaction from Jupiter
            serialized_tx = swap_response.get('swapTransaction')
            if not serialized_tx:
                print("❌ No transaction in swap response")
                return None
            
            print("   Step 3: Deserializing transaction...")
            # Deserialize the transaction
            tx_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            print("   Step 4: Signing transaction...")
            # Sign the transaction
            signed_tx = VersionedTransaction(transaction.message, [self.keypair])
            
            print("   Step 5: Sending to Solana...")
            # Serialize signed transaction
            signed_tx_bytes = bytes(signed_tx)
            signed_tx_b64 = base64.b64encode(signed_tx_bytes).decode('utf-8')
            
            # Send via RPC
            signature = self.send_transaction_rpc(signed_tx_b64)
            
            if signature:
                print(f"   ✅ Transaction sent: {signature}")
                return signature
            else:
                print("❌ Failed to send transaction")
                return None
                
        except Exception as e:
            print(f"❌ Transaction signing/sending error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute_buy_full_auto(self, token_address: str, amount_sol: float, 
                               token_symbol: str = "UNKNOWN") -> Dict:
        """
        FULL AUTO: Execute buy order automatically
        
        ⚠️  Requires:
        - Private key stored securely
        - Solana libraries installed
        - Extensive testing completed
        """
        
        print(f"\n🚀 FULL AUTO BUY EXECUTION")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_sol:.6f} SOL")
        print(f"   Time: {datetime.now().isoformat()}")
        
        # Check prerequisites
        if not SOLANA_AVAILABLE:
            return {
                "status": "manual_required",
                "message": "Solana libraries not installed. Run: pip install solders base58",
                "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}",
                "timestamp": datetime.now().isoformat()
            }
        
        if not self.keypair:
            return {
                "status": "manual_required",
                "message": "No private key available",
                "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}",
                "timestamp": datetime.now().isoformat()
            }
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        amount_lamports = int(amount_sol * 1e9)
        
        # Step 1: Get quote
        print("   Step 1: Getting Jupiter quote...")
        quote = self.get_quote(SOL_MINT, token_address, amount_lamports)
        
        if not quote:
            return {
                "status": "failed",
                "error": "Could not get quote",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract expected output
        out_amount = int(quote.get('outAmount', 0))
        decimals = 9 if out_amount > 1e12 else 6
        expected_out = out_amount / (10 ** decimals)
        price_impact = quote.get('priceImpactPct', '0')
        
        print(f"   ✅ Quote: ~{expected_out:.6f} tokens")
        print(f"   Price impact: {price_impact}%")
        
        # Safety check: price impact
        if float(price_impact) > 5.0:
            print(f"   ⚠️  HIGH PRICE IMPACT: {price_impact}%")
            print("   Trade blocked for safety")
            return {
                "status": "blocked",
                "error": f"Price impact too high: {price_impact}%",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Get swap transaction
        print("   Step 2: Building transaction...")
        swap_tx = self.get_swap_transaction(quote, str(self.keypair.pubkey()))
        
        if not swap_tx:
            return {
                "status": "failed",
                "error": "Could not build transaction",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 3: Sign and send
        tx_signature = self.sign_and_send_transaction(swap_tx)
        
        if tx_signature:
            print(f"\n🎉 TRADE EXECUTED SUCCESSFULLY!")
            print(f"   Transaction: {tx_signature}")
            print(f"   View: https://solscan.io/tx/{tx_signature}")
            
            return {
                "status": "executed",
                "transaction_signature": tx_signature,
                "expected_output": expected_out,
                "price_impact": price_impact,
                "timestamp": datetime.now().isoformat(),
                "explorer_url": f"https://solscan.io/tx/{tx_signature}"
            }
        else:
            print("\n❌ Auto-execution failed")
            print("   Falling back to manual execution")
            return {
                "status": "manual_required",
                "message": "Auto-signing failed, use manual execution",
                "manual_url": f"https://jup.ag/swap/SOL-{token_address}?amount={amount_sol}",
                "quote": quote,
                "expected_output": expected_out,
                "price_impact": price_impact,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_sell_full_auto(self, token_address: str, token_symbol: str, 
                                amount_tokens: float, token_decimals: int = 9) -> Dict:
        """
        FULL AUTO: Execute sell order (token -> SOL)
        
        Args:
            token_address: Token mint address
            token_symbol: Token symbol for display
            amount_tokens: Amount of tokens to sell
            token_decimals: Token decimals (default 9)
        
        Returns:
            Dict with execution result
        """
        
        print(f"\n🚀 FULL AUTO SELL EXECUTION")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_tokens:.6f} tokens")
        print(f"   Time: {datetime.now().isoformat()}")
        
        # Check prerequisites
        if not SOLANA_AVAILABLE:
            return {
                "status": "manual_required",
                "message": "Solana libraries not installed. Run: pip install solders base58",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL",
                "timestamp": datetime.now().isoformat()
            }
        
        if not self.keypair:
            return {
                "status": "manual_required",
                "message": "No private key available",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL",
                "timestamp": datetime.now().isoformat()
            }
        
        SOL_MINT = "So11111111111111111111111111111111111111112"
        
        # Convert token amount to raw amount (with decimals)
        amount_raw = int(amount_tokens * (10 ** token_decimals))
        
        # Step 1: Get quote (token -> SOL)
        print("   Step 1: Getting Jupiter quote...")
        quote = self.get_quote(token_address, SOL_MINT, amount_raw)
        
        if not quote:
            return {
                "status": "failed",
                "error": "Could not get quote",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract expected output
        out_amount = int(quote.get('outAmount', 0))
        expected_out_sol = out_amount / 1e9  # SOL has 9 decimals
        price_impact = quote.get('priceImpactPct', '0')
        
        print(f"   ✅ Quote: ~{expected_out_sol:.6f} SOL")
        print(f"   Price impact: {price_impact}%")
        
        # Safety check: price impact
        if float(price_impact) > 5.0:
            print(f"   ⚠️  HIGH PRICE IMPACT: {price_impact}%")
            print("   Trade blocked for safety")
            return {
                "status": "blocked",
                "error": f"Price impact too high: {price_impact}%",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Get swap transaction
        print("   Step 2: Building transaction...")
        swap_tx = self.get_swap_transaction(quote, str(self.keypair.pubkey()))
        
        if not swap_tx:
            return {
                "status": "failed",
                "error": "Could not build transaction",
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 3: Sign and send
        tx_signature = self.sign_and_send_transaction(swap_tx)
        
        if tx_signature:
            print(f"\n🎉 SELL EXECUTED SUCCESSFULLY!")
            print(f"   Transaction: {tx_signature}")
            print(f"   View: https://solscan.io/tx/{tx_signature}")
            
            return {
                "status": "executed",
                "transaction_signature": tx_signature,
                "expected_output_sol": expected_out_sol,
                "price_impact": price_impact,
                "timestamp": datetime.now().isoformat(),
                "explorer_url": f"https://solscan.io/tx/{tx_signature}"
            }
        else:
            print("\n❌ Auto-execution failed")
            print("   Falling back to manual execution")
            return {
                "status": "manual_required",
                "message": "Auto-signing failed, use manual execution",
                "manual_url": f"https://jup.ag/swap/{token_address}-SOL",
                "quote": quote,
                "expected_output_sol": expected_out_sol,
                "price_impact": price_impact,
                "timestamp": datetime.now().isoformat()
            }


# Convenience functions for LuxTrader
def execute_buy_auto(wallet: str, token_address: str, amount_sol: float, 
                     token_symbol: str = "UNKNOWN") -> Dict:
    """Execute buy with full auto capability"""
    executor = FullAutoExecutor(wallet)
    return executor.execute_buy_full_auto(token_address, amount_sol, token_symbol)


def execute_sell_auto(wallet: str, token_address: str, amount_tokens: float,
                      token_symbol: str = "UNKNOWN") -> Dict:
    """Execute sell with full auto capability"""
    executor = FullAutoExecutor(wallet)
    return executor.execute_sell_full_auto(token_address, token_symbol, amount_tokens)


if __name__ == "__main__":
    # Test
    print("Full Auto Executor Test")
    print("="*60)
    
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    
    result = execute_buy_auto(wallet, test_token, 0.001, "USDC")
    print(f"\nResult: {json.dumps(result, indent=2)}")
